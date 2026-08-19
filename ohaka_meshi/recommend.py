import requests

OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "qwen2.5:3b"
REQUEST_TIMEOUT = 120
# AIが一度に読める文章量の上限（トークン数）。Ollamaの既定値（2048程度）だと
# 記録が多いときに古い記録がこっそり読み飛ばされてしまうため、余裕を持たせて広げておく。
OLLAMA_NUM_CTX = 16384

SYSTEM_PROMPT = (
    "あなたは食事記録アプリ「お墓飯」のおすすめ機能です。ユーザーがこれまでに記録した"
    "「死んでもお供えしてほしいレベルで美味しかった料理」の一覧を見て、記録済みの料理を"
    "説明し直すのではなく、まだ記録していない・次に試すとよさそうな具体的な料理名を"
    "3〜5個、理由つきで提案してください。\n"
    "ルール:\n"
    "・「料理ジャンル」「甘味」のような大きすぎるくくりではなく、「オムライス」"
    "「担々麺」のように具体的な料理名にすること\n"
    "・実在するお店の名前は絶対に挙げないこと（存在しないお店をでっち上げるリスクが"
    "あるため）\n"
    "・理由は1文で、必ず「。」で終わる完全な文にすること。文の途中で終わらせないこと\n"
    "・下記の入力データにある「料理名:」「種別:」「店名:」のようなラベルや記号（／など）を"
    "出力にそのまま含めないこと\n"
    "・複数の提案で同じ理由の文をそのまま繰り返さず、それぞれの料理に合わせた理由にすること\n"
    "・前置きやまとめの文章、挨拶は書かず、下記の形式の行だけを出力すること\n\n"
    "各行は必ず次の形式にすること（区切り文字は半角の「|」で、料理をひと目でイメージ"
    "しやすい絵文字を1つだけ選ぶこと）:\n"
    "絵文字|料理名|理由\n\n"
    "出力形式の例（この例自体は出力しないこと）:\n"
    "🍳|オムライス|卵料理の記録が多く、洋食の中でも試していないジャンルなので楽しめ"
    "そうです。\n"
    "🌶️|担々麺|辛味のある麺料理を好む傾向があるため、次の一皿として合いそうです。\n\n"
    "上の例と同じ形式で、ユーザーの記録内容に沿った3〜5行を日本語で書いてください。"
)

DEFAULT_EMOJI = "🍽️"


def _format_entries(entries):
    lines = []
    for entry in entries:
        kind = "外食" if entry["is_eating_out"] else "内食"
        parts = [f"料理名={entry['dish_name']}", f"種別={kind}"]
        if entry["is_eating_out"] and entry["restaurant_name"]:
            parts.append(f"店名={entry['restaurant_name']}")
        if entry["is_eating_out"] and entry["location"]:
            parts.append(f"場所={entry['location']}")
        if entry["comment"]:
            parts.append(f"感想={entry['comment']}")
        lines.append("- " + "、".join(parts))
    return "\n".join(lines)


def _parse_line(line):
    line = line.strip().lstrip("・-*").strip()
    if not line:
        return None
    parts = [p.strip() for p in line.split("|")]
    if len(parts) == 3 and all(parts):
        emoji, dish_name, reason = parts
        return {"emoji": emoji, "dish_name": dish_name, "reason": reason}
    # モデルが指定フォーマットを外した場合も、行の内容自体は捨てずにそのまま表示する
    return {"emoji": DEFAULT_EMOJI, "dish_name": None, "reason": line}


def _parse_suggestions(text):
    return [s for s in (_parse_line(line) for line in text.splitlines()) if s]


def build_recommendation(entries):
    if not entries:
        return {"ok": False, "reason": "no_entries"}

    user_content = (
        "これまでの記録:\n" + _format_entries(entries) + "\n\nおすすめを提案してください。"
    )

    try:
        resp = requests.post(
            OLLAMA_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "stream": False,
                "options": {"num_predict": 500, "num_ctx": OLLAMA_NUM_CTX},
            },
            timeout=REQUEST_TIMEOUT,
        )
    except requests.exceptions.ConnectionError:
        return {"ok": False, "reason": "ollama_not_running"}
    except requests.exceptions.Timeout:
        return {"ok": False, "reason": "timeout"}
    except requests.exceptions.RequestException:
        return {"ok": False, "reason": "request_error"}

    if resp.status_code == 404:
        return {"ok": False, "reason": "model_not_found"}
    if resp.status_code != 200:
        return {"ok": False, "reason": "request_error"}

    try:
        text = resp.json()["message"]["content"].strip()
    except (ValueError, KeyError, TypeError):
        return {"ok": False, "reason": "request_error"}

    if not text:
        return {"ok": False, "reason": "request_error"}

    return {"ok": True, "text": text, "suggestions": _parse_suggestions(text)}
