<script setup lang="ts">
import { computed } from 'vue'
import type { ChatResponse, HealthResponse, Mode } from '../types/api'

const props = defineProps<{
  mode: Mode
  busy: boolean
  response: ChatResponse | null
  health: HealthResponse | null
  uploadedName: string | null
}>()

const activeRoute = computed(() => {
  if (props.response?.route) return props.response.route
  if (props.mode === 'research') return 'research'
  if (props.mode === 'vision') return 'vision'
  return props.uploadedName ? 'vision' : 'auto'
})

const steps = computed(() => {
  const route = activeRoute.value
  const base = [
    { label: 'Supervisor receives request', key: 'supervisor' },
    { label: route.includes('vision') ? 'Inspect visual payload' : 'Search external knowledge', key: route.includes('vision') ? 'vision' : 'research' },
    { label: route.includes('vision') ? 'Run local vision tools' : 'Synthesize sources with Ollama', key: 'work' },
    { label: 'Return final answer', key: 'done' },
  ]
  return base
})
</script>

<template>
  <aside class="workflow-panel">
    <div class="workflow-head">
      <div>
        <div class="kicker">workflow</div>
        <h2>{{ busy ? 'processing' : response?.route || 'standby' }}</h2>
      </div>
      <div class="orbit" :class="{ active: busy }">
        <span></span>
      </div>
    </div>

    <div class="flow-window">
      <div class="scanline"></div>
      <div
        v-for="(step, index) in steps"
        :key="step.key"
        class="flow-step"
        :class="{ active: busy, done: response && !busy }"
        :style="{ '--i': index }"
      >
        <span class="node"></span>
        <span class="label">{{ step.label }}</span>
      </div>
    </div>

    <div class="payload-grid">
      <div>
        <span>text</span>
        <strong>{{ health?.text_model || 'offline' }}</strong>
      </div>
      <div>
        <span>vision</span>
        <strong>{{ health?.vision_model || 'offline' }}</strong>
      </div>
      <div>
        <span>image</span>
        <strong>{{ uploadedName || 'none' }}</strong>
      </div>
      <div>
        <span>route</span>
        <strong>{{ activeRoute }}</strong>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.workflow-panel {
  min-height: 0;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
}

.workflow-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
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
  font-size: 15px;
  font-weight: 800;
  margin-top: 2px;
}

.orbit {
  width: 34px;
  height: 34px;
  border: 1px solid var(--color-teal-border2);
  border-radius: 50%;
  display: grid;
  place-items: center;
  position: relative;
}

.orbit::before {
  content: '';
  position: absolute;
  inset: 6px;
  border: 1px solid var(--color-glass-hover);
  border-radius: 50%;
}

.orbit span {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-accent);
  box-shadow: 0 0 14px var(--color-accent);
}

.orbit.active {
  animation: orbit-spin 1.8s linear infinite;
}

@keyframes orbit-spin {
  to {
    transform: rotate(360deg);
  }
}

.flow-window {
  position: relative;
  overflow: hidden;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  background:
    linear-gradient(rgba(0, 200, 180, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0, 200, 180, 0.03) 1px, transparent 1px),
    rgba(2, 7, 13, 0.7);
  background-size: 18px 18px;
  padding: 12px;
}

.scanline {
  position: absolute;
  left: 0;
  right: 0;
  top: -30%;
  height: 34px;
  background: linear-gradient(180deg, transparent, rgba(0, 200, 180, 0.12), transparent);
  animation: scan 2.4s linear infinite;
  opacity: 0.55;
}

@keyframes scan {
  to {
    transform: translateY(260px);
  }
}

.flow-step {
  position: relative;
  display: flex;
  align-items: center;
  gap: 9px;
  min-height: 34px;
  color: var(--color-text-secondary);
  font-size: 11px;
}

.flow-step + .flow-step::before {
  content: '';
  position: absolute;
  left: 5px;
  top: -11px;
  width: 1px;
  height: 22px;
  background: var(--color-teal-border);
}

.flow-step.active {
  animation: step-pulse 1.4s ease-in-out infinite;
  animation-delay: calc(var(--i) * 160ms);
}

.flow-step.done {
  color: var(--color-accent);
}

@keyframes step-pulse {
  50% {
    color: var(--color-accent);
  }
}

.node {
  width: 11px;
  height: 11px;
  border: 1px solid var(--color-accent);
  background: var(--color-bg-deep);
  flex-shrink: 0;
}

.flow-step.active .node {
  box-shadow: 0 0 14px rgba(0, 200, 180, 0.35);
}

.payload-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.payload-grid div {
  min-width: 0;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  background: var(--bg3);
  padding: 8px;
  display: grid;
  gap: 3px;
}

.payload-grid span {
  color: var(--color-text-muted);
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
}

.payload-grid strong {
  color: var(--color-text-secondary);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>

