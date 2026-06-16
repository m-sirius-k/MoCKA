"""
HTML GENERATOR — SEO最適HTML生成
SEO-CENTER出力を受け取り、Web標準HTML articleを生成する
"""
import re
from datetime import datetime, timezone


def _md_to_blocks(text: str) -> list[dict]:
    """Markdownを意味ブロック（intro / core / analysis / conclusion）に分解"""
    # フロントマター除去
    text = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()

    lines = text.splitlines()
    blocks: dict[str, list[str]] = {
        "introduction": [],
        "core": [],
        "analysis": [],
        "conclusion": [],
    }
    current = "introduction"
    section_map = {
        ("概要", "はじめに", "intro", "introduction", "overview"): "introduction",
        ("本質", "本文", "core", "main", "内容", "構造"): "core",
        ("分析", "考察", "analysis", "detail", "詳細"): "analysis",
        ("結論", "まとめ", "conclusion", "summary", "おわりに"): "conclusion",
    }

    for line in lines:
        if line.startswith("## ") or line.startswith("# "):
            heading = line.lstrip("#").strip().lower()
            for keys, section in section_map.items():
                if any(k in heading for k in keys):
                    current = section
                    break
        blocks[current].append(line)

    return blocks


def _md_inline(text: str) -> str:
    """インライン Markdown → HTML"""
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    text = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', text)
    return text


def _lines_to_html(lines: list[str]) -> str:
    """行リストをHTMLブロックに変換"""
    html_parts = []
    in_ul = False
    in_ol = False
    in_pre = False
    buffer = []

    def flush_para():
        nonlocal buffer
        if buffer:
            content = _md_inline(" ".join(buffer).strip())
            if content:
                html_parts.append(f"<p>{content}</p>")
            buffer = []

    for line in lines:
        if line.startswith("```"):
            if in_pre:
                html_parts.append("</code></pre>")
                in_pre = False
            else:
                flush_para()
                lang = line[3:].strip()
                cls = f' class="language-{lang}"' if lang else ""
                html_parts.append(f"<pre><code{cls}>")
                in_pre = True
            continue

        if in_pre:
            html_parts.append(line)
            continue

        # 見出し
        m = re.match(r"^(#{1,4}) (.+)$", line)
        if m:
            flush_para()
            level = len(m.group(1))
            tag = f"h{min(level + 1, 4)}"
            html_parts.append(f"<{tag}>{_md_inline(m.group(2))}</{tag}>")
            continue

        # 番号なしリスト
        m = re.match(r"^[-*] (.+)$", line)
        if m:
            flush_para()
            if not in_ul:
                html_parts.append("<ul>")
                in_ul = True
            html_parts.append(f"<li>{_md_inline(m.group(1))}</li>")
            continue
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False

        # 番号付きリスト
        m = re.match(r"^\d+\. (.+)$", line)
        if m:
            flush_para()
            if not in_ol:
                html_parts.append("<ol>")
                in_ol = True
            html_parts.append(f"<li>{_md_inline(m.group(1))}</li>")
            continue
        if in_ol:
            html_parts.append("</ol>")
            in_ol = False

        # 空行
        if not line.strip():
            flush_para()
            continue

        # 通常テキスト
        buffer.append(line)

    flush_para()
    if in_ul:
        html_parts.append("</ul>")
    if in_ol:
        html_parts.append("</ol>")

    return "\n".join(html_parts)


class HTMLGenerator:
    """SEO最適HTMLを生成するジェネレータ"""

    def generate(self, seo_result: "SEOResult") -> str:
        """
        SEOResultからフルHTML article要素を生成する。

        Returns: str（<article>〜</article>）
        """
        blocks = _md_to_blocks(seo_result.confirmed_text)

        intro_html    = _lines_to_html(blocks["introduction"])
        core_html     = _lines_to_html(blocks["core"])
        analysis_html = _lines_to_html(blocks["analysis"])
        conclusion_html = _lines_to_html(blocks["conclusion"])

        # コアブロックが空なら全文をcoreに入れる（セクション分割できなかった場合）
        if not core_html.strip():
            core_html = _lines_to_html(
                seo_result.confirmed_text.splitlines()
            )

        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        tags_html = "".join(
            f'<span class="tag">{t}</span>' for t in seo_result.tags
        )

        html = f"""<article itemscope itemtype="https://schema.org/Article">
  <header>
    <h1 itemprop="headline">{seo_result.title}</h1>
    <meta name="description" content="{seo_result.description}">
    <div class="meta">
      <time itemprop="datePublished" datetime="{date_str}">{date_str}</time>
      <div class="tags">{tags_html}</div>
    </div>
  </header>

  <section id="introduction" aria-label="概要">
    <h2>概要</h2>
    {intro_html if intro_html.strip() else f"<p>{seo_result.description}</p>"}
  </section>

  <section id="core" aria-label="本質構造">
    <h2>本質構造</h2>
    {core_html}
  </section>"""

        if analysis_html.strip():
            html += f"""

  <section id="analysis" aria-label="分析">
    <h2>分析</h2>
    {analysis_html}
  </section>"""

        if conclusion_html.strip():
            html += f"""

  <section id="conclusion" aria-label="結論">
    <h2>結論</h2>
    {conclusion_html}
  </section>"""

        html += f"""

  <footer>
    <p itemprop="author" itemscope itemtype="https://schema.org/Organization">
      Generated by <span itemprop="name">PR-OS + MoCKA</span>
    </p>
  </footer>
</article>"""

        return html

    def generate_json_ld(self, seo_result: "SEOResult") -> dict:
        """JSON-LD構造化データを生成"""
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        return {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": seo_result.title,
            "description": seo_result.description,
            "author": {
                "@type": "Organization",
                "name": "MoCKA PR-OS"
            },
            "datePublished": date_str,
            "keywords": ", ".join(seo_result.tags),
            "articleSection": seo_result.category,
            "url": ""
        }
