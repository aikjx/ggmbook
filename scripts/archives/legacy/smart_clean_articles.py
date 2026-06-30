import os
import re
import codecs

source_dir = r"D:\a10\aikjx\code\my_lib\git\CSDN博文备份"
books_dir = r"D:\a10\aikjx\gitcode\ggbook\docs\books"

categories = {
    'course': ['全域数学vs传统数学', '人类文明进阶200讲', '第1讲', '第2讲', '第3讲', '第4讲', '第5讲', '第6讲', '第7讲', '第8讲', '第9讲', '第10讲', '第11讲', '第12讲', '第13讲', '第14讲', '第15讲', '第16讲', '第17讲', '第18讲', '第19讲', '第20讲', '第21讲', '第22讲', '第23讲', '第24讲', '第25讲', '第26讲', '第27讲', '第28讲', '第29讲'],
    'goldbach': ['哥德巴赫猜想', '孪生素数', '素数', '质数', '数论', '解析数论', '离散几何', '平行素数', '网格理论'],
    'shushu': ['易经', '道德经', '河图洛书', '数术', '八卦', '五行', '太极', '阴阳'],
    'math': ['全域数学', '光速螺旋', '统一场论', '真空介电', '韦伯望远镜', 'ELN', '时空动力学', '引力场', '磁场', '维度压缩', '32维', '超球体', '全息共振', '宇宙观测者']
}

def classify_article(filename):
    lower_name = filename.lower()
    for keyword in categories['course']:
        if keyword.lower() in lower_name:
            return 'course'
    for keyword in categories['goldbach']:
        if keyword.lower() in lower_name:
            return 'goldbach'
    for keyword in categories['shushu']:
        if keyword.lower() in lower_name:
            return 'shushu'
    return 'math'

def detect_encoding(filepath):
    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'utf-16']
    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                content = f.read()
                if '\x00' not in content:
                    return encoding, content
        except:
            continue
    return 'utf-8', ''

def clean_content(content):
    content = re.sub(r'<[^>]+>', '', content)
    
    content = re.sub(r'\\\[', '$$', content)
    content = re.sub(r'\\\]', '$$', content)
    content = re.sub(r'\\\(', '$', content)
    content = re.sub(r'\\\)', '$', content)
    
    content = re.sub(r'&nbsp;', ' ', content)
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r'^\s+|\s+$', '', content)
    
    return content

def copy_and_clean_articles():
    total_count = 0
    category_counts = {'math': 0, 'goldbach': 0, 'shushu': 0, 'course': 0}
    
    for filename in os.listdir(source_dir):
        if filename.endswith('.md'):
            category = classify_article(filename)
            dest_dir = os.path.join(books_dir, category, 'articles')
            os.makedirs(dest_dir, exist_ok=True)
            
            clean_name = re.sub(r'-\d+\.md$', '.md', filename)
            dest_path = os.path.join(dest_dir, clean_name)
            
            source_path = os.path.join(source_dir, filename)
            
            try:
                encoding, content = detect_encoding(source_path)
                if not content:
                    print(f"跳过无法读取的文件: {filename}")
                    continue
                
                cleaned_content = clean_content(content)
                
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(cleaned_content)
                
                category_counts[category] += 1
                total_count += 1
                print(f"复制并清理: {filename} -> {category}/articles/{clean_name}")
            except Exception as e:
                print(f"处理失败 {filename}: {e}")
    
    print(f"\n========== 完成 ==========")
    print(f"总共处理: {total_count} 篇文章")
    for cat, count in category_counts.items():
        print(f"  {cat}: {count} 篇")

if __name__ == '__main__':
    copy_and_clean_articles()
