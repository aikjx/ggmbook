<script setup lang="ts">
const props = defineProps<{
  category: string
  articleId: string
  title: string
  paperKind: string
  summary?: string
  author?: string
  lecture?: string
  theme?: string
  series?: string
  created?: string
  contrast?: string
  tone?: string
  sourceFile?: string
  cover?: string
  bookRoute: string
  overviewRoute: string
}>()

function buildMetaRows() {
  return [
    { label: '作者', value: props.author },
    { label: '讲次', value: props.lecture },
    { label: '主题', value: props.theme },
    { label: '体系归属', value: props.series },
    { label: '成书日期', value: props.created },
    { label: '对标传统数学', value: props.contrast },
    { label: '授课调性', value: props.tone },
    { label: '原始文件', value: props.sourceFile }
  ].filter((item) => item.value)
}
</script>

<template>
  <section class="gg-paper-meta-panel">
    <div class="gg-paper-meta-main">
      <div class="gg-chip-row gg-paper-meta-chips">
        <span class="gg-chip">{{ category }}</span>
        <span class="gg-chip">{{ paperKind }}</span>
        <span class="gg-chip">编号 {{ articleId }}</span>
      </div>
      <h1 class="gg-paper-meta-title">{{ title }}</h1>
      <p v-if="summary" class="gg-paper-meta-summary">{{ summary }}</p>

      <div class="gg-paper-meta-grid">
        <div v-for="item in buildMetaRows()" :key="item.label" class="gg-paper-meta-item">
          <span class="gg-paper-meta-label">{{ item.label }}</span>
          <strong class="gg-paper-meta-value">{{ item.value }}</strong>
        </div>
      </div>

      <div class="gg-course-actions gg-paper-meta-actions">
        <a class="gg-action-button" :href="bookRoute">返回本书归档</a>
        <a class="gg-action-button is-secondary" :href="overviewRoute">返回总入口</a>
      </div>
    </div>

    <div v-if="cover" class="gg-paper-cover">
      <img :src="cover" :alt="title" />
    </div>
  </section>
</template>
