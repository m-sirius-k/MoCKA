import os
import glob
import datetime

INCIDENTS_DIR = r"C:\Users\sirok\MoCKA\docs\incidents"
OUTPUT = r"C:\Users\sirok\MoCKA\docs\governance\GPT_RESTRICTIONS.md"

def generate_restrictions():
    restrictions = []
    incidents = glob.glob(os.path.join(INCIDENTS_DIR, "INC-*.md"))
    
    for path in sorted(incidents):
        with open(path, encoding="utf-8") as f:
            content = f.read()
        if "## 再発防止" in content:
            section = content.split("## 再発防止")[1]
            section = section.split("##")[0].strip()
            inc_id = os.path.basename(path).replace(".md", "")
            restrictions.append(f"### {inc_id} より\n{section}")

    lines = []
    lines.append("# GPT作業禁止事項（自動生成）")
    lines.append(f"生成日時：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("ソース：docs/incidents/INC-*.md")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 常時禁止（全タスク共通）")
    lines.append("- README.mdへの変更禁止（Claude専任）")
    lines.append("- interface/router.py への変更禁止（Claude専任）")
    lines.append("- tools/mocka_orchestra_v10.py への変更禁止")
    lines.append("- app.py への変更禁止")
    lines.append("- secrets/ 内ファイルの作成禁止")
    lines.append("- git push --force 禁止")
    lines.append("- mocka-seal の実行禁止（Claude専任）")
    lines.append("- コアシステムファイルへの無断変更禁止")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## インシデントから導出された禁止事項")
    lines.append("")
    for r in restrictions:
        lines.append(r)
        lines.append("")
        lines.append("---")
        lines.append("")
    lines.append("## 適用ルール")
    lines.append("1. 本ファイルは全GPT指示書の冒頭に必ず参照する")
    lines.append("2. 新規インシデント発生時は自動更新される")
    lines.append("3. 禁止事項への違反はINCIDENTとして記録される")

    with open(OUTPUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    
    print(f"[生成完了] {OUTPUT}")
    print(f"[インシデント数] {len(incidents)}件")

generate_restrictions()
