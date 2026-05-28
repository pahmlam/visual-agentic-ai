<script setup lang="ts">
defineProps<{
  message: string
  busy: boolean
  uploadedName: string | null
  previewUrl: string | null
}>()

const emit = defineEmits<{
  'update:message': [value: string]
  upload: [file: File]
  run: []
}>()

function onUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    emit('upload', file)
  }
}
</script>

<template>
  <section class="mission-panel">
    <div class="panel-header">
      <span class="corner"></span>
      <h2>supervisor</h2>
      <span class="panel-code">local</span>
    </div>

    <label class="field">
      <span>ask anything</span>
      <textarea
        :value="message"
        placeholder="Ask for research, image description, or object counting..."
        spellcheck="false"
        @input="emit('update:message', ($event.target as HTMLTextAreaElement).value)"
      />
    </label>

    <div class="uplink">
      <label class="upload-btn">
        <input type="file" accept="image/png,image/jpeg,image/webp" @change="onUpload" />
        <span class="upload-title">image uplink</span>
        <span class="upload-sub">{{ uploadedName || 'png · jpg · webp' }}</span>
      </label>
      <div v-if="previewUrl" class="preview">
        <img :src="previewUrl" alt="Uploaded image preview" />
      </div>
    </div>

    <button class="run-btn" type="button" :disabled="busy || !message.trim()" @click="emit('run')">
      <span></span>
      {{ busy ? 'supervisor running' : 'send to supervisor' }}
    </button>
  </section>
</template>

<style scoped>
.mission-panel {
  min-width: 0;
  flex-shrink: 0;
  background: rgba(0, 0, 0, 0.18);
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  padding: 12px;
}

.panel-header {
  height: 30px;
  display: flex;
  align-items: center;
  gap: 9px;
  margin-bottom: 12px;
}

.corner {
  width: 12px;
  height: 12px;
  border: 1px solid var(--color-accent);
  background: var(--color-accent-subtle);
}

h2 {
  color: var(--color-text-primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.panel-code {
  margin-left: auto;
  color: var(--color-text-muted);
  font-size: 10px;
  font-weight: 800;
}

.field {
  display: grid;
  gap: 6px;
}

.field span {
  color: var(--color-text-muted);
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

textarea {
  width: 100%;
  height: 150px;
  min-height: 150px;
  resize: vertical;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  outline: none;
  background: rgba(0, 0, 0, 0.24);
  color: var(--color-text-primary);
  padding: 12px;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.55;
}

textarea:focus {
  border-color: var(--color-accent);
  box-shadow: 0 0 0 2px var(--color-accent-focus);
}

.uplink {
  margin-top: 12px;
}

.upload-btn {
  min-height: 64px;
  border: 1px dashed var(--color-teal-border2);
  border-radius: 3px;
  background: var(--color-accent-subtle);
  display: grid;
  align-content: center;
  gap: 3px;
  padding: 10px 12px;
  cursor: pointer;
}

.upload-btn input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.upload-title {
  color: var(--color-accent);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}

.upload-sub {
  color: var(--color-text-muted);
  font-size: 11px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview {
  margin-top: 8px;
  border: 1px solid var(--color-glass-hover);
  border-radius: 3px;
  background: rgba(0, 0, 0, 0.22);
  max-height: 230px;
  overflow: hidden;
}

.preview img {
  display: block;
  width: 100%;
  max-height: 230px;
  object-fit: contain;
}

.run-btn {
  width: 100%;
  height: 42px;
  margin-top: 12px;
  border: 0;
  border-radius: 3px;
  background: var(--color-accent);
  color: var(--color-bg-deep);
  font-family: inherit;
  font-size: 12px;
  font-weight: 900;
  text-transform: uppercase;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 9px;
}

.run-btn:disabled {
  cursor: wait;
  opacity: 0.62;
}

.run-btn span {
  width: 10px;
  height: 10px;
  border-top: 2px solid currentColor;
  border-right: 2px solid currentColor;
  transform: rotate(45deg);
}

@media (max-width: 980px) {
  .mission-panel {
    width: 100%;
  }
}
</style>
