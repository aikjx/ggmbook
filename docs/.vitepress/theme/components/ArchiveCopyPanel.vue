<script setup lang="ts">
import { ref } from 'vue'

const props = defineProps<{
  articleId: string
}>()

const status = ref('')

function getPayload() {
  const el = document.querySelector<HTMLElement>(
    `.gg-copy-payload[data-article-id="${props.articleId}"]`
  )
  if (!el?.textContent) {
    return null
  }
  return JSON.parse(el.textContent) as {
    markdown: string
    text: string
  }
}

function decodeBase64(value: string) {
  const binary = window.atob(value)
  const bytes = Uint8Array.from(binary, (ch) => ch.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

async function writeToClipboard(value: string) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value)
    return
  }

  const textarea = document.createElement('textarea')
  textarea.value = value
  textarea.setAttribute('readonly', 'true')
  textarea.style.position = 'fixed'
  textarea.style.opacity = '0'
  document.body.appendChild(textarea)
  textarea.select()
  document.execCommand('copy')
  document.body.removeChild(textarea)
}

async function copy(kind: 'markdown' | 'text') {
  try {
    const payload = getPayload()
    if (!payload) {
      status.value = '未找到可复制内容'
      return
    }
    const raw = kind === 'markdown' ? payload.markdown : payload.text
    await writeToClipboard(decodeBase64(raw))
    status.value = kind === 'markdown' ? '已复制 Markdown' : '已复制 Text'
    window.setTimeout(() => {
      status.value = ''
    }, 1800)
  } catch (error) {
    console.error(error)
    status.value = '复制失败'
  }
}
</script>

<template>
  <div class="gg-copy-actions">
    <button class="gg-copy-button" type="button" @click="copy('markdown')">复制 Markdown</button>
    <button class="gg-copy-button" type="button" @click="copy('text')">复制 Text</button>
    <span v-if="status" class="gg-copy-status">{{ status }}</span>
  </div>
</template>
