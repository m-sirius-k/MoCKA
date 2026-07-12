import sys
import io
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
"""
governance/human_gate_cli.py

Human Gate CLI Provider（Decision Unit B/C承認、実装範囲限定）。

MCPセッション断時でも、ローカル環境から博士本人が直接Human Gateへ
意思表示できるようにするための入力手段の追加のみを目的とする。

以下は行わない（実装範囲外）:
- phi_os/human_gate.py の変更（既存の submit/approve/reject/get_state/
  list_pending を呼び出すのみ）
- Event Store（data/mocka_events.db, human_gate_events テーブル）の複製・変更
- Human Gate Event形式の変更
- Router/Policyの実装（本スクリプトは単体のProviderであり、Routerには未接続）
- mocka_git_safe_commit()の実行（承認結果の event_id を後続でどう渡すかは
  呼び出し元の運用判断であり、本スクリプトはcommitを一切実行しない）

approve/rejectはTTY（対話端末）からの実行のみ許可する。非対話実行（パイプ・
自動スクリプト経由）は拒否する。これは「AIは承認主体にならない」という
既存原則を、CLI入力の受付時点で機械的に強制するための唯一のガードである。
"""
import argparse
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from phi_os.human_gate import submit, approve, reject, get_state, list_pending, HumanGateError


def _require_tty(action: str) -> None:
    if not sys.stdin.isatty():
        print(f"[human_gate_cli] ERROR: '{action}' は対話端末(TTY)からの実行のみ許可されています。"
              f"非対話実行(自動スクリプト・パイプ経由)は拒否します。")
        sys.exit(1)


def cmd_submit(args):
    payload = {}
    if args.note:
        payload["note"] = args.note
    if args.request_id:
        payload["request_id"] = args.request_id
    event = submit(payload)
    print(f"[submit] request_id={event['request_id']} state={event['next_state']}")


def cmd_status(args):
    state = get_state(args.request_id)
    print(f"[status] request_id={args.request_id} state={state if state else 'not_found'}")


def cmd_pending(args):
    rows = list_pending()
    if not rows:
        print("[pending] PENDING状態のrequest_idはありません。")
        return
    for row in rows:
        print(f"  {row['request_id']}  submitted_at={row['timestamp']}")


def cmd_approve(args):
    _require_tty("approve")
    current = get_state(args.request_id)
    if current is None:
        print(f"[approve] ERROR: request_id not found: {args.request_id}")
        sys.exit(1)
    print(f"[approve] request_id={args.request_id} 現在の状態={current}")
    confirm = input("この内容を、きむら博士本人が確認した上で承認しますか？ [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("[approve] キャンセルしました。")
        return
    payload = {"note": args.note} if args.note else None
    event = approve(args.request_id, payload)
    print(f"[approve] request_id={args.request_id} state={event['next_state']} event_id={event['event_id']}")


def cmd_reject(args):
    _require_tty("reject")
    current = get_state(args.request_id)
    if current is None:
        print(f"[reject] ERROR: request_id not found: {args.request_id}")
        sys.exit(1)
    confirm = input(f"request_id={args.request_id}(現在={current})を却下しますか？ [yes/no]: ")
    if confirm.strip().lower() != "yes":
        print("[reject] キャンセルしました。")
        return
    payload = {"note": args.note} if args.note else None
    event = reject(args.request_id, payload)
    print(f"[reject] request_id={args.request_id} state={event['next_state']} event_id={event['event_id']}")


def main():
    parser = argparse.ArgumentParser(description="Human Gate CLI Provider")
    sub = parser.add_subparsers(dest="command", required=True)

    p_submit = sub.add_parser("submit", help="新規Human Gateリクエストを作成する")
    p_submit.add_argument("--request-id", dest="request_id")
    p_submit.add_argument("--note")
    p_submit.set_defaults(func=cmd_submit)

    p_status = sub.add_parser("status", help="request_idの現在状態を確認する")
    p_status.add_argument("request_id")
    p_status.set_defaults(func=cmd_status)

    p_pending = sub.add_parser("pending", help="PENDING状態の一覧を表示する")
    p_pending.set_defaults(func=cmd_pending)

    p_approve = sub.add_parser("approve", help="request_idを承認する(TTY必須)")
    p_approve.add_argument("request_id")
    p_approve.add_argument("--note")
    p_approve.set_defaults(func=cmd_approve)

    p_reject = sub.add_parser("reject", help="request_idを却下する(TTY必須)")
    p_reject.add_argument("request_id")
    p_reject.add_argument("--note")
    p_reject.set_defaults(func=cmd_reject)

    args = parser.parse_args()
    try:
        args.func(args)
    except HumanGateError as e:
        print(f"[human_gate_cli] ERROR: {e.reason}")
        sys.exit(1)


if __name__ == "__main__":
    main()
