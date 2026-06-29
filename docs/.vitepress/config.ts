import { defineConfig } from 'vitepress'
import katex from '@iktakahiro/markdown-it-katex'

export default defineConfig({
  title: '乖乖数学《全域数学》',
  description: '《全域数学》作者：乖乖数学',
  srcExclude: ['aa/**'],
  ignoreDeadLinks: true,
  vite: {
    server: {
      port: 8080,
      host: '0.0.0.0'
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
      title: '乖乖数学《全域数学》',
      description: '《全域数学》作者：乖乖数学'
    },
    '/en/': {
      lang: 'en-US',
      title: 'Universal Mathematics',
      description: 'Unified Learning Framework for All Human Knowledge Ω Final Edition'
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
        nav: [
          { text: '首页', link: '/' },
          { text: '书籍', link: '/zh/books/' },
          { text: '全域数学', link: '/zh/books/math/' },
          { text: '哥德巴赫猜想', link: '/zh/books/goldbach/' },
          { text: '数术工坊', link: '/zh/books/shushu/' },
          { text: '文明进阶200讲', link: '/zh/books/course/' },
          { text: 'CSDN博文', link: '/zh/books/articles/' }
        ]
      },
      '/en/': {
        nav: [
          { text: 'Home', link: '/en/' },
          { text: 'Books', link: '/en/books/' },
          { text: 'Universal Math', link: '/en/books/math/' },
          { text: 'Goldbach', link: '/en/books/goldbach/' },
          { text: 'Shushu', link: '/en/books/shushu/' },
          { text: 'Course', link: '/en/books/course/' },
          { text: 'CSDN Blogs', link: '/en/books/articles/' }
        ]
      }
    },
    sidebar: {
      '/zh/books/': [
        {
          text: '全域数学',
          items: [
            { text: '核心理论', link: '/zh/books/math/' },
            { text: '哥德巴赫猜想', link: '/zh/books/goldbach/' },
            { text: '数术工坊', link: '/zh/books/shushu/' },
            { text: '文明进阶200讲', link: '/zh/books/course/' },
            { text: 'CSDN博文', link: '/zh/books/articles/' }
          ]
        }
      ],
      '/en/books/': [
        {
          text: 'Universal Mathematics',
          items: [
            { text: 'Core Theory', link: '/en/books/math/' },
            { text: 'Goldbach Conjecture', link: '/en/books/goldbach/' },
            { text: 'Shushu Workshop', link: '/en/books/shushu/' },
            { text: 'Civilization Course', link: '/en/books/course/' },
            { text: 'CSDN Blogs', link: '/en/books/articles/' }
          ]
        }
      ]
    }
  }
})
