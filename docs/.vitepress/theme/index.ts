import DefaultTheme from 'vitepress/theme'
import ArchiveCopyPanel from './components/ArchiveCopyPanel.vue'
import ArticlePaperMeta from './components/ArticlePaperMeta.vue'
import './style.css'

export default {
  ...DefaultTheme,
  enhanceApp(ctx) {
    DefaultTheme.enhanceApp?.(ctx)
    ctx.app.component('ArchiveCopyPanel', ArchiveCopyPanel)
    ctx.app.component('ArticlePaperMeta', ArticlePaperMeta)
  }
}
