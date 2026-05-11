"""
guidelines_to_essence.py v2
guidelines_reviewed (verdict=keep/edit) 143件 → essence テーブルに注入
essenceスキーマ: axis, content, updated_at, source_count
"""
import sqlite3
from datetime import datetime

DB_PATH = 'data/mocka_events.db'
MAX_LINES = 8  # 注入する最大行数/軸

def main():
    conn = sqlite3.connect(DB_PATH)

    # 採用済みguidelinesを取得
    rows = conn.execute("""
        SELECT category, source_text, action_summary, prevent_how, edited_content
        FROM guidelines_reviewed
        WHERE verdict IN ('keep', 'edit')
        ORDER BY score DESC
    """).fetchall()
    print(f'採用件数: {len(rows)}件')

    # カテゴリ → essence軸 マッピング
    mapping = {
        'INCIDENT':  'INCIDENT',
        'CHALLENGE': 'INCIDENT',
        'GENERAL':   'PHILOSOPHY',
        'INSIGHT':   'PHILOSOPHY',
        'DECISION':  'OPERATION',
        'MATAKA':    'OPERATION',
    }

    # 軸ごとに分類
    axis_rows = {'INCIDENT': [], 'PHILOSOPHY': [], 'OPERATION': []}
    for row in rows:
        axis = mapping.get(row[0], 'PHILOSOPHY')
        axis_rows[axis].append(row)

    print('\n--- 軸別件数 ---')
    for axis, ar in axis_rows.items():
        print(f'  {axis}: {len(ar)}件')

    print('\n--- 注入開始 ---')
    now = datetime.now().isoformat()

    for axis, ar in axis_rows.items():
        # 既存content取得
        existing_row = conn.execute(
            "SELECT content, source_count FROM essence WHERE axis=?", (axis,)
        ).fetchone()
        existing_content = existing_row[0] if existing_row else ''
        existing_count = existing_row[1] if existing_row else 0

        # 既存の[guideline]行を除去してから再注入（重複防止）
        existing_lines = [l for l in existing_content.split('\n')
                          if l.strip() and not l.startswith('[guideline]')]

        # 新しいguideline行を構築
        new_lines = []
        for category, source_text, action_summary, prevent_how, edited_content in ar:
            text = edited_content if edited_content else source_text
            summary = text.replace('\n', ' ').replace('\r', '').strip()[:80]
            if prevent_how:
                line = f"[guideline] {summary} → {prevent_how[:60]}"
            elif action_summary:
                line = f"[guideline] {summary} → {action_summary[:60]}"
            else:
                line = f"[guideline] {summary}"
            new_lines.append(line)
            if len(new_lines) >= MAX_LINES:
                break

        # 既存行 + 新guideline行を結合
        merged = existing_lines + new_lines
        final_content = '\n'.join(merged)
        new_count = existing_count + len(new_lines)

        # UPSERT
        conn.execute("""
            INSERT INTO essence (axis, content, updated_at, source_count)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(axis) DO UPDATE SET
                content=excluded.content,
                updated_at=excluded.updated_at,
                source_count=excluded.source_count
        """, (axis, final_content, now, new_count))

        print(f'  {axis}: {len(new_lines)}行注入 (既存{len(existing_lines)}行 + 新規{len(new_lines)}行)')

    conn.commit()
    conn.close()

    print('\n✅ 完了: essenceへの注入完了')
    print('次回セッション開始時のPHL注入に反映されます')

if __name__ == '__main__':
    main()
