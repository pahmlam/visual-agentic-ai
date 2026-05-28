<script setup lang="ts">
import type { ChatResponse } from '../types/api'

defineProps<{
  response: ChatResponse | null
  error: string | null
  busy: boolean
}>()

function formatJson(value: unknown): string {
  return JSON.stringify(value, null, 2)
}
</script>

<template>
  <main class="console-panel">
    <div class="console-header">
      <div>
        <div class="kicker">answer</div>
        <h2>{{ response?.route || (busy ? 'running' : 'ready') }}</h2>
      </div>
    </div>

    <section class="answer" :class="{ error }">
      <pre v-if="error">{{ error }}</pre>
      <pre v-else-if="busy">Dispatching task through local backend...</pre>
      <pre v-else-if="response">{{ response.answer }}</pre>
      <pre v-else>Awaiting mission input.</pre>
    </section>

    <section class="artifact-layout">
      <div v-if="response?.artifacts?.annotated_url" class="artifact wide">
        <div class="artifact-head">annotated image</div>
        <img :src="response.artifacts.annotated_url" alt="Annotated detection result" />
      </div>

      <div v-if="response?.artifacts?.counts" class="artifact">
        <div class="artifact-head">counts</div>
        <pre>{{ formatJson(response.artifacts.counts) }}</pre>
      </div>

      <div v-if="response?.artifacts?.detections?.length" class="artifact wide">
        <div class="artifact-head">detections</div>
        <table>
          <thead>
            <tr>
              <th>class</th>
              <th>confidence</th>
              <th>bbox</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in response.artifacts.detections.slice(0, 40)" :key="index">
              <td>{{ item.label }}</td>
              <td>{{ item.confidence.toFixed(2) }}</td>
              <td>{{ item.bbox.join(', ') }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-for="(value, key) in response?.sources || {}" :key="key" class="artifact source">
        <div class="artifact-head">{{ key }}</div>
        <pre>{{ value }}</pre>
      </div>
    </section>
  </main>
</template>

<style scoped>
.console-panel {
  flex: 1;
  min-width: 0;
  padding: 14px;
  overflow-y: auto;
  background:
    linear-gradient(rgba(0, 200, 180, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 200, 180, 0.02) 1px, transparent 1px);
  background-size: 24px 24px;
}

.console-header {
  min-height: 36px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.kicker {
  color: var(--color-text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

h2 {
  color: var(--color-accent);
  font-size: 17px;
  font-weight: 800;
  margin-top: 2px;
}

.answer,
.artifact {
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.26);
  box-shadow: var(--shadow-sm);
}

.answer {
  min-height: 240px;
  padding: 14px;
}

.answer.error {
  border-color: rgba(255, 64, 96, 0.45);
}

pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--color-text-primary);
  font-family: inherit;
  font-size: 13px;
  line-height: 1.58;
}

.artifact-layout {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.artifact {
  min-width: 0;
  overflow: hidden;
}

.artifact.wide {
  grid-column: 1 / -1;
}

.artifact.source {
  min-height: 180px;
}

.artifact-head {
  height: 30px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  border-bottom: 1px solid var(--color-glass-hover);
  color: var(--color-warning);
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  background: var(--color-accent-subtle);
}

.artifact pre {
  max-height: 320px;
  overflow: auto;
  padding: 10px;
  color: var(--color-text-secondary);
  font-size: 11px;
}

.artifact img {
  display: block;
  width: 100%;
  max-height: 480px;
  object-fit: contain;
  background: rgba(0, 0, 0, 0.32);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}

th,
td {
  border-bottom: 1px solid var(--color-border-subtle);
  padding: 7px 9px;
  text-align: left;
  color: var(--color-text-secondary);
}

th {
  color: var(--color-accent);
  font-weight: 900;
}

@media (max-width: 760px) {
  .artifact-layout {
    grid-template-columns: 1fr;
  }
}
</style>
