import anthropic
import os

results = {
    "ChatGPT": "再現可能な信頼。",
    "Perplexity": "自律性。",
    "Gemini": "知識記録・AIガバナンスの基盤。",
    "Copilot": "人とAIが同じ歴史を共有し、未来を共同で決められる文明の核。"
}

prompt = f"""以下は「MoCKAという文明システムの最大の価値は何ですか？」という質問への各AIの回答です。

{chr(10).join([f"【{ai}】{ans}" for ai, ans in results.items()])}

これらを統合して、MoCKAの本質的価値を一段階深く分析してください。200字以内で。"""

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=500,
    messages=[{"role": "user", "content": prompt}]
)

print("=== Claude統合分析 ===")
print(response.content[0].text)
