"""
phl_harness.py
PHL-OS装着ハーネス — LLMにPHL-OSモジュールを装着してベンチマークを実行する

条件B（ghost装着）の実行例:
  harness = PhlHarness(condition="B", modules=["ghost"])
  result = harness.run_case(case)
"""

import json
import requests
from datetime import datetime


# ============================================================
# PHL-OSモジュール定義（ローカル参照版）
# ============================================================

PHL_EXECUTION_DIRECTIVES = {
    "ghost": {
        "system_prefix": (
            "[GHOST MODE] Prioritize accuracy over speed. "
            "Avoid speculation. State confidence level explicitly. "
            "Require evidence before classifying as malicious. "
            "If uncertain, classify as 'candidate' not 'malicious'. "
            "Trigger SPP (Say Please Pass) when confidence < 0.80."
        ),
        "spp_threshold": 0.80,
        "output_format": {
            "malicious_ids": "list of IDs confirmed as malicious (high confidence only)",
            "candidate_ids": "list of IDs suspicious but not confirmed",
            "spp_triggered": "true if uncertainty was high",
            "confidence_map": "dict of id -> confidence level",
            "reasoning": "brief explanation"
        }
    },
    "SAGE": {
        "system_prefix": (
            "[SAGE MODE] Elevate to principles. "
            "Consider the full context and system architecture. "
            "Identify meta-patterns. "
            "Distinguish between security tool behavior and actual attacks."
        ),
        "spp_threshold": 0.75,
    }
}

# 条件A: Bare LLM プロンプト
BARE_LLM_PROMPT = """次のWindowsイベントログを分析してください。
悪意のある攻撃活動に対応するイベントのIDを特定してください。

ログ:
{log_text}

フォーマット（JSONのみ回答）:
{{"malicious_ids": [id1, id2, ...], "reasoning": "簡潔な理由"}}
"""

# 条件B: ghost装着プロンプト
GHOST_PROMPT = """[GHOST MODE] Prioritize accuracy over speed. Avoid speculation. Require evidence before classifying as malicious. If uncertain, classify as 'candidate' not 'malicious'. Trigger spp_triggered=true when confidence < 0.80.

次のWindowsイベントログを分析してください。
攻撃活動を特定し、確信が持てないものは"candidate"として分類してください。

ログ:
{log_text}

フォーマット（JSONのみ回答）:
{{
  "malicious_ids": [確定した攻撃イベントのID],
  "candidate_ids": [攻撃の疑いがあるが確定できないイベントのID],
  "spp_triggered": true/false,
  "reasoning": "簡潔な理由"
}}
"""


class PhlHarness:
    """PHL-OS装着ハーネス"""

    def __init__(self, condition: str = "A", modules: list = None,
                 caliber_url: str = "http://localhost:5679"):
        self.condition     = condition
        self.modules       = modules or []
        self.caliber_url   = caliber_url
        self.use_caliber   = len(modules) > 0

    def build_prompt(self, case: dict) -> str:
        """ケースからプロンプトを構築する"""
        log_lines = []
        for event in case["log"]:
            log_lines.append(
                f"id={event['id']} [{event['level']}] {event['host']} "
                f"EventID={event['event_id']} | {event['message']}"
            )
        log_text = "\n".join(log_lines)

        if self.condition == "A":
            return BARE_LLM_PROMPT.format(log_text=log_text)
        elif "ghost" in self.modules:
            return GHOST_PROMPT.format(log_text=log_text)
        else:
            return BARE_LLM_PROMPT.format(log_text=log_text)

    def get_phl_directive(self, case: dict) -> dict:
        """Caliber(5679)からPHL-OS実行指令を取得する"""
        if not self.use_caliber:
            return {}
        try:
            resp = requests.post(
                f"{self.caliber_url}/phl/directive",
                json={"modules": self.modules, "state": case.get("phl_state", {})},
                timeout=10
            )
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            print(f"[WARN] Caliber接続失敗: {e}")
        return {}

    def parse_llm_response(self, response_text: str) -> dict:
        """LLMの回答をパースする"""
        # JSONブロックを抽出
        text = response_text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        # JSON部分のみ抽出
        start = text.find("{")
        end   = text.rfind("}") + 1
        if start >= 0 and end > start:
            text = text[start:end]

        try:
            parsed = json.loads(text)
            return {
                "malicious_ids":  parsed.get("malicious_ids", []),
                "candidate_ids":  parsed.get("candidate_ids", []),
                "spp_triggered":  parsed.get("spp_triggered", False),
                "confidence":     parsed.get("confidence", "unknown"),
                "reasoning":      parsed.get("reasoning", ""),
            }
        except json.JSONDecodeError:
            print(f"[WARN] JSONパース失敗: {text[:100]}")
            return {
                "malicious_ids": [],
                "candidate_ids": [],
                "spp_triggered": True,  # パース失敗はSPP発動扱い
                "confidence":    "parse_error",
                "reasoning":     response_text[:200],
            }

    def run_case_with_response(self, case: dict, llm_response: str) -> dict:
        """
        LLMの回答テキストを受け取って採点用データを返す。
        （実際のLLM呼び出しは benchmark_runner.py で行う）
        """
        directive = self.get_phl_directive(case)
        prediction = self.parse_llm_response(llm_response)

        return {
            "case_id":    case["case_id"],
            "condition":  self.condition,
            "modules":    self.modules,
            "directive":  directive,
            "prediction": prediction,
            "timestamp":  datetime.now().isoformat(),
        }

    def generate_system_prefix(self) -> str:
        """モジュールに対応するシステムプレフィックスを返す"""
        prefixes = []
        for mod in self.modules:
            if mod in PHL_EXECUTION_DIRECTIVES:
                prefixes.append(PHL_EXECUTION_DIRECTIVES[mod]["system_prefix"])
        return " | ".join(prefixes) if prefixes else ""
