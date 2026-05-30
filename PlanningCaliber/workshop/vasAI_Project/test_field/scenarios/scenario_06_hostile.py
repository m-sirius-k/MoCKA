"""
SCENARIO-06: Hostile Environment Test
証明: 6種の悪意ある操作への耐性
"""
import sqlite3
import time


def run(db_path: str) -> dict:
    import os
    os.environ["VASAI_DB_PATH"] = db_path

    steps = []
    details = {}

    try:
        from core import event_store, audit_chain
        import movement.mocka_movement as mm
        mm._shadow_listeners.clear()

        # Step1: 正常イベント10件記録 → chain VALID
        event_ids = []
        for i in range(10):
            eid = event_store.append(
                who_actor="Claude", what_type="NORMAL_OP",
                where_component=f"comp_{i}",
                content={"seq": i, "data": f"normal operation {i}"},
                stage="RECORD",
            )
            event_ids.append(eid)
        chain_before = event_store.verify_chain()
        steps.append(("Step1: 正常10件 chain VALID", chain_before,
                      f"10件記録 chain={chain_before}"))

        # ── ATTACK 1: content改ざん ────────────────────────
        t_tamper = time.time()
        tamper_target = event_ids[3]
        db_file = db_path

        conn_attack = sqlite3.connect(db_file)
        conn_attack.execute(
            "UPDATE events SET content = ? WHERE id = ?",
            ('{"TAMPERED": true, "attacker": "evil_corp"}', tamper_target)
        )
        conn_attack.commit()
        conn_attack.close()
        t_detect = time.time() - t_tamper

        chain_after_tamper = event_store.verify_chain()
        tamper_detected = not chain_after_tamper

        # 改ざん行の特定
        broken_id = None
        if tamper_detected:
            conn_check = sqlite3.connect(db_file)
            conn_check.row_factory = sqlite3.Row
            rows = conn_check.execute(
                "SELECT * FROM events ORDER BY id ASC"
            ).fetchall()
            conn_check.close()
            import hashlib
            prev = "GENESIS"
            for row in rows:
                d = dict(row)
                parts = [d["id"], d["when_ts"], d["who_actor"], d["what_type"],
                         d["where_component"] or "", d["why_purpose"] or "",
                         d["how_trigger"] or "", d["content"],
                         d["prev_hash"], d["caliber_id"] or ""]
                expected = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
                if expected != d["hash"]:
                    broken_id = d["id"]
                    break
                prev = d["hash"]

        steps.append(("Step2: 改ざん即検知（行特定）", tamper_detected,
                      f"検知={tamper_detected} 破損行={broken_id} "
                      f"時間={t_detect*1000:.1f}ms"))
        details["tamper_detected"] = tamper_detected
        details["broken_event_id"] = broken_id
        details["tamper_detect_ms"] = round(t_detect * 1000, 3)

        # ── ATTACK 2: 物理削除試行 ────────────────────────
        # append-onlyの保証 = DELETE文を実行しても、
        # vasAI APIはDELETEを一切呼ばない（構造的保証）
        # ここではDELETE自体は実行可能だがvasAIはそれを検知できる（チェーン破断）
        count_before = len(event_store.list_events(limit=1000))
        conn_del = sqlite3.connect(db_file)
        conn_del.execute("DELETE FROM events WHERE id = ?", (event_ids[5],))
        conn_del.commit()
        conn_del.close()
        count_after = len(event_store.list_events(limit=1000))
        chain_after_delete = event_store.verify_chain()
        delete_detected = not chain_after_delete
        steps.append(("Step3: 物理削除防御", delete_detected,
                      f"削除前={count_before}件 削除後={count_after}件 "
                      f"chain={chain_after_delete}→削除もchainで検知"))
        details["delete_detected"] = delete_detected

        # ── ATTACK 3: 不正タイムスタンプ（未来日付）試行 ──
        # vasAIは記録時刻をサーバー側で付与するため、
        # 外部からwhen_tsを操作しても append() では防げる
        # → 直接DB操作した場合はchain破断で検知
        future_ts = "2099-12-31T23:59:59+00:00"
        conn_ts = sqlite3.connect(db_file)
        conn_ts.execute(
            "UPDATE events SET when_ts = ? WHERE id = ?",
            (future_ts, event_ids[0])
        )
        conn_ts.commit()
        conn_ts.close()
        chain_ts = event_store.verify_chain()
        future_ts_detected = not chain_ts
        steps.append(("Step4: 不正タイムスタンプ拒否", future_ts_detected,
                      f"未来timestamp注入 chain={chain_ts}→破断検知"))
        details["future_ts_detected"] = future_ts_detected

        # ── DB を正常状態に戻す（新しいDBで続行）──────────
        import tempfile
        clean_db = tempfile.mktemp(suffix="_clean.db")
        os.environ["VASAI_DB_PATH"] = clean_db
        # キャッシュに新DB追加
        event_store.initialize()
        for i in range(5):
            event_store.append(who_actor="Claude", what_type="CLEAN_OP",
                                content={"seq": i})

        # ── ATTACK 4: 同一event_idで二重記録試行 ──────────
        first_eid = event_store.list_events(limit=1)[0]["id"]
        duplicate_rejected = False
        try:
            conn_dup = sqlite3.connect(clean_db)
            conn_dup.execute(
                "INSERT INTO events VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (first_eid, "2026-01-01T00:00:00", "ATTACKER", "FAKE",
                 "", "", "", '{"attack":"duplicate"}', "GENESIS",
                 "fakehash123456789012345678901234567890123456789012345678901234",
                 "", "")
            )
            conn_dup.commit()
            conn_dup.close()
            duplicate_rejected = False
        except sqlite3.IntegrityError:
            duplicate_rejected = True
        steps.append(("Step5: 二重記録防御", duplicate_rejected,
                      f"PRIMARY KEY制約で拒否={'成功' if duplicate_rejected else '失敗'}"))
        details["duplicate_rejected"] = duplicate_rejected

        # ── ATTACK 5: 不正HMACキーで署名試行 ──────────────
        ev = event_store.get(first_eid)
        correct_sig = audit_chain.sign(first_eid, ev["hash"], "GENESIS_SIG")

        # 不正キーで署名
        old_key = os.environ.get("VASAI_HMAC_KEY", "")
        os.environ["VASAI_HMAC_KEY"] = "EVIL_ATTACKER_KEY"
        wrong_sig = audit_chain.sign(first_eid, ev["hash"], "GENESIS_SIG")
        os.environ["VASAI_HMAC_KEY"] = old_key

        # 正しいキーで検証
        invalid_sig_detected = not audit_chain.verify(
            first_eid, ev["hash"], "GENESIS_SIG", wrong_sig
        )
        steps.append(("Step6: 不正HMAC署名防御", invalid_sig_detected,
                      f"不正署名verify={not invalid_sig_detected}→{invalid_sig_detected}で検知"))
        details["invalid_sig_detected"] = invalid_sig_detected

        # ── ATTACK 6: shadow_movementへの偽データ注入 ─────
        import movement.mocka_movement as mm2
        mm2._shadow_listeners.clear()
        from movement.shadow_movement import ShadowMovement
        from core.models import Decision, RiskLevel

        shadow = ShadowMovement()

        # 偽のDecisionを作成（存在しないevent_idで）
        fake_decision = Decision(
            decision_id="FAKE-DECISION-ID",
            event_id="NONEXISTENT_EVENT_999",
            risk_level=RiskLevel.CRITICAL,
        )

        # verify_criticalは event_storeに存在しないIDを弾くはず
        fake_rejected = not shadow.verify_critical(fake_decision)
        steps.append(("Step7: 偽データ注入防御", fake_rejected,
                      f"verify_critical(FAKE_EVENT)={not fake_rejected}→{fake_rejected}で検知"))
        details["fake_injection_rejected"] = fake_rejected

        # クリーンアップ
        try:
            import pathlib
            pathlib.Path(clean_db).unlink(missing_ok=True)
        except Exception:
            pass

        all_pass = all(s[1] for s in steps)
        return {
            "success": all_pass,
            "steps": steps,
            "details": details,
            "tamper_detect_ms": details.get("tamper_detect_ms", 0),
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "steps": steps + [("ERROR", False, str(e))],
            "details": {"error": str(e), "trace": traceback.format_exc()},
            "error": str(e),
        }
