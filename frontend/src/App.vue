<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { clearMemory, getHealth, getProviderSettings, runChat, saveProviderSettings, uploadImage } from './api/client'
import ConsolePanel from './components/ConsolePanel.vue'
import MissionPanel from './components/MissionPanel.vue'
import SettingsModal from './components/SettingsModal.vue'
import TopBar from './components/TopBar.vue'
import WorkflowPanel from './components/WorkflowPanel.vue'
import type { ChatResponse, HealthResponse, ProviderSettings, ProviderSettingsPayload } from './types/api'

const message = ref('')
const health = ref<HealthResponse | null>(null)
const response = ref<ChatResponse | null>(null)
const error = ref<string | null>(null)
const busy = ref(false)
const providerSettings = ref<ProviderSettings | null>(null)
const settingsOpen = ref(false)
const settingsSaving = ref(false)
const settingsError = ref<string | null>(null)
const uploadedPath = ref<string | null>(null)
const uploadedUrl = ref<string | null>(null)
const uploadedName = ref<string | null>(null)

onMounted(async () => {
  await Promise.all([loadHealth(), loadProviderSettings()])
})

async function loadHealth() {
  try {
    health.value = await getHealth()
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err)
  }
}

async function loadProviderSettings() {
  try {
    providerSettings.value = await getProviderSettings()
  } catch (err) {
    settingsError.value = err instanceof Error ? err.message : String(err)
  }
}

async function handleUpload(file: File) {
  error.value = null
  uploadedName.value = 'uploading'
  try {
    const uploaded = await uploadImage(file)
    uploadedPath.value = uploaded.path
    uploadedUrl.value = uploaded.url
    uploadedName.value = uploaded.file_name
  } catch (err) {
    uploadedPath.value = null
    uploadedUrl.value = null
    uploadedName.value = null
    error.value = err instanceof Error ? err.message : String(err)
  }
}

async function executeMission() {
  error.value = null
  busy.value = true
  response.value = null
  try {
    const result = await runChat(message.value, 'auto', uploadedPath.value)
    response.value = result
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err)
  } finally {
    busy.value = false
  }
}

async function openSettings() {
  settingsError.value = null
  settingsOpen.value = true
  if (!providerSettings.value) {
    await loadProviderSettings()
  }
}

async function handleSaveSettings(payload: ProviderSettingsPayload) {
  settingsError.value = null
  settingsSaving.value = true
  try {
    providerSettings.value = await saveProviderSettings(payload)
    await loadHealth()
    settingsOpen.value = false
  } catch (err) {
    settingsError.value = err instanceof Error ? err.message : String(err)
  } finally {
    settingsSaving.value = false
  }
}

async function handleClearMemory() {
  if (!window.confirm('Clear all saved conversation memory?')) return
  error.value = null
  try {
    await clearMemory()
    if (response.value?.artifacts) {
      response.value.artifacts.memory_used = []
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : String(err)
  }
}
</script>

<template>
  <div class="app-shell">
    <TopBar :health="health" :loading="busy" @open-settings="openSettings" />
    <div class="main-grid">
      <section class="left-stack">
        <MissionPanel
          v-model:message="message"
          :busy="busy"
          :uploaded-name="uploadedName"
          :preview-url="uploadedUrl"
          @upload="handleUpload"
          @run="executeMission"
        />
        <WorkflowPanel
          mode="auto"
          :busy="busy"
          :response="response"
          :health="health"
          :uploaded-name="uploadedName"
        />
      </section>
      <ConsolePanel
        :response="response"
        :error="error"
        :busy="busy"
        @clear-memory="handleClearMemory"
      />
    </div>
    <SettingsModal
      :visible="settingsOpen"
      :settings="providerSettings"
      :saving="settingsSaving"
      :error="settingsError"
      @close="settingsOpen = false"
      @save="handleSaveSettings"
    />
  </div>
</template>

<style>
:root {
  --color-bg-deep: #04080f;
  --color-bg-gradient-end: #070d18;
  --border2: rgba(0, 200, 180, 0.2);
  --bg3: #0d1625;
  --bg2: #070d18;
  --color-glass: rgba(0, 200, 180, 0.04);
  --color-glass-border: rgba(0, 200, 180, 0.09);
  --color-border-subtle: rgba(0, 200, 180, 0.06);
  --color-glass-hover: rgba(0, 200, 180, 0.08);
  --color-glass-active: rgba(0, 200, 180, 0.12);
  --color-scrollbar-thumb: rgba(0, 200, 180, 0.45);
  --color-scrollbar-thumb-hover: rgba(0, 200, 180, 0.7);
  --color-text-primary: #d4f5ef;
  --color-text-secondary: #5a9e94;
  --color-text-muted: #2a5550;
  --color-text-bold: #e8f0ef;
  --color-accent: #00c8b4;
  --color-accent-hover: #00e5d0;
  --color-accent-subtle: rgba(0, 200, 180, 0.05);
  --color-accent-light: rgba(0, 200, 180, 0.08);
  --color-accent-medium: rgba(0, 200, 180, 0.12);
  --color-accent-focus: rgba(0, 200, 180, 0.2);
  --color-teal-dim: rgba(0, 200, 180, 0.08);
  --color-teal-border: rgba(0, 200, 180, 0.18);
  --color-teal-border2: rgba(0, 200, 180, 0.35);
  --color-warning: #f0c040;
  --color-error: #ff4060;
  --color-surface-dark: #0d1625;
  --color-surface-elevated: #142030;
  --color-section-rule: rgba(0, 200, 180, 0.2);
  --font-mono: Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  --font-sans: Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  --radius-sm: 3px;
  --radius-md: 3px;
  --radius-lg: 3px;
  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.35);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.4);
}

*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

@supports (-moz-appearance: none) {
  *,
  *::before,
  *::after {
    scrollbar-width: thin;
    scrollbar-color: var(--color-scrollbar-thumb) transparent;
  }
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--color-scrollbar-thumb);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-scrollbar-thumb-hover);
}

button,
input,
select,
textarea {
  font-family: inherit;
}

body {
  min-width: 320px;
  min-height: 100vh;
  font-family: var(--font-sans);
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text-primary);
  background:
    linear-gradient(135deg, var(--color-bg-deep) 0%, var(--color-bg-gradient-end) 100%);
  background-attachment: fixed;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body::before {
  content: '';
  position: fixed;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 18% 20%, rgba(0, 200, 180, 0.12) 0 1px, transparent 1.5px),
    radial-gradient(circle at 66% 28%, rgba(240, 192, 64, 0.12) 0 1px, transparent 1.5px),
    radial-gradient(circle at 86% 78%, rgba(0, 200, 180, 0.1) 0 1px, transparent 1.5px);
  background-size: 260px 220px, 420px 380px, 520px 460px;
  opacity: 0.65;
}

.app-shell {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.main-grid {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(340px, 480px) 1fr;
  gap: 12px;
  padding: 12px;
  overflow: hidden;
}

.left-stack {
  min-height: 0;
  display: grid;
  grid-template-rows: auto minmax(280px, 1fr);
  gap: 12px;
  overflow: hidden;
}

@media (max-width: 980px) {
  .app-shell {
    height: auto;
    min-height: 100vh;
    overflow: visible;
  }

  .main-grid {
    grid-template-columns: 1fr;
    overflow: visible;
  }

  .left-stack {
    overflow: visible;
  }
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
