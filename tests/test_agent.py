"""エージェントの配線テスト。

TestModel は実際のLLMを呼ばない偽モデルで、登録されたツールを全部呼んでから
ダミーの回答を返す。APIキーも利用枠も使わずに、
「ツールが登録され、呼ばれ、結果がモデルに戻るか」を確かめられる。
"""

from pydantic_ai import DeferredToolRequests
from pydantic_ai.messages import ToolCallPart, ToolReturnPart
from pydantic_ai.models.test import TestModel

from app.agent import agent, request_tool_approvals, run_chat, run_prompt

BASE_TOOLS = {"search_glossary", "get_lecture_summary"}


def _parts(result, kind):
    return [p for m in result.all_messages() for p in m.parts if isinstance(p, kind)]


def test_base_tools_are_registered_and_called():
    model = TestModel()
    with agent.override(model=model):
        result = agent.run_sync("LoRAとは？")

    offered = {t.name for t in model.last_model_request_parameters.function_tools}
    assert BASE_TOOLS <= offered  # 演習でツールを足しても壊れないよう「含む」で判定

    called = {p.tool_name for p in _parts(result, ToolCallPart)}
    assert BASE_TOOLS <= called
    # 承認が必要なツール（requires_approval=True）は、実行されずに承認待ちになるので戻り値が無い
    waiting = len(result.output.approvals) if isinstance(result.output, DeferredToolRequests) else 0
    assert len(_parts(result, ToolReturnPart)) + waiting == len(_parts(result, ToolCallPart))
    assert result.output


def test_glossary_result_reaches_the_model():
    model = TestModel(call_tools=["search_glossary"])
    with agent.override(model=model):
        result = agent.run_sync("RAGとは？")
    returns = _parts(result, ToolReturnPart)
    assert returns and returns[0].tool_name == "search_glossary"


def test_deferred_tool_request_can_be_approved(monkeypatch):
    model = TestModel(call_tools=["save_learning_log"])
    with agent.override(model=model):
        result = agent.run_sync("この会話を学習ログに保存して")

    assert isinstance(result.output, DeferredToolRequests)
    call = result.output.approvals[0]
    prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: prompts.append(prompt) or "はい")

    deferred_results = request_tool_approvals(result.output)

    assert deferred_results.approvals == {call.tool_call_id: True}
    assert call.tool_name in prompts[0]


def test_run_prompt_approves_and_resumes_deferred_tool(monkeypatch, tmp_path):
    model = TestModel(call_tools=["save_learning_log"])
    monkeypatch.setattr("builtins.input", lambda _: "はい")
    log_path = tmp_path / "learning_log.md"
    monkeypatch.setattr("app.agent.tools.LOG_DIR", tmp_path)
    monkeypatch.setattr("app.agent.tools.LOG_PATH", log_path)

    with agent.override(model=model):
        result = run_prompt(agent, "学習ログを保存して", model)

    assert result.output
    assert "質問 a" in log_path.read_text(encoding="utf-8")


def test_chat_carries_history_between_turns(monkeypatch):
    class Result:
        def __init__(self, output, messages):
            self.output = output
            self.messages = messages

        def all_messages(self):
            return self.messages

    class Target:
        def __init__(self):
            self.calls = []

        def run_sync(self, prompt, *, model, message_history=None):
            self.calls.append((prompt, message_history, model))
            messages = list(message_history or [])
            messages.extend([("user", prompt), ("assistant", f"回答: {prompt}")])
            return Result(f"回答: {prompt}", messages)

    prompts = iter(["LoRAとは何ですか？", "それは何に使いますか？", "終了"])
    monkeypatch.setattr("builtins.input", lambda _: next(prompts))
    target = Target()

    run_chat(target, model=object())

    assert target.calls[0][:2] == ("LoRAとは何ですか？", [])
    assert target.calls[1][:2] == (
        "それは何に使いますか？",
        [
            ("user", "LoRAとは何ですか？"),
            ("assistant", "回答: LoRAとは何ですか？"),
        ],
    )


def test_chat_saves_previous_learning_turn_after_approval(monkeypatch):
    class Result:
        def __init__(self, output, messages):
            self.output = output
            self.messages = messages

        def all_messages(self):
            return self.messages

    class Target:
        def __init__(self):
            self.calls = []
            self.tool_call = ToolCallPart(
                tool_name="save_learning_log",
                args={
                    "question": "LoRAとは何ですか？",
                    "answer": "LoRAは追加学習のパラメータを減らす手法です。",
                },
                tool_call_id="save-log-1",
            )

        def run_sync(
            self, prompt=None, *, model, message_history=None, deferred_tool_results=None
        ):
            assert model is not None
            self.calls.append((prompt, message_history, deferred_tool_results))
            if deferred_tool_results is not None:
                return Result("保存しました", ["resumed"])
            if prompt == "LoRAとは何ですか？":
                return Result(
                    "LoRAは追加学習のパラメータを減らす手法です。",
                    ["question", "answer"],
                )
            messages = list(message_history or []) + ["save request"]
            return Result(DeferredToolRequests(approvals=[self.tool_call]), messages)

    inputs = iter(["LoRAとは何ですか？", "学習ログを保存して", "はい", "終了"])
    approval_prompts = []
    monkeypatch.setattr("builtins.input", lambda prompt: approval_prompts.append(prompt) or next(inputs))
    target = Target()

    run_chat(target, model=object())

    assert [call[0] for call in target.calls] == [
        "LoRAとは何ですか？",
        "学習ログを保存して",
        None,
    ]
    assert target.calls[1][1] == ["question", "answer"]
    assert target.calls[2][1] == ["question", "answer", "save request"]
    assert target.calls[2][2].approvals == {"save-log-1": True}
    assert "save_learning_log" in approval_prompts[2]
