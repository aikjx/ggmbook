from __future__ import annotations

from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re


DOCS_DIR = Path(__file__).resolve().parent.parent
SOURCE_DIR = DOCS_DIR / "aa" / "CSDN博文备份"
ZH_BOOKS_DIR = DOCS_DIR / "zh" / "books"
EN_BOOKS_DIR = DOCS_DIR / "en" / "books"


@dataclass(frozen=True)
class Category:
    key: str
    zh_name: str
    en_name: str
    zh_route: str
    en_route: str
    zh_book_route: str
    en_book_route: str
    zh_description: str
    en_description: str
    keywords: tuple[str, ...]


CATEGORIES = {
    "math": Category(
        key="math",
        zh_name="全域数学",
        en_name="Universal Mathematics",
        zh_route="/zh/books/math/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/math/",
        en_book_route="/en/books/math/",
        zh_description="涵盖全域数学、统一场论、光速螺旋、物理与跨学科延展等内容。",
        en_description="Covers Universal Mathematics, unified field theory, speed-of-light spiral, physics, and cross-disciplinary topics.",
        keywords=(
            "全域数学",
            "统一场论",
            "光速螺旋",
            "vc",
            "引力",
            "电磁",
            "量子",
            "黑洞",
            "拓扑",
            "维度",
            "超球体",
            "人工场",
            "张祥前",
            "场计算机",
            "ai",
            "信息场",
            "经济",
            "金融",
            "密码",
            "哈希",
            "navier-stokes",
            "黎曼",
            "分形",
            "射影",
            "套娃",
            "算子",
            "泛函",
        ),
    ),
    "goldbach": Category(
        key="goldbach",
        zh_name="哥德巴赫猜想",
        en_name="Goldbach Conjecture",
        zh_route="/zh/books/goldbach/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/goldbach/",
        en_book_route="/en/books/goldbach/",
        zh_description="集中收录哥德巴赫猜想、孪生素数、素数网格与数论相关研究。",
        en_description="Collects Goldbach conjecture, twin primes, prime grids, and related number theory research.",
        keywords=(
            "哥德巴赫",
            "孪生素数",
            "素数",
            "质数",
            "数论",
            "解析数论",
            "平行素数",
            "离散解析数论",
        ),
    ),
    "shushu": Category(
        key="shushu",
        zh_name="数术工坊",
        en_name="Shushu Workshop",
        zh_route="/zh/books/shushu/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/shushu/",
        en_book_route="/en/books/shushu/",
        zh_description="收录易经、河图洛书、太极五行、道德经与传统数术方向文章。",
        en_description="Collects articles on Yijing, Hetu-Luoshu, Taiji-Wuxing, Daodejing, and traditional numerology.",
        keywords=(
            "数术",
            "易经",
            "河图洛书",
            "河图",
            "洛书",
            "太极",
            "五行",
            "八卦",
            "阴阳",
            "道德经",
            "佛教",
            "心经",
            "华夏",
        ),
    ),
    "course": Category(
        key="course",
        zh_name="文明进阶200讲",
        en_name="Civilization Course",
        zh_route="/zh/books/course/articles/",
        en_route="/en/books/articles/",
        zh_book_route="/zh/books/course/",
        en_book_route="/en/books/course/",
        zh_description="收录“全域数学 vs 传统数学：人类文明进阶200讲”系列及其通俗课程内容。",
        en_description="Collects the 'Universal Mathematics vs Traditional Mathematics: 200 Lectures' series and related course content.",
        keywords=(
            "全域数学vs传统数学",
            "人类文明进阶200讲",
            "第1讲",
            "第2讲",
            "第3讲",
            "第4讲",
            "第5讲",
            "第6讲",
            "第7讲",
            "第8讲",
            "第9讲",
            "第10讲",
            "第11讲",
            "第12讲",
            "第13讲",
            "第14讲",
            "第15讲",
            "第16讲",
            "第17讲",
            "第18讲",
            "第19讲",
            "第20讲",
            "第21讲",
            "第22讲",
            "第23讲",
            "第24讲",
            "第25讲",
            "第26讲",
            "第27讲",
            "第28讲",
            "第29讲",
            "小学通俗版",
            "初中",
        ),
    ),
}

PRIORITY = {"course": 0, "goldbach": 1, "shushu": 2, "math": 3}
ENCODINGS = ("utf-8", "utf-8-sig", "gbk", "gb2312", "big5", "utf-16")


class MarkdownArchiveParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.list_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = dict(attrs)
        if tag in {"p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"br"}:
            self.parts.append("\n")
        elif tag in {"ul", "ol"}:
            self.parts.append("\n")
            self.list_depth += 1
        elif tag == "li":
            self.parts.append("\n- ")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            level = int(tag[1])
            self.parts.append(f"\n\n{'#' * level} ")
        elif tag == "hr":
            self.parts.append("\n\n---\n\n")
        elif tag == "img":
            src = attrs_dict.get("src") or ""
            alt = attrs_dict.get("alt") or "image"
            if src:
                self.parts.append(f"\n\n![{alt}]({src})\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "section", "article", "blockquote"}:
            self.parts.append("\n\n")
        elif tag in {"ul", "ol"}:
            self.parts.append("\n")
            self.list_depth = max(0, self.list_depth - 1)
        elif tag == "li":
            self.parts.append("\n")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if data:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        self.parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        self.parts.append(unescape(f"&#{name};"))

    def get_markdown(self) -> str:
        return "".join(self.parts)


def read_text(path: Path) -> str:
    for encoding in ENCODINGS:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def extract_article_id(path: Path) -> str:
    match = re.search(r"-(\d+)$", path.stem)
    if match:
        return match.group(1)
    fallback = re.sub(r"[^0-9A-Za-z_-]+", "-", path.stem).strip("-")
    return fallback or "article"


def clean_title(path: Path) -> str:
    title = re.sub(r"-\d+$", "", path.stem)
    title = re.sub(r"\s+", " ", title).strip()
    return title


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def sanitize_content(content: str) -> str:
    parser = MarkdownArchiveParser()
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    try:
        parser.feed(normalized)
        parser.close()
        text = parser.get_markdown()
    except Exception:
        text = normalized

    text = unescape(text)
    filtered_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if re.search(
            r"\\(boldsymbol|frac|dfrac|vec|mathcal|nabla|sum|prod|int|lim|min|max|cdot|to|ge|le|mid|otimes|cong|rho|Omega|partial|sim|ln|pi|infty|text)",
            stripped,
        ):
            continue
        filtered_lines.append(line)
    text = "\n".join(filtered_lines)
    text = text.replace("{", "&#123;").replace("}", "&#125;")
    text = re.sub(r"\n[ \t]+\n", "\n\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def score_category(title: str, sample: str, category: Category) -> int:
    title_lower = title.lower()
    sample_lower = sample.lower()
    score = 0
    for keyword in category.keywords:
        keyword_lower = keyword.lower()
        if keyword_lower in title_lower:
            score += 10
        elif keyword_lower in sample_lower:
            score += 3
    return score


def classify_article(title: str, content: str) -> str:
    sample = content[:4000]
    best_key = "math"
    best_score = -1
    for key, category in CATEGORIES.items():
        score = score_category(title, sample, category)
        if score > best_score:
            best_key = key
            best_score = score
            continue
        if score == best_score and PRIORITY[key] < PRIORITY[best_key]:
            best_key = key
    return best_key if best_score > 0 else "math"


def render_article_page(category: Category, article_id: str, original_name: str, title: str, content: str) -> str:
    return (
        "---\n"
        f"title: {yaml_quote(title)}\n"
        "---\n\n"
        f"> 分类：{category.zh_name}  \n"
        f"> 编号：`{article_id}`  \n"
        f"> 原始文件：`{original_name}`  \n"
        f"> 返回：[本书归档]({category.zh_route}) · [总入口](/zh/books/articles/)\n\n"
        f"{content.strip()}\n"
    )


def render_category_index(category: Category, articles: list[dict[str, str]]) -> str:
    lines = [
        f"# {category.zh_name}博文归档",
        "",
        f"已从 `docs/aa/CSDN博文备份` 自动分类收录，共 **{len(articles)}** 篇。",
        "",
        f"- [返回本书首页]({category.zh_book_route})",
        "- [返回总入口](/zh/books/articles/)",
        "",
        "## 说明",
        "",
        f"- {category.zh_description}",
        "- 文件按原始标题自动分类，正文保留原始 Markdown/HTML 内容，适合站内在线阅读。",
        "",
        "## 文章列表",
        "",
    ]
    for article in articles:
        lines.append(f"- [{article['title']}]({category.zh_route}{article['id']})")
    lines.append("")
    return "\n".join(lines)


def render_overview_zh(grouped: dict[str, list[dict[str, str]]], recent_articles: list[dict[str, str]]) -> str:
    total = sum(len(items) for items in grouped.values())
    lines = [
        "# CSDN博文归档",
        "",
        "已将 `docs/aa/CSDN博文备份` 自动分析并分流到不同书籍目录，可在站点内直接阅读。",
        "",
        "## 分类入口",
        "",
        "| 书籍 | 文章数 | 入口 |",
        "| --- | ---: | --- |",
    ]
    for key in ("math", "goldbach", "shushu", "course"):
        category = CATEGORIES[key]
        lines.append(f"| {category.zh_name} | {len(grouped[key])} | [进入归档]({category.zh_route}) |")
    lines.extend(
        [
            f"| **总计** | **{total}** | - |",
            "",
            "## 最新收录",
            "",
        ]
    )
    for article in recent_articles:
        lines.append(f"- [{article['title']}]({article['route']}) · {article['category_name']}")
    lines.extend(
        [
            "",
            "## 分类说明",
            "",
            "- 文明进阶200讲：优先识别“全域数学vs传统数学”“人类文明进阶200讲”“第X讲”等课程特征。",
            "- 哥德巴赫猜想：识别哥德巴赫、孪生素数、素数、质数、数论等关键词。",
            "- 数术工坊：识别易经、河图洛书、太极、五行、道德经、佛教等传统数术关键词。",
            "- 其余默认归入全域数学。",
            "",
        ]
    )
    return "\n".join(lines)


def render_overview_en(grouped: dict[str, list[dict[str, str]]]) -> str:
    total = sum(len(items) for items in grouped.values())
    lines = [
        "# CSDN Blog Archive",
        "",
        "The articles from `docs/aa/CSDN博文备份` are automatically classified into book-specific Chinese archives for online reading.",
        "",
        "## Archive Entry Points",
        "",
        "| Book | Articles | Archive |",
        "| --- | ---: | --- |",
    ]
    for key in ("math", "goldbach", "shushu", "course"):
        category = CATEGORIES[key]
        lines.append(f"| {category.en_name} | {len(grouped[key])} | [Open Chinese Archive]({category.zh_route}) |")
    lines.extend(
        [
            f"| **Total** | **{total}** | - |",
            "",
            "## Notes",
            "",
            "- These archived posts are Chinese-language originals from the CSDN backup directory.",
            "- Classification is based on filename and article content keywords.",
            "- Use the links above to browse the book-specific archives directly.",
            "",
        ]
    )
    return "\n".join(lines)


def ensure_clean_archive_dirs() -> None:
    for key in CATEGORIES:
        archive_dir = ZH_BOOKS_DIR / key / "articles"
        if archive_dir.exists():
            for file_path in archive_dir.glob("*.md"):
                file_path.unlink()
        archive_dir.mkdir(parents=True, exist_ok=True)


def build_archives() -> None:
    ensure_clean_archive_dirs()
    source_files = sorted(SOURCE_DIR.glob("*.md"))
    grouped: dict[str, list[dict[str, str]]] = {key: [] for key in CATEGORIES}

    for path in source_files:
        title = clean_title(path)
        raw_content = read_text(path).strip()
        content = sanitize_content(raw_content)
        category_key = classify_article(title, content)
        category = CATEGORIES[category_key]
        article_id = extract_article_id(path)
        target_path = ZH_BOOKS_DIR / category_key / "articles" / f"{article_id}.md"
        target_path.write_text(
            render_article_page(category, article_id, path.name, title, content),
            encoding="utf-8",
        )
        grouped[category_key].append(
            {
                "id": article_id,
                "title": title,
                "route": f"{category.zh_route}{article_id}",
                "category_name": category.zh_name,
            }
        )

    for key, articles in grouped.items():
        articles.sort(key=lambda item: int(item["id"]) if item["id"].isdigit() else 0, reverse=True)
        index_path = ZH_BOOKS_DIR / key / "articles" / "index.md"
        index_path.write_text(render_category_index(CATEGORIES[key], articles), encoding="utf-8")

    recent_articles: list[dict[str, str]] = []
    for items in grouped.values():
        recent_articles.extend(items)
    recent_articles.sort(key=lambda item: int(item["id"]) if item["id"].isdigit() else 0, reverse=True)

    (ZH_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (EN_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (ZH_BOOKS_DIR / "articles" / "index.md").write_text(
        render_overview_zh(grouped, recent_articles[:20]),
        encoding="utf-8",
    )
    (EN_BOOKS_DIR / "articles" / "index.md").write_text(
        render_overview_en(grouped),
        encoding="utf-8",
    )

    total = sum(len(items) for items in grouped.values())
    print(f"已生成 {total} 篇归档文章")
    for key in ("math", "goldbach", "shushu", "course"):
        print(f"  {key}: {len(grouped[key])} 篇")


if __name__ == "__main__":
    build_archives()
