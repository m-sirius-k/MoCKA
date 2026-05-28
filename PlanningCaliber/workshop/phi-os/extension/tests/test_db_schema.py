# test_db_schema.py — DNA_v3 Step2 テスト
import sqlite3
import os
import sys

DB_PATH = r"C:\Users\sirok\MoCKA\data\mocka_events.db"

def test_judgement_reason_exists():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='judgement_reason'")
    result = c.fetchone()
    conn.close()
    assert result is not None, "judgement_reason テーブルが存在しない"
    print("[PASS] judgement_reason テーブル存在確認")

def test_indexes_exist():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='judgement_reason'")
    indexes = [r[0] for r in c.fetchall()]
    conn.close()
    required = ["idx_jr_tags", "idx_jr_tension", "idx_jr_session", "idx_jr_event"]
    for idx in required:
        assert idx in indexes, f"インデックス {idx} が存在しない"
    print("[PASS] インデックス全4件確認")

def test_insert_and_query():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO judgement_reason
        (event_id, session_date, decision, reason, tension, tension_severity, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, ("E_TEST_001", "2026-05-28", "採用",
          "テスト挿入", "テスト違和感", 3, "tension,unresolved"))
    conn.commit()
    c.execute("SELECT id FROM judgement_reason WHERE event_id='E_TEST_001'")
    result = c.fetchone()
    c.execute("DELETE FROM judgement_reason WHERE event_id='E_TEST_001'")
    conn.commit()
    conn.close()
    assert result is not None, "挿入・取得に失敗"
    print("[PASS] INSERT/SELECT/DELETE確認")

def test_decision_constraint():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO judgement_reason (event_id, session_date, decision, reason)
            VALUES (?, ?, ?, ?)
        """, ("E_TEST_BAD", "2026-05-28", "INVALID", "test"))
        conn.commit()
        conn.close()
        assert False, "不正なdecision値が挿入できてしまった"
    except sqlite3.IntegrityError:
        conn.close()
        print("[PASS] decision CHECK制約確認")

def test_tension_severity_constraint():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO judgement_reason (event_id, session_date, decision, reason, tension_severity)
            VALUES (?, ?, ?, ?, ?)
        """, ("E_TEST_BAD2", "2026-05-28", "採用", "test", 9))
        conn.commit()
        conn.close()
        assert False, "tension_severity=9 が挿入できてしまった"
    except sqlite3.IntegrityError:
        conn.close()
        print("[PASS] tension_severity CHECK制約確認")

if __name__ == "__main__":
    test_judgement_reason_exists()
    test_indexes_exist()
    test_insert_and_query()
    test_decision_constraint()
    test_tension_severity_constraint()
    print("=== 全テスト PASS ===")
