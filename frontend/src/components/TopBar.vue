<script setup lang="ts">
import type { HealthResponse } from '../types/api'

defineProps<{
  health: HealthResponse | null
  loading: boolean
}>()

const emit = defineEmits<{
  'open-settings': []
}>()
</script>

<template>
  <header class="topbar">
    <div class="brand">
      <div class="brand-mark">
        <span></span>
      </div>
      <div>
        <div class="brand-name">VISUAL<span>AGENT</span></div>
        <div class="brand-sub">LOCAL SYSTEM</div>
      </div>
    </div>

    <div class="telemetry">
      <div class="t-stat">
        <span class="t-num">{{ health ? `${health.llm_provider} / ${health.text_model}` : 'offline' }}</span>
        <span class="t-label">TEXT MODEL</span>
      </div>
      <div class="divider"></div>
      <div class="t-stat">
        <span class="t-num">{{ health ? `${health.vlm_provider} / ${health.vision_model}` : 'offline' }}</span>
        <span class="t-label">VISION MODEL</span>
      </div>
      <div class="divider"></div>
      <div class="status" :class="{ busy: loading, ok: health?.status === 'ok' }">
        <span class="status-dot"></span>
        <span>{{ loading ? 'RUNNING' : health?.status === 'ok' ? 'READY' : 'CHECKING' }}</span>
      </div>
      <button class="settings-btn" type="button" title="Settings" @click="emit('open-settings')">
        SETTINGS
      </button>
    </div>
  </header>
</template>

<style scoped>
.topbar {
  height: 46px;
  flex-shrink: 0;
  padding: 0 16px;
  background: var(--color-bg-gradient-end);
  border-bottom: 1px solid var(--border2);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.topbar::after {
  content: '';
  position: absolute;
  inset: auto 0 0;
  height: 1px;
  background: linear-gradient(90deg, var(--color-accent), transparent 62%);
  opacity: 0.5;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand-mark {
  width: 24px;
  height: 24px;
  border: 1px solid var(--color-accent);
  border-radius: 3px;
  display: grid;
  place-items: center;
  background: var(--color-accent-subtle);
  box-shadow: inset 0 0 18px rgba(0, 200, 180, 0.18);
}

.brand-mark span {
  width: 9px;
  height: 9px;
  border: 1px solid var(--color-accent);
  transform: rotate(45deg);
}

.brand-name {
  color: var(--color-accent);
  font-size: 13px;
  font-weight: 800;
  line-height: 1;
  letter-spacing: 0.08em;
}

.brand-name span {
  color: var(--color-text-secondary);
  margin-left: 2px;
}

.brand-sub {
  color: var(--color-text-muted);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
  margin-top: 3px;
}

.telemetry {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.t-stat {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.t-num {
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 700;
  max-width: 170px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.t-label {
  color: var(--color-text-muted);
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.1em;
}

.divider {
  width: 1px;
  height: 26px;
  background: var(--color-section-rule);
}

.status {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 800;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-text-muted);
}

.status.ok .status-dot {
  background: var(--color-accent);
  box-shadow: 0 0 12px var(--color-accent);
}

.status.busy .status-dot {
  background: var(--color-warning);
  box-shadow: 0 0 12px var(--color-warning);
}

.settings-btn {
  height: 28px;
  border: 1px solid var(--color-teal-border);
  border-radius: 3px;
  background: var(--color-accent-subtle);
  color: var(--color-accent);
  padding: 0 10px;
  font-size: 10px;
  font-weight: 900;
  letter-spacing: 0.08em;
  cursor: pointer;
}

.settings-btn:hover {
  border-color: var(--color-accent);
  background: var(--color-accent-light);
}

@media (max-width: 760px) {
  .topbar {
    height: auto;
    min-height: 58px;
    align-items: flex-start;
    flex-direction: column;
    padding: 10px 12px;
    gap: 10px;
  }

  .telemetry {
    width: 100%;
    justify-content: space-between;
    gap: 8px;
  }

  .t-stat {
    align-items: flex-start;
  }

  .divider {
    display: none;
  }

  .settings-btn {
    margin-left: auto;
  }
}
</style>
