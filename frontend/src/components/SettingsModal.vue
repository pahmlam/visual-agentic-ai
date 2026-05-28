<script setup lang="ts">
import { computed, reactive, watch } from 'vue'
import type { Provider, ProviderSettings, ProviderSettingsPayload } from '../types/api'

const props = defineProps<{
  visible: boolean
  settings: ProviderSettings | null
  saving: boolean
  error: string | null
}>()

const emit = defineEmits<{
  close: []
  save: [payload: ProviderSettingsPayload]
}>()

const form = reactive<ProviderSettingsPayload>({
  llm_provider: 'ollama',
  vlm_provider: 'ollama',
  ollama_text_model: 'llama3.2:3b',
  ollama_vision_model: 'llama3.2-vision',
  openai_text_model: 'gpt-4.1-nano',
  openai_vision_model: 'gpt-4o-mini',
  gemini_text_model: 'gemini-2.5-flash',
  gemini_vision_model: 'gemini-2.5-flash',
  openai_api_key: '',
  gemini_api_key: '',
})

const providers: { value: Provider; label: string }[] = [
  { value: 'ollama', label: 'Ollama local' },
  { value: 'openai', label: 'GPT / OpenAI' },
  { value: 'gemini', label: 'Gemini' },
]

watch(
  () => props.settings,
  (settings) => {
    if (!settings) return
    form.llm_provider = settings.llm_provider
    form.vlm_provider = settings.vlm_provider
    form.ollama_text_model = settings.ollama_text_model
    form.ollama_vision_model = settings.ollama_vision_model
    form.openai_text_model = settings.openai_text_model
    form.openai_vision_model = settings.openai_vision_model
    form.gemini_text_model = settings.gemini_text_model
    form.gemini_vision_model = settings.gemini_vision_model
    form.openai_api_key = ''
    form.gemini_api_key = ''
  },
  { immediate: true },
)

const needsOpenAI = computed(() => form.llm_provider === 'openai' || form.vlm_provider === 'openai')
const needsGemini = computed(() => form.llm_provider === 'gemini' || form.vlm_provider === 'gemini')

const openAIKeyMissing = computed(
  () => needsOpenAI.value && !props.settings?.has_openai_api_key && !form.openai_api_key?.trim(),
)
const geminiKeyMissing = computed(
  () => needsGemini.value && !props.settings?.has_gemini_api_key && !form.gemini_api_key?.trim(),
)
const modelMissing = computed(() =>
  [
    form.ollama_text_model,
    form.ollama_vision_model,
    form.openai_text_model,
    form.openai_vision_model,
    form.gemini_text_model,
    form.gemini_vision_model,
  ].some((value) => !value.trim()),
)

const canSave = computed(
  () => !props.saving && !modelMissing.value && !openAIKeyMissing.value && !geminiKeyMissing.value,
)

function submit() {
  if (!canSave.value) return
  emit('save', { ...form })
}
</script>

<template>
  <Teleport to="body">
    <div v-if="visible" class="backdrop" @click.self="emit('close')">
      <section class="modal">
        <header class="modal-head">
          <div>
            <div class="kicker">settings</div>
            <h2>Providers</h2>
          </div>
          <button class="icon-btn" type="button" aria-label="Close settings" @click="emit('close')">×</button>
        </header>

        <div class="provider-grid">
          <label class="field">
            <span>LLM</span>
            <select v-model="form.llm_provider">
              <option v-for="provider in providers" :key="provider.value" :value="provider.value">
                {{ provider.label }}
              </option>
            </select>
          </label>
          <label class="field">
            <span>VLM</span>
            <select v-model="form.vlm_provider">
              <option v-for="provider in providers" :key="provider.value" :value="provider.value">
                {{ provider.label }}
              </option>
            </select>
          </label>
        </div>

        <div class="model-grid">
          <label class="field">
            <span>Ollama text model</span>
            <input v-model="form.ollama_text_model" />
          </label>
          <label class="field">
            <span>Ollama vision model</span>
            <input v-model="form.ollama_vision_model" />
          </label>
          <label class="field">
            <span>OpenAI text model</span>
            <input v-model="form.openai_text_model" />
          </label>
          <label class="field">
            <span>OpenAI vision model</span>
            <input v-model="form.openai_vision_model" />
          </label>
          <label class="field">
            <span>Gemini text model</span>
            <input v-model="form.gemini_text_model" />
          </label>
          <label class="field">
            <span>Gemini vision model</span>
            <input v-model="form.gemini_vision_model" />
          </label>
        </div>

        <div class="key-grid">
          <label class="field">
            <span>OpenAI API key</span>
            <input
              v-model="form.openai_api_key"
              type="password"
              autocomplete="off"
              :placeholder="settings?.has_openai_api_key ? 'saved in .env' : 'required for GPT/OpenAI'"
            />
          </label>
          <label class="field">
            <span>Gemini API key</span>
            <input
              v-model="form.gemini_api_key"
              type="password"
              autocomplete="off"
              :placeholder="settings?.has_gemini_api_key ? 'saved in .env' : 'required for Gemini'"
            />
          </label>
        </div>

        <p v-if="openAIKeyMissing" class="warning">OpenAI key is required when GPT/OpenAI is selected.</p>
        <p v-if="geminiKeyMissing" class="warning">Gemini key is required when Gemini is selected.</p>
        <p v-if="modelMissing" class="warning">All model names are required.</p>
        <p v-if="error" class="error">{{ error }}</p>

        <footer class="modal-actions">
          <button class="ghost" type="button" @click="emit('close')">Cancel</button>
          <button class="save" type="button" :disabled="!canSave" @click="submit">
            {{ saving ? 'Saving' : 'Save settings' }}
          </button>
        </footer>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(0, 0, 0, 0.64);
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal {
  width: min(760px, 100%);
  max-height: min(760px, calc(100vh - 40px));
  overflow: auto;
  border: 1px solid var(--color-teal-border2);
  border-radius: 3px;
  background: var(--color-bg-gradient-end);
  box-shadow: var(--shadow-lg);
  padding: 14px;
}

.modal-head,
.modal-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.modal-head {
  margin-bottom: 14px;
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
  font-size: 16px;
}

.icon-btn,
.ghost,
.save {
  border-radius: 3px;
  font-family: inherit;
  cursor: pointer;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border: 1px solid var(--color-glass-hover);
  background: var(--bg3);
  color: var(--color-text-secondary);
  font-size: 18px;
}

.provider-grid,
.key-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.model-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
  margin: 12px 0;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  color: var(--color-text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

input,
select {
  height: 36px;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  outline: none;
  background: rgba(0, 0, 0, 0.28);
  color: var(--color-text-primary);
  padding: 0 10px;
}

input:focus,
select:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-focus);
}

.warning,
.error {
  margin-top: 10px;
  font-size: 12px;
}

.warning {
  color: var(--color-warning);
}

.error {
  color: var(--color-error);
}

.modal-actions {
  margin-top: 14px;
}

.ghost,
.save {
  height: 34px;
  padding: 0 12px;
}

.ghost {
  border: 1px solid var(--color-glass-hover);
  background: transparent;
  color: var(--color-text-secondary);
}

.save {
  border: 0;
  background: var(--color-accent);
  color: var(--color-bg-deep);
  font-weight: 900;
}

.save:disabled {
  cursor: not-allowed;
  opacity: 0.58;
}

@media (max-width: 720px) {
  .provider-grid,
  .key-grid,
  .model-grid {
    grid-template-columns: 1fr;
  }
}
</style>
