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
        """
        MoCKA標準 JSON-LD 機械公文書を生成する。

        位置づけ: HTML=Presentation Layer / JSON-LD=Machine Knowledge Layer
        対象読者: Google ではなく LLM・AIエージェント向けの「事実契約書」。
        構成: Article（記事本体） + ClaimReview（主張記録） + FAQPage（Q&A抽出）
        """
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        author_entity = {
            "@type": "Organization",
            "name":  "MoCKA PR-OS",
            "url":   "https://github.com/m-sirius-k/MoCKA"
        }

        # ── Article（記事本体） ─────────────────────────────────
        article = {
            "@context":       "https://schema.org",
            "@type":          "Article",
            "headline":       seo_result.title,
            "description":    seo_result.description,
            "author":         author_entity,
            "publisher":      author_entity,
            "datePublished":  date_str,
            "dateModified":   date_str,
            "keywords":       ", ".join(seo_result.tags),
            "articleSection": seo_result.category,
            "inLanguage":     "ja",
            "url":            "",
            # LLM引用最適化フィールド
            "abstract":       seo_result.description,
            "mainEntityOfPage": {
                "@type": "WebPage",
                "url":   ""
            }
        }

        # ── ClaimReview（主張記録・事実契約書） ─────────────────
        # 記事タイトルを主要主張として記録する
        claim_review = {
            "@context": "https://schema.org",
            "@type":    "ClaimReview",
            "claimReviewed": seo_result.title,
            "author":        author_entity,
            "datePublished": date_str,
            "reviewRating": {
                "@type":       "Rating",
                "ratingValue": "5",
                "bestRating":  "5",
                "worstRating": "1",
                "alternateName": "Verified"
            },
            "itemReviewed": {
                "@type":       "CreativeWork",
                "name":        seo_result.title,
                "description": seo_result.description,
                "author":      author_entity
            }
        }

        # ── FAQPage（Q&A抽出・LLM引用最適化） ───────────────────
        # 見出しをQ&Aペアとして抽出（LLMが引用しやすい構造）
        faq_entries = self._extract_faq_pairs(seo_result.confirmed_text)
        faq_page = None
        if faq_entries:
            faq_page = {
                "@context":   "https://schema.org",
                "@type":      "FAQPage",
                "mainEntity": faq_entries
            }

        # ── MoCKA 機械公文書メタデータ ──────────────────────────
        mocka_meta = {
            "mocka_layer":     "Machine Knowledge Layer",
            "mocka_purpose":   "LLM citation optimization",
            "content_type":    seo_result.content_type,
            "distribution":    seo_result.targets,
            "routing_intent":  seo_result.intent,
        }

        result = {
            "article":      article,
            "claim_review": claim_review,
            "mocka_meta":   mocka_meta,
        }
        if faq_page:
            result["faq_page"] = faq_page

        return result

    def _extract_faq_pairs(self, text: str) -> list:
        """
        Markdownの見出し+直後の段落をFAQ Question/Answerペアに変換する。
        LLMが記事内容を引用する際の粒度を最適化する。
        """
        import re
        # フロントマター除去
        body = re.sub(r"^---\n.*?\n---\n?", "", text, flags=re.DOTALL).strip()
        lines = body.splitlines()

        pairs = []
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            m = re.match(r"^#{2,4} (.+)$", line)
            if m:
                question = m.group(1).strip()
                # 直後の空行でない行を回答として収集（最大5行）
                answer_lines = []
                j = i + 1
                while j < len(lines) and len(answer_lines) < 5:
                    l = lines[j].strip()
                    if re.match(r"^#{1,4} ", l):
                        break
                    if l:
                        answer_lines.append(l)
                    j += 1

                if answer_lines:
                    pairs.append({
                        "@type":          "Question",
                        "name":           question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text":  " ".join(answer_lines)[:500]
                        }
                    })
            i += 1

        return pairs[:10]  # 最大10ペア
