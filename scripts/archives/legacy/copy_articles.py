import os
import shutil
import re

# 源目录
source_dir = r"D:\a10\aikjx\code\my_lib\git\CSDN博文备份"
# 目标目录
target_dir = r"D:\a10\aikjx\gitcode\ggbook\docs\books"

# 分类规则
categories = {
    'course': [
        '全域数学vs传统数学',
        '人类文明进阶200讲',
        '第1讲', '第2讲', '第3讲', '第4讲', '第5讲',
        '第6讲', '第7讲', '第8讲', '第9讲', '第10讲',
        '第18讲', '第22讲', '第13讲', '第14讲', '小学通俗版'
    ],
    'goldbach': [
        '哥德巴赫猜想',
        '孪生素数',
        '素数',
        '克拉梅尔',
        '数论',
        '质数'
    ],
    'shushu': [
        '易经',
        '道德经',
        '河图洛书',
        '数术',
        '太极',
        '五行',
        '禅修',
        '心经',
        '佛教'
    ],
    'math': [
        '全域数学',
        '光速螺旋',
        '统一场论',
        'vc公理',
        '0-1-∞',
        '三元公理',
        '万物理论',
        '黎曼',
        '纳维-斯托克斯',
        '精细结构常数',
        '暗物质',
        '黑洞',
        '量子',
        '引力',
        '电磁',
        '光子',
        '人工场',
        '张祥前',
        '32维',
        '超球体',
        '几何化',
        '套娃',
        '算子',
        '泛函',
        '拓扑',
        '射影',
        '分形',
        '维度',
        '网格',
        '平行',
        '对称',
        '不动点',
        '螺旋',
        '曲率',
        '挠率',
        '场计算机',
        'AGI',
        'AI',
        '信息场',
        '精算',
        '经济',
        '金融',
        '密码',
        '破解',
        '量子安全',
        '椭圆曲线',
        'BTC',
        '哈希'
    ]
}

def sanitize_filename(filename):
    """清理文件名中的特殊字符"""
    # 移除或替换特殊字符
    filename = re.sub(r'[\\/*?:"<>|]', '', filename)
    # 移除末尾的数字和连字符
    filename = re.sub(r'-\d+\.md$', '.md', filename)
    return filename

def classify_article(filename):
    """根据文件名分类文章"""
    lower_name = filename.lower()
    
    # 优先匹配课程类（200讲）
    for keyword in categories['course']:
        if keyword.lower() in lower_name:
            return 'course'
    
    # 匹配哥德巴赫猜想类
    for keyword in categories['goldbach']:
        if keyword.lower() in lower_name:
            return 'goldbach'
    
    # 匹配数术工坊类
    for keyword in categories['shushu']:
        if keyword.lower() in lower_name:
            return 'shushu'
    
    # 默认归类到全域数学
    return 'math'

def copy_and_classify():
    """复制并分类所有文章"""
    # 确保目标目录存在
    for category in categories.keys():
        cat_dir = os.path.join(target_dir, category, 'articles')
        os.makedirs(cat_dir, exist_ok=True)
    
    # 遍历源目录
    files = [f for f in os.listdir(source_dir) if f.endswith('.md') and not f.startswith('.')]
    
    print(f"发现 {len(files)} 篇文章")
    
    for filename in files:
        # 分类文章
        category = classify_article(filename)
        
        # 清理文件名
        new_filename = sanitize_filename(filename)
        
        # 构建路径
        source_path = os.path.join(source_dir, filename)
        target_path = os.path.join(target_dir, category, 'articles', new_filename)
        
        # 复制文件
        try:
            shutil.copy2(source_path, target_path)
            print(f"复制: {filename} -> {category}/articles/{new_filename}")
        except Exception as e:
            print(f"复制失败 {filename}: {e}")
    
    print("\n分类完成！")

if __name__ == '__main__':
    copy_and_classify()