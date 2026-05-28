from __future__ import annotations

import re

import arxiv as arxiv_lib
import wikipedia as wikipedia_pkg
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import ArxivAPIWrapper, WikipediaAPIWrapper

from app.models import ChatResponse
from app.services.llm import invoke_text


class RateLimitFriendlyArxivAPIWrapper(ArxivAPIWrapper):
    def _fetch_results(self, query: str):
        query = query[: self.ARXIV_MAX_QUERY_LENGTH]

        if self.is_arxiv_identifier(query):
            search = arxiv_lib.Search(
                id_list=query.split(),
                max_results=self.top_k_results,
            )
        else:
            search = arxiv_lib.Search(
                query=query,
                max_results=self.top_k_results,
                sort_by=arxiv_lib.SortCriterion.Relevance,
            )

        client = arxiv_lib.Client(
            page_size=self.top_k_results,
            delay_seconds=5.0,
            num_retries=5,
        )
        return list(client.results(search))


wikipedia_pkg.set_user_agent("VisualAgentLocal/1.0 (local development)")

arxiv_tool = ArxivQueryRun(
    api_wrapper=RateLimitFriendlyArxivAPIWrapper(
        top_k_results=3,
        load_max_docs=3,
        doc_content_chars_max=3500,
        continue_on_failure=True,
    ),
    description="Search arXiv papers for a given research topic.",
)

wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=3000),
    description="Search Wikipedia for background context.",
)


RECENT_HINT_RE = re.compile(r"\b(latest|recent|newest|current|mới nhất|gần đây)\b", re.I)


def _clean_research_query(query: str) -> str:
    cleaned = query.strip()
    cleaned = re.sub(r"[?!.]+$", "", cleaned)
    cleaned = re.sub(
        r"(?i)\b(what|which|tell me|give me|provide me|find|search|show)\b",
        " ",
        cleaned,
    )
    cleaned = re.sub(
        r"(?i)\b(is|are|the|a|an|and|on|about|of|for|latest|recent|newest|current|research|papers?|studies|information)\b",
        " ",
        cleaned,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned or query.strip()


def _build_wikipedia_query(query: str) -> str:
    return _clean_research_query(query)


def _topic_variants(topic: str) -> list[str]:
    variants = [topic]
    words = topic.split()

    if words:
        last = words[-1]
        singular = None
        if last.lower().endswith("ies") and len(last) > 4:
            singular = last[:-3] + "y"
        elif last.lower().endswith("s") and len(last) > 3:
            singular = last[:-1]

        if singular:
            variants.append(" ".join([*words[:-1], singular]))

        if len(words) >= 4:
            variants.append(" ".join(words[-3:]))
        if len(words) >= 5:
            variants.append(" ".join(words[-4:]))

    deduped: list[str] = []
    seen: set[str] = set()
    for variant in variants:
        normalized = variant.lower()
        if normalized not in seen:
            deduped.append(variant)
            seen.add(normalized)
    return deduped


def _build_arxiv_query(query: str) -> str:
    topic = _clean_research_query(query)
    clauses: list[str] = []

    for variant in _topic_variants(topic):
        safe = variant.replace('"', "").strip()
        if not safe:
            continue
        if len(safe.split()) > 1:
            clauses.extend([f'ti:"{safe}"', f'abs:"{safe}"'])
        else:
            clauses.extend([f"ti:{safe}", f"abs:{safe}"])

    return " OR ".join(clauses) if clauses else query


def _format_arxiv_results(results: list[arxiv_lib.Result]) -> str:
    docs = []
    for result in results:
        docs.append(
            f"Published: {result.updated.date()}\n"
            f"Title: {result.title}\n"
            f"Authors: {', '.join(author.name for author in result.authors)}\n"
            f"Summary: {result.summary}"
        )
    return "\n\n".join(docs) if docs else "No good Arxiv Result was found"


def _search_arxiv(query: str, latest: bool) -> str:
    search = arxiv_lib.Search(
        query=_build_arxiv_query(query),
        max_results=3,
        sort_by=(
            arxiv_lib.SortCriterion.SubmittedDate
            if latest
            else arxiv_lib.SortCriterion.Relevance
        ),
        sort_order=arxiv_lib.SortOrder.Descending,
    )
    client = arxiv_lib.Client(page_size=3, delay_seconds=5.0, num_retries=5)
    return _format_arxiv_results(list(client.results(search)))[:3500]


def search_research(query: str) -> ChatResponse:
    sources: dict[str, str] = {}
    latest = bool(RECENT_HINT_RE.search(query))
    wikipedia_query = _build_wikipedia_query(query)
    arxiv_query = _build_arxiv_query(query)

    try:
        sources["wikipedia"] = wikipedia_tool.invoke({"query": wikipedia_query})
    except Exception as exc:
        sources["wikipedia"] = f"Wikipedia failed: {exc}"

    try:
        sources["arxiv"] = _search_arxiv(query, latest=latest)
    except Exception as exc:
        sources["arxiv"] = f"arXiv failed: {exc}"

    prompt = (
        "You are a concise research assistant. Answer in English.\n"
        "Synthesize the sources below. Separate background context from research papers.\n"
        "If a source failed or is irrelevant, say that briefly.\n\n"
        "Ignore source items that are clearly unrelated to the user question.\n"
        "Return the final answer only. Do not say that you will summarize.\n\n"
        f"Question:\n{query}\n\n"
        f"Wikipedia search query:\n{wikipedia_query}\n\n"
        f"arXiv search query:\n{arxiv_query}\n\n"
        f"Wikipedia:\n{sources['wikipedia']}\n\n"
        f"arXiv:\n{sources['arxiv']}\n"
    )

    try:
        answer = invoke_text(prompt)
    except Exception as exc:
        answer = (
            "Không gọi được LLM để tổng hợp. Dưới đây là dữ liệu thô từ nguồn.\n\n"
            f"Wikipedia:\n{sources['wikipedia']}\n\narXiv:\n{sources['arxiv']}\n\n"
            f"Lỗi LLM: {exc}"
        )

    return ChatResponse(route="research", answer=answer, sources=sources)
