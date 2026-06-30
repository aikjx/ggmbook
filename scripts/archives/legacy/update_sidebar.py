import os
import json

books_dir = r"D:\a10\aikjx\gitcode\ggbook\docs\books"
config_path = r"D:\a10\aikjx\gitcode\ggbook\docs\.vitepress\config.ts"

def get_articles(category):
    articles_dir = os.path.join(books_dir, category, 'articles')
    articles = []
    if os.path.exists(articles_dir):
        for filename in sorted(os.listdir(articles_dir)):
            if filename.endswith('.md'):
                name = filename[:-3]
                link = f'/books/{category}/articles/{name}'
                articles.append({'text': name, 'link': link})
    return articles

def update_config():
    math_articles = get_articles('math')
    goldbach_articles = get_articles('goldbach')
    shushu_articles = get_articles('shushu')
    course_articles = get_articles('course')
    
    config_content = f'''import {{ defineConfig }} from 'vitepress'

export default defineConfig({{
  title: '全域数学',
  description: '人类全部知识·全域数学统一学习总纲 Ω终版',
  server: {{
    port: 8080,
    host: '0.0.0.0'
  }},
  markdown: {{
    math: 'katex'
  }},
  themeConfig: {{
    nav: [
      {{ text: '首页', link: '/' }},
      {{ text: '书籍列表', link: '/books/' }},
      {{ text: '全域数学', link: '/books/math/' }},
      {{ text: '哥德巴赫猜想', link: '/books/goldbach/' }},
      {{ text: '数术工坊', link: '/books/shushu/' }},
      {{ text: '文明进阶200讲', link: '/books/course/' }}
    ],
    sidebar: {{
      '/books/math/': [
        {{
          text: '核心理论层',
          items: [
            {{ text: '全域数学基础', link: '/books/math/' }},
            {{ text: '0-1-∞三相公理', link: '/books/math/axiom' }},
            {{ text: '全域统一场论', link: '/books/math/unified' }}
          ]
        }},
        {{
          text: '常数本源层',
          items: [
            {{ text: 'π的深度研究', link: '/books/math/pi' }},
            {{ text: '自然常数e', link: '/books/math/e' }},
            {{ text: '虚数i', link: '/books/math/i' }},
            {{ text: '无量纲常数本源', link: '/books/math/dimensionless' }}
          ]
        }},
        {{
          text: '计算实践层',
          items: [
            {{ text: '无穷套娃理论', link: '/books/math/nested' }},
            {{ text: '算子数学', link: '/books/math/operator' }},
            {{ text: '虚数微分方程', link: '/books/math/complex_ode' }}
          ]
        }},
        {{
          text: '密码安全层',
          items: [
            {{ text: '椭圆曲线密码', link: '/books/math/ecc' }},
            {{ text: 'BTC安全研究', link: '/books/math/btc' }},
            {{ text: '量子安全算法', link: '/books/math/quantum' }}
          ]
        }},
        {{
          text: '跨学科应用层',
          items: [
            {{ text: '物理统一场论', link: '/books/math/physics' }},
            {{ text: 'AI意识场理论', link: '/books/math/ai' }},
            {{ text: '信息场禅修体系', link: '/books/math/meditation' }}
          ]
        }},
        {{
          text: '公式典藏层',
          items: [
            {{ text: '本源数学10000条公式', link: '/books/math/formulas' }},
            {{ text: 'Ω体系', link: '/books/math/omega' }},
            {{ text: 'Λ体系', link: '/books/math/lambda' }},
            {{ text: 'Θ体系', link: '/books/math/theta' }}
          ]
        }},
        {{
          text: '精选文章 ({len(math_articles)})',
          items: {json.dumps(math_articles, ensure_ascii=False, indent=6)}
        }}
      ],
      '/books/goldbach/': [
        {{
          text: '哥德巴赫猜想',
          items: [
            {{ text: '猜想概述', link: '/books/goldbach/' }},
            {{ text: '最简本源方程', link: '/books/goldbach/origin' }},
            {{ text: '猜想历史', link: '/books/goldbach/history' }},
            {{ text: '证明进展', link: '/books/goldbach/progress' }},
            {{ text: '孪生素数猜想', link: '/books/goldbach/twin' }},
            {{ text: '强形式克拉梅尔猜想', link: '/books/goldbach/cramer' }},
            {{ text: '相关论文', link: '/books/goldbach/papers' }}
          ]
        }},
        {{
          text: '精选文章 ({len(goldbach_articles)})',
          items: {json.dumps(goldbach_articles, ensure_ascii=False, indent=6)}
        }}
      ],
      '/books/shushu/': [
        {{
          text: '数术工坊八卷全书',
          items: [
            {{ text: '工坊概述', link: '/books/shushu/' }},
            {{ text: '第一卷·泛函套娃录', link: '/books/shushu/vol1' }},
            {{ text: '第二卷·天命赌坊录', link: '/books/shushu/vol2' }},
            {{ text: '第三卷·质数王朝志', link: '/books/shushu/vol3' }},
            {{ text: '第四卷·形变归元录', link: '/books/shushu/vol4' }},
            {{ text: '第五卷·方程兵器谱', link: '/books/shushu/vol5' }},
            {{ text: '第六卷·量天尺传奇', link: '/books/shushu/vol6' }},
            {{ text: '第七卷·流韵万象录', link: '/books/shushu/vol7' }},
            {{ text: '第八卷·大道归一录', link: '/books/shushu/vol8' }},
            {{ text: '易经数理', link: '/books/shushu/yijing' }},
            {{ text: '河图洛书', link: '/books/shushu/hetu' }},
            {{ text: '道德经解析', link: '/books/shushu/daode' }}
          ]
        }},
        {{
          text: '精选文章 ({len(shushu_articles)})',
          items: {json.dumps(shushu_articles, ensure_ascii=False, indent=6)}
        }}
      ],
      '/books/course/': [
        {{
          text: '全域数学vs传统数学：人类文明进阶200讲',
          items: [
            {{ text: '课程概述', link: '/books/course/' }},
            {{ text: '第1-50讲：基础概念', link: '/books/course/part1' }},
            {{ text: '第51-100讲：高中数学', link: '/books/course/part2' }},
            {{ text: '第101-150讲：高等数学', link: '/books/course/part3' }},
            {{ text: '第151-200讲：跨学科应用', link: '/books/course/part4' }},
            {{ text: '第58讲：圆锥曲线', link: '/books/course/lesson58' }}
          ]
        }},
        {{
          text: '精选文章 ({len(course_articles)})',
          items: {json.dumps(course_articles, ensure_ascii=False, indent=6)}
        }}
      ]
    }}
  }}
}})
'''
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print(f"配置文件已更新")
    print(f"math: {len(math_articles)} 篇文章")
    print(f"goldbach: {len(goldbach_articles)} 篇文章")
    print(f"shushu: {len(shushu_articles)} 篇文章")
    print(f"course: {len(course_articles)} 篇文章")

if __name__ == '__main__':
    update_config()
