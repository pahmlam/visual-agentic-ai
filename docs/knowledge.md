# Nhật Ký Kiến Thức

File này ghi lại các lỗi đã sửa, ghi chú debug, và các câu trả lời kỹ thuật quan trọng trong project.

## 2026-05-27

### zsh `event not found: apt`

- Nguyên nhân: Trong `zsh`, `!apt-get` kích hoạt history expansion. Đây là cú pháp thường dùng trong notebook, không phải cú pháp terminal bình thường.
- Cách sửa: Chạy lệnh terminal mà không có dấu `!`.
- Ghi chú macOS: `apt-get` dành cho Debian/Ubuntu. Trên macOS nên dùng Homebrew, ví dụ `brew install libmagic`.

### OpenAI `RateLimitError: insufficient_quota`

- Nguyên nhân: API key OpenAI đã hết quota, chưa có billing, hoặc bị chặn bởi giới hạn chi tiêu.
- Đổi từ `gpt-4.1-nano` sang model OpenAI khác vẫn có thể lỗi nếu quota đã hết.
- Hướng thay thế miễn phí/local: dùng Ollama với LangChain.

### Ollama trên MacBook Air M2

- MacBook Air M2 chạy được các local model nhỏ và vừa thông qua Ollama.
- Model nên bắt đầu: `llama3.2:3b`.
- Nếu máy có 8 GB RAM, nên ưu tiên model 3B. Nếu có 16 GB RAM, có thể thử model 7B/8B nhưng máy có thể nóng và chậm hơn.

### `ModuleNotFoundError: No module named 'langchain_ollama'`

- Nguyên nhân: `langchain-ollama` chưa được cài trong virtual environment của project.
- Cách sửa đã áp dụng:
  - Cài `langchain-ollama`.
  - Chỉnh dependency cho tương thích bằng `langchain-ollama==0.3.10` với `langchain-core==0.3.86`.
- Đã kiểm tra:
  - `from langchain_ollama import ChatOllama` import thành công.
  - `ChatOllama(model="llama3.2:3b").invoke(...)` gọi được Ollama local server.

### Quản lý model Ollama

- Ollama chủ yếu được quản lý bằng terminal.
- Các lệnh thường dùng:
  - `ollama list`: xem danh sách model đã tải.
  - `ollama pull llama3.2:3b`: tải model.
  - `ollama run llama3.2:3b`: chat với model trong terminal.
  - `ollama rm llama3.2:3b`: xóa model.
  - `ollama ps`: xem model đang được load/chạy.
  - `ollama show llama3.2:3b`: xem thông tin chi tiết của model.

### arXiv `HTTP 429`

- Nguyên nhân: arXiv API đang rate-limit, thường do gửi quá nhiều request hoặc fetch page quá lớn.
- Dấu hiệu: `HTTPError: Page request resulted in HTTP 429`.
- Cách giảm lỗi:
  - Giảm số lượng kết quả cần lấy.
  - Thêm delay và retry.
  - Tránh chạy lại cùng một cell notebook liên tục.
  - Nếu IP bị rate-limit tạm thời, đợi vài phút rồi chạy lại.

### LangChain `ArxivAPIWrapper` fetching `max_results=100`

- Vấn đề: Dù set `top_k_results=2`, bên dưới `arxiv.Search.results()` vẫn có thể dùng `arxiv.Client()` với `page_size=100` mặc định.
- Hệ quả: URL request vẫn có thể chứa `max_results=100`, làm tăng nguy cơ bị rate-limit.
- Cách tốt hơn: subclass `ArxivAPIWrapper` và dùng rõ `arxiv.Client(page_size=top_k_results, delay_seconds=5.0, num_retries=5)`.

Ví dụ:

```python
import arxiv as arxiv_lib

from langchain_community.utilities import ArxivAPIWrapper
from langchain_community.tools import ArxivQueryRun


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


arxiv_wrapper = RateLimitFriendlyArxivAPIWrapper(
    top_k_results=2,
    load_max_docs=2,
    doc_content_chars_max=1000,
    continue_on_failure=True,
)

arxiv_tool = ArxivQueryRun(
    api_wrapper=arxiv_wrapper,
    description="Search arXiv papers for a given research topic.",
)

result = arxiv_tool.invoke({
    "query": 'ti:"RoFormer" OR abs:"Rotary Position Embedding"'
})

print(result)
```

### arXiv query trả về paper không liên quan

- Query `"Rotary Positional Encoding"` có thể match nhầm các paper chứa những từ như "Positional" và "Encoding" nhưng không liên quan tới RoPE trong Transformer.
- Query chính xác hơn:
  - `ti:"RoFormer"`
  - `ti:"RoFormer" OR abs:"Rotary Position Embedding"`
- Paper liên quan thường cần tìm: `RoFormer: Enhanced Transformer with Rotary Position Embedding`.

## 2026-05-28

### Cơ chế search của code arXiv trong LangChain

- `ArxivQueryRun` là LangChain tool nhận input dạng `{"query": "..."}`.
- Tool gọi `ArxivAPIWrapper.run(query)`.
- `ArxivAPIWrapper` tạo request qua package Python `arxiv`, rồi package này gọi endpoint `https://export.arxiv.org/api/query`.
- arXiv API không phải semantic search. Nó chủ yếu match từ khóa theo cú pháp query của arXiv.
- `sortBy=relevance` chỉ sắp xếp kết quả theo độ liên quan do arXiv tính, không đảm bảo hiểu đúng intent như LLM hoặc Google.
- Query quá chung như `"Rotary Positional Encoding"` có thể match nhầm các paper chứa từ "Positional" và "Encoding".
- Nên dùng field search để chính xác hơn:
  - `ti:"RoFormer"`: tìm trong title.
  - `abs:"Rotary Position Embedding"`: tìm trong abstract.
  - `au:"Tên tác giả"`: tìm theo author.
- Trong version đang dùng, `arxiv.Search.results()` có thể dùng client mặc định `page_size=100`; nên dùng `arxiv.Client(page_size=top_k_results, delay_seconds=5.0, num_retries=5)` để tránh request quá lớn và giảm lỗi 429.

### Dùng Ollama với LangGraph `create_react_agent`

- `create_react_agent` có thể nhận model object, không bắt buộc phải truyền string model OpenAI.
- Để dùng Ollama, tạo `ChatOllama` rồi truyền vào `model`.
- Với agent có tools, `ChatOllama` trong môi trường hiện tại có hỗ trợ `bind_tools`.
- Nên đặt `temperature=0` cho agent dùng tool để giảm trả lời lan man.
- Nếu dùng tool biến tên `arxiv_tool`, phải truyền `tools=[arxiv_tool, wikipedia]`, tránh nhầm với module/package tên `arxiv`.

### Vì sao LangGraph agent chỉ dùng một tool

- Trong `create_react_agent`, `tools=[arxiv_tool, wikipedia]` là danh sách tool mà agent được phép chọn, không phải pipeline bắt buộc phải chạy hết.
- Agent sẽ gọi 0, 1, hoặc nhiều tool tùy model đánh giá câu hỏi cần gì.
- Với query chung như `"machine learning"`, agent thường chọn `wikipedia` vì phù hợp để lấy định nghĩa/tổng quan.
- `arxiv_tool` thường chỉ được chọn khi câu hỏi có ngữ cảnh nghiên cứu/paper, ví dụ `"find recent arXiv papers about rotary position embedding"`.
- Nếu muốn luôn dùng cả hai, cần ghi rõ trong prompt hoặc tự gọi cả hai tool rồi tổng hợp kết quả. Với model nhỏ như `llama3.2:3b`, cách tự gọi tool thủ công thường ổn định hơn ép agent tự làm.

### `PydanticOutputParser` bị `JSONDecodeError` với Ollama

- Nguyên nhân: Parser mong model trả về JSON đúng schema, nhưng `llama3.2:3b` có thể trả lời thêm markdown/giải thích/code nên không parse được JSON.
- Dấu hiệu: `OUTPUT_PARSING_FAILURE` hoặc `JSONDecodeError`.
- Cách sửa ổn định:
  - Dùng `ChatOllama(format="json", temperature=0)` để ép JSON mode.
  - Prompt phải yêu cầu "Return only valid JSON".
  - Nếu chỉ cần extract pattern đơn giản như URL/path, có thể dùng regex/Python parser thay vì LLM.
- Với structured output, model lớn hơn hoặc model có khả năng tuân thủ JSON tốt hơn sẽ ổn định hơn.

### `PydanticOutputParser` là gì

- `PydanticOutputParser` là output parser của LangChain dùng để ép output của LLM thành object theo schema Pydantic.
- Quy trình:
  - Định nghĩa class Pydantic, ví dụ `ImageInput`.
  - Parser tạo format instructions để bảo model trả JSON đúng field.
  - LLM trả text JSON.
  - Parser parse JSON đó thành object Pydantic.
- Lợi ích: code phía sau nhận object có field rõ ràng thay vì text tự do.
- Điểm yếu: nếu model trả thêm giải thích/markdown hoặc JSON sai format, parser sẽ lỗi.


Ví dụ bạn có schema:

```python
class ImageInput(BaseModel):
    image_path_or_url: str
```

Thì `PydanticOutputParser` sẽ yêu cầu LLM trả về JSON kiểu:

```json
{
  "image_path_or_url": "https://example.com/image.png"
}
```

Sau đó parser biến JSON đó thành object Python:

```python
ImageInput(image_path_or_url="https://example.com/image.png")
```

Lợi ích: thay vì nhận text tự do từ model, bạn nhận dữ liệu có field rõ ràng để code xử lý tiếp.

Điểm yếu: nếu model trả thêm giải thích như:

```text
Here is the JSON:
{
  "image_path_or_url": "..."
}
```

hoặc trả JSON sai format, parser sẽ lỗi `JSONDecodeError` / `OUTPUT_PARSING_FAILURE`.

### `PydanticOutputParser` lỗi field required vì model trả schema

- Dấu hiệu: output có dạng `{"properties": {...}, "required": [...]}` rồi báo thiếu field thật như `image_path_or_url`.
- Nguyên nhân: model trả nhầm JSON schema/format instructions thay vì trả object dữ liệu.
- Parser cần output dạng `{"image_path_or_url": "https://example.com/image.png"}`, không phải schema mô tả field.
- Cách giảm lỗi:
  - Prompt phải ghi rõ "Do not return the schema".
  - Cho ví dụ output đúng.
  - Dùng `ChatOllama(format="json", temperature=0)`.
  - Với extraction đơn giản, dùng regex hoặc parser thủ công sẽ ổn định hơn.

### Vì sao nên dùng schema output/Pydantic thay vì chỉ prompt

- Prompt chỉ là hướng dẫn cho LLM, không đảm bảo output luôn đúng format.
- Schema/Pydantic tạo một hợp đồng dữ liệu rõ ràng giữa LLM và code phía sau.
- Parser có thể kiểm tra output có đủ field, đúng kiểu dữ liệu, đúng cấu trúc hay không.
- Khi output sai, code fail sớm với lỗi rõ ràng thay vì truyền text sai xuống bước sau.
- Schema giúp pipeline ổn định hơn khi cần automation, agent, tool calling, lưu database, gọi API, hoặc xử lý batch.
- Vẫn cần prompt tốt, nhưng prompt tốt chỉ giúp model trả lời đúng hơn; schema/parser giúp chương trình xác minh câu trả lời đó có dùng được không.

### Dùng Ollama để mô tả ảnh

- `llama3.2:3b` là text model, không đọc được ảnh.
- Muốn gửi image input qua Ollama cần dùng vision model, ví dụ `llama3.2-vision` hoặc `llava`.
- Với LangChain `ChatOllama`, có thể truyền ảnh theo dạng message content có `type="image_url"` và data URL base64, nhưng model phải hỗ trợ image.
- `with_structured_output(ImageDescription)` có thể dùng được, nhưng với Ollama/local model có thể không ổn định bằng tách hai bước:
  - Bước 1: vision model mô tả ảnh thành text.
  - Bước 2: parser/structured output chuẩn hóa text đó nếu cần.
- Với MacBook Air M2, vision model thường nặng hơn text model 3B, cần cân nhắc RAM và tốc độ.

### Ollama agent in ra JSON tool call thay vì chạy tool

- Dấu hiệu: stream chỉ in `Ai Message` có nội dung như `{"name": "arXiv", "parameters": {"query": "machine learning"}}`.
- Nguyên nhân thường gặp: model local nhỏ trả tool call như text thường trong `content`, thay vì trả tool call chuẩn trong metadata/message format mà LangGraph hiểu.
- Khi đó graph không chuyển sang tool node, nên chưa có `Tool Message` hoặc kết quả thật từ tool.
- Cách kiểm tra: xem message có `tool_calls` hay không. Nếu chỉ có JSON trong `content`, tool chưa chạy.
- Cách xử lý:
  - Dùng model có tool calling tốt hơn.
  - Thử `create_react_agent(..., version="v2")` nếu version LangGraph hỗ trợ.
  - Với workflow học/test, gọi tool thủ công rồi đưa kết quả cho LLM tổng hợp thường ổn định hơn local model nhỏ.

### Wrap image describer thành `BaseTool` với Ollama

- `BaseTool` không phụ thuộc OpenAI hay Ollama; phần cần chú ý là chain bên trong tool.
- Với Pydantic v2/LangChain hiện tại, nên khai báo `args_schema: type[BaseModel] = ImageDescriberInput`, không cần `Optional`.
- Nếu input tool chỉ là path/URL như `./github_logo.png`, không cần dùng LLM để extract path; có thể dùng trực tiếp hoặc chỉ fallback sang extractor khi input là câu tự nhiên.
- `_arun` không nên truyền `AsyncCallbackManagerForToolRun` vào `_run` nếu `_run` type hint là `CallbackManagerForToolRun`.
- `return_direct=True` làm agent trả kết quả tool trực tiếp và dừng; chỉ dùng nếu muốn như vậy.
- Với Ollama vision, `image_describer_agent` phải dùng vision model như `llama3.2-vision`, không dùng `llama3.2:3b`.

### Provider settings cho LLM/VLM

- App đã có cấu hình provider riêng cho LLM và VLM:
  - `ollama`: chạy local bằng `langchain-ollama`.
  - `openai`: gọi GPT/OpenAI bằng `OPENAI_API_KEY`.
  - `gemini`: gọi Gemini qua Google Generative Language API bằng `GEMINI_API_KEY`.
- UI có một nút `SETTINGS` trên top bar để chọn provider, model text, model vision, và nhập API key nếu cần.
- Backend lưu cấu hình vào `.env` qua `POST /api/settings`.
- `GET /api/settings` không trả raw API key về frontend, chỉ trả boolean `has_openai_api_key` và `has_gemini_api_key`.
- `GET /api/health` trả provider/model đang active để UI hiển thị trạng thái hiện tại.
- `Settings` trong `app/config.py` phải đọc env trong `__init__`; nếu đặt giá trị ở class attribute thì `reload_settings()` không đọc lại `.env`/`os.environ` đúng sau khi user đổi provider.
- Backend và UI đều validate model name không được rỗng trước khi lưu `.env`.
- Khi gọi Gemini, không dùng trực tiếp `raise_for_status()` để tránh exception hiển thị URL có query `key=...`; cần raise lỗi đã sanitize.

### Port mặc định của repo web app

- Backend FastAPI mặc định chạy ở `127.0.0.1:8300`.
- Frontend Vite dev server mặc định chạy ở `127.0.0.1:5177`.
- `frontend/vite.config.ts` proxy `/api` và `/uploads` về `http://127.0.0.1:8300`.
- README và AGENTS phải giữ nhất quán hai port này để tránh mở nhầm server cũ `8000` hoặc Vite port cũ.

### Dùng Ollama cho `vision_agent`

- Thay `model="gpt-4o-mini"` bằng `ChatOllama(...)`.
- Nếu agent chỉ quyết định chọn tool, có thể dùng text model như `llama3.2:3b`.
- Nếu chính agent cần nhìn ảnh trực tiếp thì phải dùng vision model như `llama3.2-vision`.
- Với local model nhỏ, tool-calling có thể không ổn định; nếu model in JSON tool call như text mà không chạy tool, nên gọi tool trực tiếp hoặc viết router thủ công.
- Với tác vụ đếm object, tool YOLO/detect thường nên được gọi trực tiếp vì chính xác và ổn định hơn để LLM tự chọn.

### Dùng Ollama cho `langgraph_supervisor`

- `create_supervisor` nhận trực tiếp runnable model, nên có thể truyền `ChatOllama(...)` thay vì `init_chat_model("gpt-4o-mini")`.
- Supervisor dùng cơ chế handoff tới agent, về bản chất cũng là tool/function calling.
- Với model local nhỏ như `llama3.2:3b`, supervisor có thể in JSON handoff như text thay vì gọi agent thật.
- Nếu handoff không ổn định, nên dùng model local có tool calling tốt hơn, hoặc viết router thủ công dựa trên keyword/intent.
- `parallel_tool_calls=False` phù hợp với rule "không gọi nhiều agent song song".

### `for chunk in supervisor.stream(...)` nghĩa là gì

- `.stream(...)` của LangGraph trả về một iterator/generator.
- Mỗi `chunk` là một update mới của graph trong lúc chạy, ví dụ supervisor quyết định handoff, agent gọi tool, tool trả kết quả, agent trả lời cuối.
- `for chunk in ...` nghĩa là Python lặp qua từng update đó ngay khi nó xuất hiện, thay vì đợi toàn bộ graph chạy xong.
- Biến `chunk` sau vòng lặp vẫn giữ update cuối cùng, nên có thể dùng tiếp như `get_final_supervisor_messages(chunk)`.
- Nếu không cần xem từng bước trung gian, có thể dùng `.invoke(...)` để nhận kết quả cuối cùng một lần.

### Chuyển notebook Visual Agent thành repo web app

- Cấu trúc app mới:
  - `app/main.py`: FastAPI entrypoint, serve API và static UI.
  - `app/services/research.py`: Wikipedia/arXiv lookup và Ollama text synthesis.
  - `app/services/vision.py`: Ollama vision description và YOLO detection/counting.
  - `app/services/router.py`: route thủ công giữa research/vision để tránh phụ thuộc quá nhiều vào tool-calling của model nhỏ.
  - `app/static/`: web UI chạy trực tiếp, không cần npm build.
- Lý do dùng router thủ công: `llama3.2:3b` có thể yếu ở handoff/tool-calling, nên backend tự quyết định gọi service nào sẽ ổn định hơn cho app local.
- Backend vẫn giữ tinh thần agent pipeline:
  - Research dùng nguồn Wikipedia + arXiv rồi LLM tổng hợp.
  - Vision dùng YOLO để detect/count và Ollama vision để describe.
  - Auto mode có thể chạy cả vision và research nếu prompt vừa có ảnh vừa hỏi thông tin nghiên cứu.
- UI theme dùng phong cách space/alien/technology với font stack monospace: `Space Mono`, `Menlo`, `Monaco`, `Consolas`, monospace.
- Các file vận hành:
  - `requirements.txt`: dependency chính.
  - `.env.example`: cấu hình model/path.
  - `scripts/run_local.sh`: chạy server local.
  - `README.md`: hướng dẫn setup/run.

### Chuyển UI Visual Agent sang stack giống `knowte`

- Stack frontend của `knowte`: Vue 3, Vite, TypeScript, Single File Components, scoped CSS, API client wrapper.
- Visual Agent đã được chuyển từ static HTML/CSS/JS sang `frontend/` theo stack đó.
- `frontend/vite.config.ts` build output vào `app/static`, nên FastAPI vẫn serve UI tại `http://127.0.0.1:8300`.
- UI mới dùng app shell full-height giống console:
  - `TopBar.vue`: model/status telemetry.
  - `AgentRail.vue`: supervisor/research/vision routing status.
  - `MissionPanel.vue`: mode, prompt, upload, quick tasks.
  - `ConsolePanel.vue`: answer, sources, YOLO artifacts.
- Theme bám palette alien/technology của `knowte`: dark teal, sharp 3px radius, Menlo monospace, dense operational panels.
- Build command:
  - `cd frontend && npm run build`
  - hoặc `./scripts/build_frontend.sh`.

### Thêm `AGENTS.md` cho session Codex mới

- `AGENTS.md` được thêm ở root repo để agent mới nắm nhanh project.
- Nội dung chính:
  - Trả lời bằng tiếng Việt.
  - Luôn cập nhật `docs/knowledge.md` khi có fix/kiến thức mới.
  - App source chính nằm trong `app/` và `frontend/`, notebook chỉ là tham khảo.
  - Frontend phải theo stack `knowte`: Vue 3, Vite, TypeScript, SFC scoped CSS.
  - Backend chạy FastAPI, Ollama, arXiv/Wikipedia, YOLO.
  - Lệnh build/chạy/kiểm tra nhanh.
  - Cảnh báo không copy secrets từ notebook cũ.

### Nút `positional research` trong UI

- `positional research` là quick prompt preset trong `MissionPanel.vue`.
- Nó chỉ tự điền prompt mẫu `What is the latest research on positional embeddings?` để test nhanh research route.
- Đây không phải một agent/tool riêng và không có logic đặc biệt trong backend.
- Nếu label gây khó hiểu, nên đổi thành tên rõ hơn như `sample research`, `research demo`, hoặc bỏ hẳn khỏi quick actions.
- Đã đổi label thành `research demo` trong `frontend/src/components/MissionPanel.vue`.

### Research query không được hardcode theo từng chủ đề

- Lỗi từng gặp: prompt `What is the latest research on positional embeddings?` trả về nguồn lệch như Llama/GPS và paper có chữ `research` nhưng không liên quan.
- Nguyên nhân: backend đưa nguyên câu hỏi tự nhiên vào Wikipedia/arXiv; arXiv/Wikipedia là keyword search, không hiểu intent như semantic search.
- Không nên hardcode riêng cho `positional embeddings`, vì hỏi chủ đề khác sẽ phải sửa code.
- Cách sửa hiện tại trong `app/services/research.py`:
  - `_clean_research_query(...)` bỏ từ nhiễu như `what/latest/research/papers/about`.
  - `_build_arxiv_query(...)` search topic trong `ti:` và `abs:`.
  - `_topic_variants(...)` thêm biến thể singular/plural và suffix phrase cho query dài.
  - Nếu query có `latest/recent`, arXiv sort theo `SubmittedDate` giảm dần.
- Ví dụ:
  - Input: `What is the latest research on positional embeddings?`
  - Clean topic: `positional embeddings`
  - arXiv query: `ti:"positional embeddings" OR abs:"positional embeddings" OR ti:"positional embedding" OR abs:"positional embedding"`

### Đơn giản hóa UI theo hướng supervisor-first

- User không muốn UI lộ agent rail, `mission control`, hoặc các nút demo query.
- Cách chỉnh:
  - Xóa `AgentRail.vue`.
  - Thêm `WorkflowPanel.vue` để hiện animation luồng xử lý.
  - `MissionPanel.vue` đổi thành khung `supervisor`, bỏ quick buttons và bỏ selector `auto/research/vision`.
  - `App.vue` đổi layout thành 2 cột: supervisor input + workflow ở trái, answer/artifacts ở phải.
- Người dùng chỉ tương tác với supervisor; frontend luôn gửi `mode="auto"` để backend tự route.
- Build frontend đã cập nhật vào `app/static`.

### Tài liệu kỹ thuật chi tiết (Technical Document)

- Đã tạo tài liệu kỹ thuật tại [technical_document.md](file:///Users/phamtunglam/Documents/Projects/visual-agent/docs/technical_document.md) để mô tả toàn bộ cấu trúc thư mục, kiến trúc Client-Server, luồng dữ liệu của các Services (Research, Vision, LLM, Image I/O) và cơ chế định tuyến thủ công (manual routing flow).
- Tài liệu sử dụng sơ đồ Mermaid giúp mô tả sinh động cách thức điều phối của hệ thống từ lúc nhận request đến khi điều hướng thành công.
- Ghi nhận chi tiết cách khắc phục lỗi rate-limit của arXiv qua custom `arxiv.Client` và cơ chế gom cụm (combine) kết quả Vision + Research trong chế độ `auto`.

### Tài liệu API (API Document)

- Đã tạo tài liệu API chi tiết tại [api_document.md](file:///Users/phamtunglam/Documents/Projects/visual-agent/docs/api_document.md) liệt kê đầy đủ toàn bộ 8 API Endpoints của backend FastAPI.
- Tài liệu mô tả rõ Method, URL, Schema Request/Response, ví dụ Payload thực tế cho các API: Health Check (`/api/health`), Settings Management (`/api/settings` GET & POST), Upload tệp tin (`/api/upload`), Chat Router (`/api/chat`) và các endpoint nghiệp vụ trực tiếp (`/api/research`, `/api/vision/describe`, `/api/vision/detect`).

### Hướng dẫn tải model trong README.md

- Đã cập nhật [README.md](file:///Users/phamtunglam/Documents/Projects/visual-agent/README.md) để cung cấp hướng dẫn cài đặt và thiết lập chi tiết:
  - **Ollama**: Hướng dẫn cài đặt từ web chính thức, khởi chạy nền, tải các model qua CLI (`llama3.2:3b` và `llama3.2-vision`) và kiểm tra bằng `ollama list`.
  - **YOLOv11**: Hướng dẫn tải trực tiếp file weights `yolo11x.pt` từ GitHub release chính thức của Ultralytics qua lệnh `curl`. Hướng dẫn thêm tuỳ chọn tải model nhẹ hơn (`yolo11n.pt`) cho máy cấu hình yếu kèm cách cấu hình lại biến `YOLO_MODEL_PATH` trong `.env`.



