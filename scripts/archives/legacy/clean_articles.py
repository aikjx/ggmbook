import os
import re

books_dir = r"D:\a10\aikjx\gitcode\ggmbook\docs\books"

def clean_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace('<', '&lt;').replace('>', '&gt;')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def clean_all_articles():
    categories = ['math', 'goldbach', 'shushu', 'course']
    
    for category in categories:
        articles_dir = os.path.join(books_dir, category, 'articles')
        if os.path.exists(articles_dir):
            for filename in os.listdir(articles_dir):
                if filename.endswith('.md'):
                    filepath = os.path.join(articles_dir, filename)
                    try:
                        clean_file(filepath)
                        print(f"清理完成: {category}/articles/{filename}")
                    except Exception as e:
                        print(f"清理失败 {filename}: {e}")

if __name__ == '__main__':
    clean_all_articles()
    print("\n所有文章清理完成！")
