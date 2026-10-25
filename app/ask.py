"""第1回: Gemini API と会話するスクリプト。

使い方:
    uv run python -m app.ask "LoRAとは何ですか？"
    uv run python -m app.ask            # 質問を省略すると、講座に固有の質問から始める

ツールは使わない「素の」呼び出し。起動中は会話履歴を保持する。
講座に固有のことを聞くと、「分からない」と答えるか、一般論でもっともらしく答える
（講座の実際とは違う）ことを確かめよう。
（第3回で、用語集を検索できるエージェントにして改善する）
"""

import argparse
import time

from google import genai
from google.genai import errors

from app.config import MODEL, api_error_message, get_api_key

# 講座に固有の質問。正しい答えは data/glossary.json の homework-levels にある
DEFAULT_QUESTION = "AIE2026の講座の宿題にある「3レベル」とは何ですか？"


def main() -> None:
    parser = argparse.ArgumentParser(description="素のLLMに質問する")
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    args = parser.parse_args()

    print(f"[model] {MODEL}")
    client = genai.Client(api_key=get_api_key())
    chat = client.chats.create(model=MODEL)
    question = args.question

    try:
        while True:
            print(f"[質問] {question}")
            started_at = time.perf_counter()
            response = chat.send_message(question)
            elapsed = time.perf_counter() - started_at
            usage = response.usage_metadata
            if usage is not None:
                print(
                    f"[usage] 入力: {usage.prompt_token_count} tokens, "
                    f"出力: {usage.candidates_token_count} tokens"
                )
            print(f"[応答時間] {elapsed:.2f} 秒")
            print(f"AI: {response.text}")

            while True:
                question = input("あなた: ").strip()
                if question.lower() in {"exit", "quit"}:
                    return
                if question:
                    break
    except errors.APIError as e:
        print(api_error_message(e.code, e.message))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
