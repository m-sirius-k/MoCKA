# -*- coding: utf-8 -*-
"""Report Alignment Engine (Phase 4-3 Report Truth Governance Layer)

役割: レポートを「修正」しない。代わりに:
  1. 「正しい状態(truth_state)との差分」を生成
  2. 「レポート修正案」を生成 (テキストの提案のみ、ファイルへの書き込みは行わない)

出力は AlignmentDiff のリスト。Governance Engine はこれを参照するが、
本エンジン自身がレポートファイルを書き換えることは禁止 (report override禁止)。
"""

from dataclasses import dataclass, field


@dataclass
class AlignmentDiff:
    file_path: str
    report_source: str
    line_no: int
    claimed_status: str
    truth_state: str
    diff_description: str
    proposed_correction: str


def generate(file_path: str, claim_set, truth_state: str) -> list:
    """指定ファイルについて、claim と truth_state が異なる箇所の
    AlignmentDiff を生成する。truth_state == claimed_status の場合は
    diffを生成しない。
    """
    diffs = []
    for c in claim_set.for_file(file_path):
        if c.claimed_status == "UNKNOWN":
            continue
        if c.claimed_status == truth_state:
            continue

        diff_description = (
            f"{c.report_source}:L{c.line_no} は '{c.claimed_status}' と記載しているが、"
            f"確定状態(Code Evidence)は '{truth_state}' である。"
        )
        proposed_correction = (
            f"[提案] {c.report_source}:L{c.line_no} の記述を "
            f"'{c.claimed_status}' -> '{truth_state}' に更新する "
            f"(根拠: Code Evidence / Reality Sync Result)。"
            f"原文: \"{c.quote}\""
        )

        diffs.append(AlignmentDiff(
            file_path=file_path,
            report_source=c.report_source,
            line_no=c.line_no,
            claimed_status=c.claimed_status,
            truth_state=truth_state,
            diff_description=diff_description,
            proposed_correction=proposed_correction,
        ))

    return diffs


if __name__ == "__main__":
    from report_truth_governance.report_parser import parse
    from report_truth_governance.report_evidence_linker import link
    from report_truth_governance.report_truth_validator import true_state

    claim_set = parse()
    evidence_map = link()

    for file_path in sorted(claim_set.files()):
        truth, _ = true_state(file_path, evidence_map)
        for d in generate(file_path, claim_set, truth):
            print(d)
