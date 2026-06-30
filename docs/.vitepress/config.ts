import { defineConfig } from 'vitepress'
import katex from '@iktakahiro/markdown-it-katex'
import { siteDescriptionEn, siteDescriptionZh, siteTitleEn, siteTitleZh, viteServerHost, viteServerPort } from './site/meta'
import { navZh } from './site/nav.zh'
import { navEn } from './site/nav.en'
import { sidebarZh } from './site/sidebar.zh'
import { sidebarEn } from './site/sidebar.en'

export default defineConfig({
  title: siteTitleZh,
  description: siteDescriptionZh,
  srcExclude: ['aa/**'],
  ignoreDeadLinks: true,
  vite: {
    server: {
      port: viteServerPort,
      host: viteServerHost
    }
  },
  markdown: {
    config: (md) => {
      md.use(katex, {
        throwOnError: false
      })
    }
  },
  locales: {
    '/': {
      lang: 'zh-CN',
      title: siteTitleZh,
      description: siteDescriptionZh
    },
    '/en/': {
      lang: 'en-US',
      title: siteTitleEn,
      description: siteDescriptionEn
    }
  },
  themeConfig: {
    nav: [
      {
        text: '语言',
        items: [
          { text: '中文', link: '/' },
          { text: 'English', link: '/en/' }
        ]
      }
    ],
    locales: {
      '/': {
        nav: navZh
      },
      '/en/': {
        nav: navEn
      }
    },
    sidebar: {
      ...sidebarZh,
      ...sidebarEn
    }
  }
})
