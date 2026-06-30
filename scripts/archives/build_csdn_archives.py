from __future__ import annotations

from dataclasses import dataclass
import base64
from html import escape, unescape
from html.parser import HTMLParser
import argparse
import hashlib
import json
import mimetypes
from pathlib import Path
import re
import shutil
import time
from urllib.error import URLError, HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = REPO_ROOT / "docs"
SOURCE_DIR = DOCS_DIR / "aa" / "CSDN博文备份"
ZH_BOOKS_DIR = DOCS_DIR / "zh" / "books"
EN_BOOKS_DIR = DOCS_DIR / "en" / "books"
LOG_PATH = REPO_ROOT / "tmp" / "archive_build.log"

DEFAULT_TIMEOUT_SEC = 20
DEFAULT_RETRIES = 2
DEFAULT_USER_AGENT = "ggbook-archive-bot/1.0"


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
            "第30讲",
            "第31讲",
            "第32讲",
            "第33讲",
            "第34讲",
            "第35讲",
            "第36讲",
            "第37讲",
            "第38讲",
            "第39讲",
            "第40讲",
            "第41讲",
            "第42讲",
            "第43讲",
            "第44讲",
            "第45讲",
            "第46讲",
            "第47讲",
            "第48讲",
            "第49讲",
            "第50讲",
            "小学通俗版",
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


def normalize_http_url(url: str) -> str:
    url = url.strip()
    if url.startswith("//"):
        return "https:" + url
    if url.startswith("http://"):
        return "https://" + url[len("http://") :]
    return url


def is_http_url(url: str) -> bool:
    return url.startswith("http://") or url.startswith("https://") or url.startswith("//")


def classify_image_host(url: str) -> str:
    parsed = urlparse(normalize_http_url(url))
    netloc = (parsed.netloc or "").lower()
    if "csdnimg" in netloc or netloc.endswith("csdn.net") or "csdn" in netloc:
        return "csdnimg"
    return "external"


def guess_extension(url: str, content_type: str | None) -> str:
    parsed = urlparse(normalize_http_url(url))
    path = parsed.path or ""
    match = re.search(r"\.([A-Za-z0-9]{1,5})$", path)
    if match:
        ext = "." + match.group(1).lower()
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            return ".jpg" if ext == ".jpeg" else ext

    if content_type:
        mime = content_type.split(";")[0].strip().lower()
        ext = mimetypes.guess_extension(mime) or ""
        if ext in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}:
            return ".jpg" if ext == ".jpeg" else ext

    return ".png"


def safe_write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_bytes(data)
    tmp_path.replace(path)


def log_line(message: str) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fp:
        fp.write(message.rstrip() + "\n")


def fetch_image_bytes(url: str, *, timeout_sec: int, retries: int) -> tuple[bytes | None, str | None]:
    url = normalize_http_url(url)
    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = Request(url, headers={"User-Agent": DEFAULT_USER_AGENT})
            with urlopen(req, timeout=timeout_sec) as resp:
                data = resp.read()
                content_type = resp.headers.get("Content-Type")
                if not data:
                    return None, content_type
                return data, content_type
        except (HTTPError, URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            time.sleep(0.6 * (attempt + 1))
    if last_error:
        print(f"图片拉取失败: {url} ({type(last_error).__name__})")
    return None, None


def download_image(url: str, dest_path: Path, *, timeout_sec: int, retries: int) -> bool:
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return True
    data, _ = fetch_image_bytes(url, timeout_sec=timeout_sec, retries=retries)
    if not data:
        return False
    safe_write_bytes(dest_path, data)
    return True


def parse_markdown_image_url(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        raw = raw[1:-1].strip()
    raw = raw.strip('"').strip("'")
    parts = raw.split()
    return parts[0] if parts else raw


def localize_images_in_markdown(
    content: str,
    assets_root: Path,
    *,
    download: bool,
    timeout_sec: int,
    retries: int,
) -> tuple[str, int, int]:
    md_image_pattern = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    html_img_pattern = re.compile(r"(<img[^>]*?\ssrc=)(['\"])([^'\"]+)(\2)", re.IGNORECASE)
    md_ref_pattern = re.compile(r"(^\s*\[[^\]]+\]:\s*)(\S+)(.*$)", re.MULTILINE)
    url_map: dict[str, str] = {}
    downloaded_count = 0
    total_count = 0

    def build_local_ref(norm_url: str, *, prefer_content_type: str | None) -> str:
        nonlocal downloaded_count, total_count
        total_count += 1
        if not download:
            return norm_url

        data, content_type = fetch_image_bytes(norm_url, timeout_sec=timeout_sec, retries=retries)
        if not data:
            return norm_url

        host_group = classify_image_host(norm_url)
        ext = guess_extension(norm_url, content_type or prefer_content_type)
        ext_dir = ext.lstrip(".") or "bin"
        digest = hashlib.sha1(norm_url.encode("utf-8")).hexdigest()[:16]
        filename = f"{digest}{ext}"
        host_dir = assets_root / host_group / ext_dir
        host_dir.mkdir(parents=True, exist_ok=True)
        safe_write_bytes(host_dir / filename, data)
        downloaded_count += 1
        return f"./assets/{host_group}/{ext_dir}/{filename}"

    def get_rewritten_url(url: str) -> str:
        if not is_http_url(url):
            return url
        norm_url = normalize_http_url(url)
        if norm_url not in url_map:
            url_map[norm_url] = build_local_ref(norm_url, prefer_content_type=None)
        return url_map[norm_url]

    def replace_md_image(match: re.Match[str]) -> str:
        nonlocal downloaded_count, total_count
        alt_text = match.group(1)
        raw_target = match.group(2)
        url = parse_markdown_image_url(raw_target)
        rewritten_url = get_rewritten_url(url)
        if rewritten_url == url:
            return match.group(0)
        return f"![{alt_text}]({rewritten_url})"

    def replace_html_img(match: re.Match[str]) -> str:
        prefix = match.group(1)
        quote = match.group(2)
        src = match.group(3)
        suffix_quote = match.group(4)
        rewritten_url = get_rewritten_url(src)
        return f"{prefix}{quote}{rewritten_url}{suffix_quote}"

    def replace_md_ref(match: re.Match[str]) -> str:
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        rewritten_url = get_rewritten_url(url)
        return f"{prefix}{rewritten_url}{suffix}"

    rewritten = md_image_pattern.sub(replace_md_image, content)
    rewritten = html_img_pattern.sub(replace_html_img, rewritten)
    rewritten = md_ref_pattern.sub(replace_md_ref, rewritten)
    return rewritten, downloaded_count, total_count


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


def markdown_to_plain_text(content: str) -> str:
    text = content.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^>\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"```[\w-]*\n", "", text)
    text = text.replace("```", "")
    text = text.replace("**", "").replace("__", "").replace("*", "").replace("_", "")
    text = text.replace("$$", "").replace("$", "")
    text = re.sub(r"<[^>]+>", "", text)
    text = unescape(text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def encode_copy_payload(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


META_LABELS = (
    "作者",
    "讲次",
    "主题",
    "对标传统数学",
    "授课调性",
    "成书日期",
    "体系归属",
)


def html_attr(value: str | None) -> str:
    return escape(value or "", quote=True)


def extract_prefixed_value(content: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}[：:]\s*(.+)$", content, flags=re.MULTILINE)
    if not match:
        return ""
    return match.group(1).strip()


def extract_first_image(content: str) -> str:
    markdown_match = re.search(r"!\[[^\]]*\]\(([^)]+)\)", content)
    if markdown_match:
        return markdown_match.group(1).strip()
    html_match = re.search(r"<img[^>]*\ssrc=['\"]([^'\"]+)['\"]", content, flags=re.IGNORECASE)
    if html_match:
        return html_match.group(1).strip()
    return ""


def extract_summary(content: str) -> str:
    for block in re.split(r"\n\s*\n", content):
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("!"):
            continue
        if stripped.startswith("---"):
            continue
        if stripped.startswith("#"):
            continue
        plain = markdown_to_plain_text(stripped)
        if not plain:
            continue
        if any(plain.startswith(f"{label}：") or plain.startswith(f"{label}:") for label in META_LABELS):
            continue
        if plain.startswith("返回：") or plain.startswith("分类：") or plain.startswith("编号：") or plain.startswith("原始文件："):
            continue
        if len(plain) < 16:
            continue
        return plain[:140].rstrip() + ("..." if len(plain) > 140 else "")
    return ""


def build_article_meta(category: Category, article_id: str, original_name: str, title: str, content: str) -> dict[str, str]:
    lecture = extract_prefixed_value(content, "讲次")
    theme = extract_prefixed_value(content, "主题")
    series = extract_prefixed_value(content, "体系归属")
    created = extract_prefixed_value(content, "成书日期")
    contrast = extract_prefixed_value(content, "对标传统数学")
    tone = extract_prefixed_value(content, "授课调性")
    summary = extract_summary(content) or theme or series or category.zh_description
    if category.key == "course":
        paper_kind = "课程讲义"
    elif category.key == "shushu":
        paper_kind = "专题文稿"
    else:
        paper_kind = "研究论文"
    return {
        "category": category.zh_name,
        "article_id": article_id,
        "title": title,
        "paper_kind": paper_kind,
        "author": extract_prefixed_value(content, "作者") or "乖乖数学",
        "lecture": lecture,
        "theme": theme,
        "series": series,
        "created": created,
        "contrast": contrast,
        "tone": tone,
        "summary": summary,
        "source_file": original_name,
        "cover": extract_first_image(content),
        "book_route": category.zh_route,
        "overview_route": "/zh/books/articles/",
    }


def render_article_meta_component(meta: dict[str, str]) -> str:
    attrs = [
        f'category="{html_attr(meta["category"])}"',
        f'article-id="{html_attr(meta["article_id"])}"',
        f'title="{html_attr(meta["title"])}"',
        f'paper-kind="{html_attr(meta["paper_kind"])}"',
        f'book-route="{html_attr(meta["book_route"])}"',
        f'overview-route="{html_attr(meta["overview_route"])}"',
    ]
    optional_mapping = {
        "summary": "summary",
        "author": "author",
        "lecture": "lecture",
        "theme": "theme",
        "series": "series",
        "created": "created",
        "contrast": "contrast",
        "tone": "tone",
        "source_file": "source-file",
        "cover": "cover",
    }
    for key, prop_name in optional_mapping.items():
        if meta.get(key):
            attrs.append(f'{prop_name}="{html_attr(meta[key])}"')
    return f"<ArticlePaperMeta {' '.join(attrs)} />"


def render_article_body(category: Category, article_id: str, original_name: str, content: str) -> str:
    return (
        f"> 分类：{category.zh_name}  \n"
        f"> 编号：`{article_id}`  \n"
        f"> 原始文件：`{original_name}`  \n"
        f"> 返回：[本书归档]({category.zh_route}) · [总入口](/zh/books/articles/)\n\n"
        f"{content.strip()}\n"
    )


def render_article_page(category: Category, article_id: str, original_name: str, title: str, content: str) -> str:
    meta = build_article_meta(category, article_id, original_name, title, content)
    article_body = render_article_body(category, article_id, original_name, content)
    payload = json.dumps(
        {
            "markdown": encode_copy_payload(article_body),
            "text": encode_copy_payload(markdown_to_plain_text(article_body)),
        },
        separators=(",", ":"),
    )
    frontmatter_lines = [
        "---",
        f"title: {yaml_quote(title)}",
        f"description: {yaml_quote(meta['summary'])}",
        f"author: {yaml_quote(meta['author'])}",
        f"category: {yaml_quote(meta['category'])}",
        f"paperKind: {yaml_quote(meta['paper_kind'])}",
        f"articleId: {yaml_quote(article_id)}",
        f"sourceFile: {yaml_quote(original_name)}",
    ]
    if meta["lecture"]:
        frontmatter_lines.append(f"lecture: {yaml_quote(meta['lecture'])}")
    if meta["theme"]:
        frontmatter_lines.append(f"theme: {yaml_quote(meta['theme'])}")
    if meta["series"]:
        frontmatter_lines.append(f"series: {yaml_quote(meta['series'])}")
    if meta["created"]:
        frontmatter_lines.append(f"created: {yaml_quote(meta['created'])}")
    frontmatter_lines.extend(["---", ""])
    meta_component = render_article_meta_component(meta)
    return (
        "\n".join(frontmatter_lines)
        + f"<ArchiveCopyPanel article-id=\"{article_id}\" />\n"
        + f"<div class=\"gg-copy-payload\" data-article-id=\"{article_id}\">{payload}</div>\n\n"
        + "> 分类："
        + f"{category.zh_name}  \n"
        + f"> 编号：`{article_id}`  \n"
        + f"> 原始文件：`{original_name}`  \n"
        + f"> 返回：[本书归档]({category.zh_route}) · [总入口](/zh/books/articles/)\n\n"
        + meta_component
        + "\n\n"
        + f"{content.strip()}\n"
    )


def short_course_title(title: str) -> str:
    short = re.sub(r"[-\s]*全域数学\s*vs\s*传统数学.*$", "", title, flags=re.IGNORECASE)
    short = re.sub(r"[-\s]*全域数学vs传统数学.*$", "", short, flags=re.IGNORECASE)
    short = re.sub(r"[-\s]*人类文明进阶200讲.*$", "", short)
    short = re.sub(r"[-\s]*第\s*\d{1,3}\s*讲.*$", "", short)
    short = short.strip(" -_")
    return short or title


def render_course_category_index(category: Category, articles: list[dict[str, str]]) -> str:
    lecture_map = {article["lecture"]: article for article in articles if article.get("lecture") is not None}
    max_lecture = max(max(lecture_map) if lecture_map else 0, 50)
    missing_lectures = [lecture for lecture in range(1, max_lecture + 1) if lecture not in lecture_map]

    lines = [
        f"# {category.zh_name}博文归档",
        "",
        '<div class="gg-course-hero">',
        '  <p class="gg-kicker">课程归档总目录</p>',
        f'  <h2 class="gg-course-hero-title">{category.zh_name}</h2>',
        '  <p class="gg-course-hero-text">按讲次整理成分段目录，适合从首页快速进入具体文章阅读。</p>',
        '  <div class="gg-stat-grid">',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">已上线文章</span><strong class="gg-stat-value">{len(articles)}</strong></div>',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">当前整理范围</span><strong class="gg-stat-value">第1-{max_lecture}讲</strong></div>',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">待补章节</span><strong class="gg-stat-value">{("第" + "、第".join(str(item) for item in missing_lectures) + "讲") if missing_lectures else "已完整"}</strong></div>',
        "  </div>",
        '  <div class="gg-course-actions">',
        f'    <a class="gg-action-button" href="{category.zh_book_route}">返回课程首页</a>',
        '    <a class="gg-action-button is-secondary" href="/zh/books/articles/">返回总入口</a>',
        "  </div>",
        "</div>",
        "",
        "## 分段速览",
        "",
        '<div class="gg-chip-row">',
    ]

    for start in range(1, max_lecture + 1, 10):
        end = min(start + 9, max_lecture)
        lines.append(f'  <a class="gg-chip" href="#lecture-{start:03d}-{end:03d}">第{start}-{end}讲</a>')

    lines.extend(
        [
            "</div>",
            "",
            "## 快速进入",
            "",
        ]
    )

    for start in range(1, max_lecture + 1, 10):
        end = min(start + 9, max_lecture)
        available = [lecture for lecture in range(start, end + 1) if lecture in lecture_map]
        missing = [lecture for lecture in range(start, end + 1) if lecture not in lecture_map]
        lines.extend(
            [
                f'<section class="gg-lecture-section" id="lecture-{start:03d}-{end:03d}">',
                '  <div class="gg-lecture-head">',
                f'    <div><h2>第{start}-{end}讲</h2><p>适合按章节顺序连续阅读。</p></div>',
                f'    <div class="gg-lecture-summary">已上线 {len(available)} / {end - start + 1}</div>',
                "  </div>",
            ]
        )

        if missing:
            lines.append(
                f'  <p class="gg-lecture-missing">待补：{"、".join(f"第{lecture}讲" for lecture in missing)}</p>'
            )

        lines.append('  <div class="gg-lecture-grid">')
        for lecture in range(start, end + 1):
            article = lecture_map.get(lecture)
            if article is None:
                lines.extend(
                    [
                        '    <div class="gg-lecture-card is-missing">',
                        f'      <span class="gg-lecture-badge">第{lecture}讲</span>',
                        '      <strong>待补充</strong>',
                        '      <span class="gg-lecture-note">当前还没有对应文章</span>',
                        "    </div>",
                    ]
                )
                continue
            title = short_course_title(article["title"])
            lines.extend(
                [
                    f'    <a class="gg-lecture-card" href="{category.zh_route}{article["id"]}/">',
                    f'      <span class="gg-lecture-badge">第{lecture}讲</span>',
                    f"      <strong>{escape(title)}</strong>",
                    '      <span class="gg-lecture-note">点击进入文章</span>',
                    "    </a>",
                ]
            )
        lines.extend(["  </div>", "</section>", ""])

    return "\n".join(lines)


def render_paper_card(article: dict[str, str], *, note: str = "点击进入文章") -> list[str]:
    badges = [
        f'      <span class="gg-paper-badge">{escape(article.get("paper_kind") or article.get("category_name") or "文章")}</span>',
        f'      <span class="gg-paper-badge">#{escape(article["id"])}</span>',
    ]
    if article.get("lecture_text"):
        badges.insert(0, f'      <span class="gg-paper-badge">{escape(article["lecture_text"])}</span>')
    meta_chips: list[str] = []
    if article.get("author"):
        meta_chips.append(f'      <span class="gg-paper-meta-chip">{escape(article["author"])}</span>')
    if article.get("series"):
        meta_chips.append(f'      <span class="gg-paper-meta-chip">{escape(article["series"])}</span>')
    elif article.get("category_name"):
        meta_chips.append(f'      <span class="gg-paper-meta-chip">{escape(article["category_name"])}</span>')
    lines = [
        f'  <a class="gg-paper-card" href="{article["route"]}">',
        '    <div class="gg-paper-card-header">',
        *badges,
        "    </div>",
        f'    <h3>{escape(article["title"])}</h3>',
        f'    <p>{escape(article.get("summary") or note)}</p>',
    ]
    if meta_chips:
        lines.extend(['    <div class="gg-paper-card-meta">', *meta_chips, "    </div>"])
    lines.append("  </a>")
    return lines


def render_category_index(category: Category, articles: list[dict[str, str]]) -> str:
    if category.key == "course":
        return render_course_category_index(category, articles)
    latest_id = articles[0]["id"] if articles else "暂无"
    lines = [
        f"# {category.zh_name}博文归档",
        "",
        '<div class="gg-course-hero">',
        '  <p class="gg-kicker">专题文章与论文归档</p>',
        f'  <h2 class="gg-course-hero-title">{category.zh_name}</h2>',
        f'  <p class="gg-course-hero-text">{category.zh_description}</p>',
        '  <div class="gg-stat-grid">',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">已上线文章</span><strong class="gg-stat-value">{len(articles)} 篇</strong></div>',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">展示类型</span><strong class="gg-stat-value">论文 / 文稿 / 归档</strong></div>',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">最新编号</span><strong class="gg-stat-value">{latest_id}</strong></div>',
        "  </div>",
        '  <div class="gg-course-actions">',
        f'    <a class="gg-action-button" href="{category.zh_book_route}">返回本书首页</a>',
        '    <a class="gg-action-button is-secondary" href="/zh/books/articles/">返回总入口</a>',
        "  </div>",
        "</div>",
        "",
        '## 文章论文展示',
        "",
    ]
    if articles:
        lines.extend(
            [
                '<div class="gg-paper-section">',
                '  <div class="gg-paper-section-head">',
                f'    <div><h2>{category.zh_name}最新内容</h2><p>统一按企业级卡片方式展示文章、论文与专题文稿。</p></div>',
                f'    <div class="gg-paper-section-note">共 {len(articles)} 篇</div>',
                "  </div>",
                '  <div class="gg-paper-grid">',
            ]
        )
        for article in articles:
            lines.extend(render_paper_card(article))
        lines.extend(["  </div>", "</div>", ""])
    else:
        lines.extend(
            [
                '<div class="gg-note-panel">',
                '  <strong>当前暂无已接入文章</strong>',
                f'  <p>{category.zh_name} 频道已完成归档入口建设，后续接入文章后会自动按论文卡片形式展示。</p>',
                "</div>",
                "",
            ]
        )
    lines.extend(
        [
            "## 归档说明",
            "",
            f"- {category.zh_description}",
            "- 文章页统一提供复制、元信息、归档来源和返回链路。",
            "- 新增归档内容后，执行标准化重建命令即可自动更新当前目录页。",
            "",
        ]
    )
    return "\n".join(lines)


def render_overview_zh(grouped: dict[str, list[dict[str, str]]], recent_articles: list[dict[str, str]]) -> str:
    total = sum(len(items) for items in grouped.values())
    active_categories = sum(1 for items in grouped.values() if items)
    lines = [
        "# CSDN博文归档",
        "",
        '<div class="gg-course-hero">',
        '  <p class="gg-kicker">总站归档入口</p>',
        '  <h2 class="gg-course-hero-title">文章 / 论文 / 课程归档总览</h2>',
        '  <p class="gg-course-hero-text">统一承载四大书籍的文章、课程讲义、研究论文与专题文稿，按分类入口和最新收录双维展示。</p>',
        '  <div class="gg-stat-grid">',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">归档总数</span><strong class="gg-stat-value">{total} 篇</strong></div>',
        f'    <div class="gg-stat-card"><span class="gg-stat-label">活跃书籍</span><strong class="gg-stat-value">{active_categories} / 4</strong></div>',
        '    <div class="gg-stat-card"><span class="gg-stat-label">展示方式</span><strong class="gg-stat-value">书籍入口 + 文章卡片</strong></div>',
        "  </div>",
        '  <div class="gg-course-actions">',
        '    <a class="gg-action-button" href="/zh/books/">返回书籍总览</a>',
        '    <a class="gg-action-button is-secondary" href="/zh/books/course/">进入课程总入口</a>',
        "  </div>",
        "</div>",
        "",
        "## 分类入口",
        "",
        '<div class="gg-paper-grid">',
    ]
    for key in ("math", "goldbach", "shushu", "course"):
        category = CATEGORIES[key]
        count = len(grouped[key])
        lines.extend(
            [
                f'  <a class="gg-paper-card" href="{category.zh_route}">',
                '    <div class="gg-paper-card-header">',
                f'      <span class="gg-paper-badge">{category.zh_name}</span>',
                f'      <span class="gg-paper-badge">{count} 篇</span>',
                "    </div>",
                f'    <h3>{category.zh_name}</h3>',
                f'    <p>{category.zh_description}</p>',
                '    <div class="gg-paper-card-meta">',
                '      <span class="gg-paper-meta-chip">专题归档</span>',
                '      <span class="gg-paper-meta-chip">在线阅读</span>',
                "    </div>",
                "  </a>",
            ]
        )
    lines.extend(
        [
            "</div>",
            "",
            "## 最新收录",
            "",
        ]
    )
    for article in recent_articles:
        if len(lines) == 0:
            pass
    lines.append('<div class="gg-paper-grid">')
    for article in recent_articles:
        lines.extend(render_paper_card(article, note="查看最新归档内容"))
    lines.extend(
        [
            "</div>",
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


def ensure_archive_dirs(*, purge: bool) -> None:
    for key in CATEGORIES:
        archive_dir = ZH_BOOKS_DIR / key / "articles"
        if purge and archive_dir.exists():
            for child in archive_dir.iterdir():
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
        archive_dir.mkdir(parents=True, exist_ok=True)

    (ZH_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)
    (EN_BOOKS_DIR / "articles").mkdir(parents=True, exist_ok=True)


def read_frontmatter_title(md_path: Path) -> str:
    try:
        lines = md_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return md_path.parent.name
    if not lines or lines[0].strip() != "---":
        return md_path.parent.name
    for i in range(1, min(len(lines), 30)):
        line = lines[i].strip()
        if line == "---":
            break
        match = re.match(r'^title:\s*"(.*)"\s*$', line)
        if match:
            return match.group(1).strip() or md_path.parent.name
        match = re.match(r"^title:\s*(.*)\s*$", line)
        if match:
            raw = match.group(1).strip().strip('"').strip("'")
            if raw:
                return raw
    return md_path.parent.name


def extract_lecture_number(title: str) -> int | None:
    match = re.search(r"第\s*(\d{1,3})\s*讲", title)
    if not match:
        return None
    return int(match.group(1))


def extract_lecture_number_from_file(md_path: Path) -> int | None:
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None
    return extract_lecture_number(text)


def build_indexes_from_generated() -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, lis