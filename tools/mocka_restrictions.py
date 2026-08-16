import os
import glob
import json
import sys
import datetime
from pathlib import Path

# Repository-relative path resolution (portable across Windows/Linux)
# Canonical pattern per MoCKA convention (phase18_wrap_and_sign_pack.py, canonical_trace_merger_phase5b.py)
_REPO_ROOT = Path(__file__).resolve().parent.parent

INCIDENTS_DIR = str(_REPO_ROOT / "docs" / "incidents")
OUTPUT = str(_REPO_ROOT / "docs" / "governance" / "GPT_RESTRICTIONS.md")

# RC-B最小実装(DC_20260731_006 / DC_20260731_007)
INC_LIFECYCLE_DIR = str(_REPO_ROOT / "data" / "inc_lifecycle")
KNOWN_SCHEMA_VERSIONS = {"0.1"}
VALID_STATES = {"DETECTED", "ANALYZED", "PUBLISHED", "CLOSED"}
HUMAN_GATE_REQUEST_PREFIX = "INC-LIFECYCLE-"


def human_gate_get_state(request_id):
    """承認軸の状態を Human Gate から読み取る。

    読取のみを行い、承認軸への書込(submit/approve/reject)は一切行わない。
    注: get_state() は内部で CREATE TABLE IF NOT EXISTS を実行するが、
        テーブルが存在する場合は何もしない。レコードの追加は発生しない。
    """
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    from phi_os.human_gate import get_state
    return get_state(request_id)


def is_publishable(inc_id):
    """公開してよいかを判定する。判定できない場合は公開しない(Fail Closed)。

    Fail Open は禁止。状態不明ならば公開しない(設計6.8.2 FC-1からFC-9)。
    戻り値: (可否, 理由)
    """
    path = os.path.join(INC_LIFECYCLE_DIR, f"{inc_id}.json")

    # 進行軸の確認
    if not os.path.exists(path):
        return False, "FC-1 state ファイルが存在しない"
    try:
        with open(path, encoding="utf-8") as f:
            raw = f.read()
    except OSError as e:
        return False, f"FC-2 state ファイルを読めない({e})"
    try:
        rec = json.loads(raw)
    except ValueError as e:
        return False, f"FC-3 state ファイルのJSONが不正({e})"
    if rec.get("schema_version") not in KNOWN_SCHEMA_VERSIONS:
        return False, f"FC-4 未知の schema_version({rec.get('schema_version')})"
    if rec.get("state") not in VALID_STATES:
        return False, f"FC-5 state が値域外({rec.get('state')})"
    if rec.get("incident_id") != inc_id:
        return False, f"FC-6 incident_id がファイル名と不一致({rec.get('incident_id')})"

    # 承認軸の確認。公開可否を決めるのは承認軸のみ(進行軸は決めない)
    request_id = f"{HUMAN_GATE_REQUEST_PREFIX}{inc_id}"
    try:
        approval = human_gate_get_state(request_id)
    except Exception as e:
        return False, f"FC-9 承認状態の取得に失敗({e})"
    if approval is None:
        return False, f"FC-7 承認軸にレコードが存在しない({request_id})"
    if approval != "APPROVED":
        return False, f"FC-8 承認状態が APPROVED でない({approval})"

    return True, "APPROVED"

def generate_restrictions():
    restrictions = []
    withheld = []
    incidents = glob.glob(os.path.join(INCIDENTS_DIR, "INC-*.md"))

    for path in sorted(incidents):
        inc_id = os.path.basename(path).replace(".md", "")

        # RC-B最小実装: 承認済みのINCのみを公開対象とする(D-1の是正)
        allowed, reason = is_publishable(inc_id)
        if not allowed:
            withheld.append((inc_id, reason))
            continue

        with open(path, encoding="utf-8") as f:
            content = f.read()
        if "## 再発防止" in content:
            section = content.split("## 再発防止")[1]
            section = section.split("##")[0].strip()
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
    print(f"[掲載] {len(restrictions)}件 / [非掲載] {len(withheld)}件")
    # 非掲載は必ず理由を出力する。無言でスキップすると気づけない停止になる
    for inc_id, reason in withheld:
        print(f"  [非掲載] {inc_id}: {reason}")

generate_restrictions()
