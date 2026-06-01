# -*- coding: utf-8 -*-
"""
structural/bee.py — β Ecology Engine (BEE) (TODO_216)
βのライフサイクル（観察β→成長中→確立→制度化→衰退→消滅）を管理する。
毎朝 MoCKA-START.bat から呼び出す。APIゼロ・ローカル処理。

Usage:
  python structural/bee.py --daily     # 毎朝スキャン（全処理）
  python structural/bee.py --status    # 現在のβライフサイクル一覧
  python structural/bee.py --evidence <beta_id> [--type support|contra] [--source scan]
"""
import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Windows コンソール UTF-8 対応
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ROOT           = Path(__file__).parent.parent
STRUCTURAL_DIR = Path(__file__).parent
BETA_REG_PATH  = STRUCTURAL_DIR / "beta_registry.json"
PATTERN_DB_PATH = STRUCTURAL_DIR / "pattern_db.json"
DB_PATH        = ROOT / "data" / "mocka_events.db"
MCP_URL        = "http://localhost:5002/agent/mocka_write_event"

# ─── ライフサイクル閾値 ──────────────────────────────────────────────────────

STAGE_THRESHOLDS = {
    "観察β":   {"evidence_min": 0,  "evidence_max": 4,  "contra_rate_max": None},
    "成長中":   {"evidence_min": 5,  "evidence_max": 19, "contra_rate_max": 0.39},
    "確立":     {"evidence_min": 20, "evidence_max": None,"contra_rate_max": 0.19},
    "制度化":   {"evidence_min": 20, "evidence_max": None,"contra_rate_max": 0.19},  # Meta β生成済み
    "衰退":     {"contra_rate_min": 0.40},
    "消滅":     {"days_since_last_seen": 90},
}

# ─── JSON ローダー ───────────────────────────────────────────────────────────

def _load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def _save_json(path: Path, data: dict):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

# ─── BetaEcologyEngine ───────────────────────────────────────────────────────

class BetaEcologyEngine:

    def __init__(self):
        self.breg  = _load_json(BETA_REG_PATH)
        self.pdb   = _load_json(PATTERN_DB_PATH)
        self._dirty = False

    def _save(self):
        if self._dirty:
            _save_json(BETA_REG_PATH, self.breg)
            self._dirty = False

    # ── 1. evidence 収集 ─────────────────────────────────────────────────────

    def collect_evidence(self, beta_id: str) -> dict:
        """
        events.db を全スキャンして beta の構造タグと一致するイベントを
        evidence / contradiction に仕分けする。
        """
        entry = self.breg.get(beta_id)
        if not entry:
            return {"error": f"{beta_id} not found"}

        # betaの構造タグ: tension から抽出
        tension = entry.get("tension", "")
        support_tags = self._extract_tags_from_tension(tension, side="left")
        contra_tags  = self._extract_tags_from_tension(tension, side="right_inverted")

        if not DB_PATH.exists():
            return {"error": "DB not found", "beta_id": beta_id}

        try:
            con = sqlite3.connect(str(DB_PATH))
            cur = con.cursor()
            cur.execute(
                "SELECT event_id, title, what_type, why_purpose, how_trigger FROM events "
                "ORDER BY when_ts DESC LIMIT 500"
            )
            rows = cur.fetchall()
            con.close()
        except Exception as e:
            return {"error": str(e), "beta_id": beta_id}

        ev_new     = 0
        contra_new = 0
        for row in rows:
            text = " ".join(str(c) for c in row if c)
            text_lower = text.lower()
            matched_support = any(
                any(kw.lower() in text_lower for kw in self.pdb.get(tag, {}).get("keywords", []))
                for tag in support_tags
            )
            # 反証: contra_tags のキーワードが出現し、かつ support_tags のキーワードが
            # 出現しない場合のみカウント（支持と反証が同時にあれば支持を優先）
            matched_contra = (
                not matched_support and
                any(
                    any(kw.lower() in text_lower for kw in self.pdb.get(tag, {}).get("keywords", []))
                    for tag in contra_tags
                )
            )
            if matched_support:
                ev_new += 1
            if matched_contra:
                contra_new += 1

        today = datetime.now().strftime("%Y-%m-%d")
        self.breg[beta_id]["evidence"]     = entry.get("evidence", 0) + ev_new
        self.breg[beta_id]["contradiction"] = entry.get("contradiction", 0) + contra_new
        self.breg[beta_id]["last_seen"]    = today
        self._dirty = True

        return {
            "beta_id":     beta_id,
            "ev_added":    ev_new,
            "contra_added": contra_new,
            "evidence_total": self.breg[beta_id]["evidence"],
            "contra_total":   self.breg[beta_id]["contradiction"],
        }

    def _extract_tags_from_tension(self, tension: str, side: str) -> list:
        """tension 文字列（"tag_a → tag_b"）からタグを抽出する"""
        if "→" in tension:
            parts = [t.strip() for t in tension.split("→")]
            if side == "left" and len(parts) >= 1:
                return [parts[0]] if parts[0] in self.pdb else []
            if side == "right_inverted" and len(parts) >= 2:
                # 右側タグの「反対方向」= 右側が出現したら支持、左側が消えたら反証
                # ここでは単純に左側タグのキーワードが出ない場合を反証とする
                return [parts[1]] if parts[1] in self.pdb else []
        return []

    # ── 2. ライフサイクル更新 ────────────────────────────────────────────────

    def update_lifecycle(self, beta_id: str) -> str:
        """evidence / contradiction の比率から status を自動更新する"""
        entry = self.breg.get(beta_id)
        if not entry:
            return "not_found"

        ev     = entry.get("evidence", 0)
        contra = entry.get("contradiction", 0)
        rate   = contra / ev if ev > 0 else 0.0
        current = entry.get("status", "観察β")
        last_seen = entry.get("last_seen", datetime.now().strftime("%Y-%m-%d"))

        # Human Gate 承認済みβは自動的に「衰退」には落とさない
        if entry.get("approved_by") and current in ("確立", "制度化", "成長中"):
            if rate >= 0.40:
                # 承認済みβが高い反証率 → Human Gate に通知するだけで自動衰退はしない
                print(f"  [BEE] 注意: {beta_id} 反証率={rate:.2f} (Human Gate承認済みのため自動衰退スキップ)")
                return current

        # 消滅チェック（90日更新なし）
        try:
            days_since = (datetime.now() - datetime.strptime(last_seen, "%Y-%m-%d")).days
        except Exception:
            days_since = 0

        if days_since >= 90 and current not in ("確立", "制度化"):
            new_status = "消滅"
        elif rate >= 0.40 and current not in ("観察β",):
            new_status = "衰退"
        elif ev >= 20 and rate < 0.20 and current in ("成長中", "観察β"):
            new_status = "確立"
        elif ev >= 5 and current == "観察β":
            new_status = "成長中"
        else:
            new_status = current

        if new_status != current:
            self.breg[beta_id]["status"] = new_status
            self._dirty = True

        return new_status

    # ── 3. 共起検出 ─────────────────────────────────────────────────────────

    def detect_co_occurrence(self):
        """同じイベントで複数βが検知された場合に co_occurrence を更新する"""
        if not DB_PATH.exists():
            return

        try:
            con = sqlite3.connect(str(DB_PATH))
            cur = con.cursor()
            cur.execute(
                "SELECT event_id, title, why_purpose FROM events ORDER BY when_ts DESC LIMIT 300"
            )
            rows = cur.fetchall()
            con.close()
        except Exception:
            return

        beta_ids = [k for k in self.breg if not k.startswith("_")]

        for row in rows:
            text = " ".join(str(c) for c in row if c).lower()
            matched = []
            for bid in beta_ids:
                entry = self.breg[bid]
                tension = entry.get("tension", "")
                tags = self._extract_tags_from_tension(tension, "left")
                kws  = []
                for tag in tags:
                    kws += self.pdb.get(tag, {}).get("keywords", [])
                if any(kw.lower() in text for kw in kws):
                    matched.append(bid)

            # 同一イベントで2β以上検知 → co_occurrence に追記
            if len(matched) >= 2:
                for bid in matched:
                    others = [b for b in matched if b != bid]
                    co = self.breg[bid].get("co_occurrence") or []
                    for other in others:
                        if other not in co:
                            co.append(other)
                    self.breg[bid]["co_occurrence"] = co
                    self._dirty = True

    # ── 4. Meta β抽出 ────────────────────────────────────────────────────────

    META_BETA_TEMPLATES = {
        ("dependency", 3): ("institutional_evolution",  "制度化進化フェーズ",
                            "MoCKAは今、依存関係を制度的に整理する進化フェーズにある"),
        ("risk",       3): ("risk_awareness_culture",   "リスク認知文化の形成",
                            "MoCKAはリスクを検知・記録・制度化するサイクルを確立しつつある"),
        ("automation", 3): ("full_automation_horizon",  "完全自動化地平",
                            "MoCKAの手動プロセスは制度的自動化に向けて収束しつつある"),
    }

    def extract_meta_beta(self) -> list:
        """
        同カテゴリの「確立」βが3つ以上 AND co_occurrence が重なる場合
        Meta β を自動生成する。
        """
        established = [
            bid for bid, e in self.breg.items()
            if not bid.startswith("_") and e.get("status") in ("確立", "制度化")
        ]

        # カテゴリ別に集計
        cat_map: dict[str, list] = {}
        for bid in established:
            tension = self.breg[bid].get("tension", "")
            tags = self._extract_tags_from_tension(tension, "left")
            for tag in tags:
                cat = self.pdb.get(tag, {}).get("category", "")
                if cat:
                    cat_map.setdefault(cat, []).append(bid)

        generated = []
        for (cat, threshold), (meta_key, meta_ja, meta_impl) in self.META_BETA_TEMPLATES.items():
            bids = cat_map.get(cat, [])
            if len(bids) < threshold:
                continue

            # co_occurrence の重なり確認
            co_sets = [set(self.breg[b].get("co_occurrence") or []) for b in bids]
            overlap = co_sets[0].intersection(*co_sets[1:]) if len(co_sets) > 1 else set()

            if len(overlap) >= 1 or len(bids) >= threshold:
                # Meta β を beta_registry に追記
                today = datetime.now().strftime("%Y-%m-%d")
                if meta_key not in self.breg:
                    self.breg[meta_key] = {
                        "beta_ja":       meta_ja,
                        "beta_en":       meta_key,
                        "status":        "制度化",
                        "is_meta":       True,
                        "evidence":      sum(self.breg[b].get("evidence", 0) for b in bids),
                        "contradiction": 0,
                        "last_seen":     today,
                        "first_seen":    today,
                        "implication":   meta_impl,
                        "source_betas":  bids,
                        "co_occurrence": [],
                        "meta_beta":     None,
                        "approved_by":   None,
                        "approved_at":   None,
                        "expires_at":    None,
                    }
                    self._dirty = True
                    # 各source βの meta_beta を更新
                    for b in bids:
                        self.breg[b]["meta_beta"] = meta_key
                        self._dirty = True

                generated.append({"meta_key": meta_key, "meta_ja": meta_ja,
                                   "source_betas": bids})

        return generated

    # ── 5. 消滅処理 ──────────────────────────────────────────────────────────

    def expire_extinct(self) -> list:
        """status=消滅 のβをレジストリから削除し events.db に BETA_EXTINCT として記録する"""
        to_remove = [
            bid for bid, e in self.breg.items()
            if not bid.startswith("_") and e.get("status") == "消滅"
        ]
        removed = []
        for bid in to_remove:
            entry = self.breg.pop(bid)
            removed.append({"beta_id": bid, "beta_ja": entry.get("beta_ja"),
                             "last_seen": entry.get("last_seen")})
            self._dirty = True
            self._record_extinct(bid, entry)

        return removed

    def _record_extinct(self, beta_id: str, entry: dict):
        """消滅βを events.db に記録する"""
        if not DB_PATH.exists():
            return
        try:
            con = sqlite3.connect(str(DB_PATH))
            eid = f"BETA_EXTINCT_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            con.execute(
                "INSERT OR IGNORE INTO events (event_id, title, what_type, when_ts) VALUES (?,?,?,?)",
                (eid, f"[BEE] β消滅: {entry.get('beta_ja')} ({beta_id})",
                 "BETA_EXTINCT", datetime.now().isoformat())
            )
            con.commit()
            con.close()
        except Exception:
            pass

    # ── 6. またか！ボタン連動 ────────────────────────────────────────────────

    def on_mataka_event(self, event_text: str):
        """
        「またか！」ボタンが押されたとき、
        構造タグと一致するβの evidence を +3 する。
        （博士が実証したパターン = 強い証拠）
        """
        import importlib.util
        morph_path = STRUCTURAL_DIR / "morphology.py"
        try:
            spec = importlib.util.spec_from_file_location("morphology", morph_path)
            morph = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(morph)
            result = morph.analyze(event_text)
            tags = set(result.get("structures", []))
        except Exception:
            tags = set()

        updated = []
        for bid, entry in self.breg.items():
            if bid.startswith("_"):
                continue
            tension_tags = set(self._extract_tags_from_tension(entry.get("tension", ""), "left"))
            if tension_tags & tags:
                self.breg[bid]["evidence"] = entry.get("evidence", 0) + 3
                self.breg[bid]["last_seen"] = datetime.now().strftime("%Y-%m-%d")
                self._dirty = True
                updated.append(bid)

        self._save()
        return updated

    # ── 7. PHI Decision DNA 双方向接続 ──────────────────────────────────────

    def on_phi_approved(self, beta_id: str):
        """judgement_reason で beta_id が approved → evidence +5"""
        if beta_id in self.breg:
            self.breg[beta_id]["evidence"] = self.breg[beta_id].get("evidence", 0) + 5
            self.breg[beta_id]["approved_by"] = "きむら博士 (PHI DNA)"
            self.breg[beta_id]["approved_at"] = datetime.now().strftime("%Y-%m-%d")
            self._dirty = True
            self._save()

    def on_phi_rejected(self, beta_id: str):
        """judgement_reason で beta_id が rejected → contradiction +5"""
        if beta_id in self.breg:
            self.breg[beta_id]["contradiction"] = self.breg[beta_id].get("contradiction", 0) + 5
            self._dirty = True
            self._save()

    # ── 8. 毎朝スキャン ──────────────────────────────────────────────────────

    def run_daily(self) -> dict:
        """
        MoCKA-START.bat から毎朝1回呼び出す。
        1. collect_evidence（全β）
        2. update_lifecycle（全β）
        3. detect_co_occurrence
        4. extract_meta_beta
        5. expire_extinct（90日消滅）
        6. mocka_write_event(BEE_DAILY_SCAN) で記録
        """
        beta_ids = [k for k in self.breg if not k.startswith("_")]
        scan_log = {"ts": datetime.now().isoformat(), "betas": {}}

        print(f"[BEE] 毎朝スキャン開始 ({len(beta_ids)}β)")

        # 1. evidence 収集
        for bid in beta_ids:
            r = self.collect_evidence(bid)
            scan_log["betas"][bid] = r
            print(f"  evidence: {bid} +{r.get('ev_added', 0)} / contra+{r.get('contra_added', 0)}")

        # 2. ライフサイクル更新
        lifecycle_changes = []
        for bid in beta_ids:
            old = self.breg.get(bid, {}).get("status", "観察β")
            new = self.update_lifecycle(bid)
            if old != new:
                lifecycle_changes.append({"beta_id": bid, "from": old, "to": new})
                print(f"  lifecycle: {bid} {old} → {new}")

        # 3. 共起検出
        self.detect_co_occurrence()

        # 4. Meta β
        meta_betas = self.extract_meta_beta()
        if meta_betas:
            for mb in meta_betas:
                print(f"  META β: {mb['meta_ja']} (source: {mb['source_betas']})")

        # 5. 消滅処理
        extinct = self.expire_extinct()
        if extinct:
            for e in extinct:
                print(f"  EXTINCT: {e['beta_ja']} ({e['beta_id']})")

        self._save()

        # 6. MoCKA 記録
        summary = (
            f"β:{len(beta_ids)} スキャン / ライフサイクル変化:{len(lifecycle_changes)} / "
            f"Meta β:{len(meta_betas)} / 消滅:{len(extinct)}"
        )
        self._write_event("BEE_DAILY_SCAN", summary, lifecycle_changes, meta_betas)

        print(f"[BEE] 完了: {summary}")
        return {
            "scan_log":          scan_log,
            "lifecycle_changes": lifecycle_changes,
            "meta_betas":        meta_betas,
            "extinct":           extinct,
        }

    def _write_event(self, event_type: str, description: str,
                      lifecycle_changes: list, meta_betas: list):
        """MoCKA MCP 経由でイベントを記録する（失敗しても続行）"""
        try:
            import urllib.request
            payload = json.dumps({
                "title":       f"[BEE] {event_type}: {description}",
                "description": description,
                "tags":        f"bee,{event_type.lower()},structural_intelligence",
                "why_purpose": "β Ecology ライフサイクル記録",
                "how_trigger": "bee.py run_daily",
            }).encode("utf-8")
            req = urllib.request.Request(
                MCP_URL, data=payload,
                headers={"Content-Type": "application/json"}, method="POST"
            )
            urllib.request.urlopen(req, timeout=3)
        except Exception:
            pass

    # ── 9. ステータス表示 ────────────────────────────────────────────────────

    def print_status(self):
        """現在のβライフサイクル一覧をコンソールに表示する"""
        betas = [(bid, e) for bid, e in self.breg.items() if not bid.startswith("_")]
        order = {"制度化": 0, "確立": 1, "成長中": 2, "観察β": 3, "衰退": 4, "消滅": 5}
        betas.sort(key=lambda x: order.get(x[1].get("status", "観察β"), 9))

        print("\n┌─────────────────────────────────────────────────────────────┐")
        print("│ 🧬 β ECOLOGY STATUS                                         │")
        print("├─────────────────────────────────────────────────────────────┤")
        for bid, e in betas:
            status = e.get("status", "観察β")
            ev     = e.get("evidence", 0)
            contra = e.get("contradiction", 0)
            total  = ev + contra
            pct    = int(ev / total * 100) if total > 0 else 0
            bar    = "█" * (pct // 8) + "░" * (12 - pct // 8)
            is_meta = "🌟" if e.get("is_meta") else "  "
            meta_label = f" → {e['meta_beta']}" if e.get("meta_beta") else ""
            print(f"│ {is_meta} {status:<6}  {e.get('beta_ja',''):<22} ev:{ev:<4} contra:{contra:<3} {bar} {pct}%{meta_label}")
        print("└─────────────────────────────────────────────────────────────┘\n")


# ─── CLI ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="β Ecology Engine (BEE)")
    parser.add_argument("--daily",    action="store_true", help="毎朝スキャン実行")
    parser.add_argument("--status",   action="store_true", help="βライフサイクル一覧表示")
    parser.add_argument("--evidence", metavar="BETA_ID",   help="evidence 手動追加対象のβID")
    parser.add_argument("--type",     default="support",   choices=["support", "contra"])
    parser.add_argument("--source",   default="manual",    help="evidence ソース")
    args = parser.parse_args()

    bee = BetaEcologyEngine()

    if args.daily:
        bee.run_daily()
    elif args.status:
        bee.print_status()
    elif args.evidence:
        bid = args.evidence
        if bid not in bee.breg:
            print(f"[BEE] β not found: {bid}")
            sys.exit(1)
        if args.type == "support":
            bee.breg[bid]["evidence"] = bee.breg[bid].get("evidence", 0) + 1
            print(f"[BEE] evidence +1 → {bid} (total: {bee.breg[bid]['evidence']})")
        else:
            bee.breg[bid]["contradiction"] = bee.breg[bid].get("contradiction", 0) + 1
            print(f"[BEE] contradiction +1 → {bid} (total: {bee.breg[bid]['contradiction']})")
        bee.update_lifecycle(bid)
        bee._dirty = True
        bee._save()
        bee.print_status()
    else:
        parser.print_help()
