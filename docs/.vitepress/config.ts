import { defineConfig } from 'vitepress'
import katex from '@iktakahiro/markdown-it-katex'
import { siteDescriptionEn, siteDescriptionZh, siteTitleEn, siteTitleZh, viteServerHost, viteServerPort } from './site/meta'
import { navZh } from './site/nav.zh'
import { navEn } from './site/nav.en'
import { sidebarZh } from './site/sidebar.zh'
import { sidebarEn } from './site/sidebar.en'

export default defineConfig({
  base: '/ggmbook/',
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
    footer: {
      message: 'Copyright 2024-2026 乖乖数学团队. All rights reserved.',
      copyright: 'Licensed under MIT License. <a href="/zh/legal">法律声明</a> | <a href="/en/legal">Legal Notice</a>'
    },
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
