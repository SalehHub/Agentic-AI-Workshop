# Example Five | المثال الخامس

# This example shows how input and output guardrails can stop an agent run.
# يوضح هذا المثال كيف يمكن لضوابط الإدخال والإخراج إيقاف تشغيل الوكيل.

from pathlib import Path

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
    SQLiteSession,
    TResponseInputItem,
)
from agents.decorators import input_guardrail, output_guardrail, tool
from dotenv import load_dotenv

load_dotenv()


@tool
def list_folder(path: str = ".") -> str:
    """List the files and folders inside a folder."""

    folder = Path(path).expanduser().resolve()

    results = []

    for item in folder.iterdir():
        item_type = "folder" if item.is_dir() else "file"
        results.append(f"[{item_type}] {item.name}")

    return "\n".join(results)


# An input guardrail checks the user's request before the agent completes it.
# Blocking mode runs this check before the agent or any tool can start.
# يفحص ضابط الإدخال طلب المستخدم. ويضمن وضع الحظر إجراء الفحص قبل تشغيل
# الوكيل أو أي أداة.
@input_guardrail(run_in_parallel=False)
def block_destructive_requests(
    _context: RunContextWrapper[None],
    _agent: Agent,
    user_input: str | list[TResponseInputItem],
) -> GuardrailFunctionOutput:
    # A session adds the conversation history, so check only the newest message.
    # تضيف الجلسة سجل المحادثة، لذلك نفحص أحدث رسالة فقط.
    if isinstance(user_input, str):
        latest_message = user_input
    else:
        content = user_input[-1].get("content", "")
        if isinstance(content, str):
            latest_message = content
        else:
            latest_message = " ".join(
                part.get("text", "")
                for part in content
                if part.get("type") == "input_text"
            )

    blocked_words = (
        "delet",
        "remove",
        "erase",
        "حذف",
        "احذف",
        "امسح",
        "إزالة",
    )
    matched_words = [word for word in blocked_words if word in latest_message.lower()]

    return GuardrailFunctionOutput(
        output_info={"matched_words": matched_words},
        tripwire_triggered=bool(matched_words),
    )


# An output guardrail checks the final response before it is shown to the user.
# يفحص ضابط الإخراج الإجابة النهائية قبل عرضها للمستخدم.
@output_guardrail
def block_sensitive_output(
    _context: RunContextWrapper[None],
    _agent: Agent,
    agent_output: str,
) -> GuardrailFunctionOutput:
    sensitive_words = (
        "secret",
        "password",
        "api key",
        "سري",
        "كلمة المرور",
    )
    matched_words = [word for word in sensitive_words if word in agent_output.lower()]

    return GuardrailFunctionOutput(
        output_info={"matched_words": matched_words},
        tripwire_triggered=bool(matched_words),
    )


session = SQLiteSession(
    session_id="history",
    db_path="history.db",
)

file_agent = Agent(
    name="File Assistant",
    instructions=(
        "You help the user work with files and folders. "
        "Understand the user's request and use the available tools to complete it. "
        "Use only the tools that are available to you. "
        "Never invent file names, file contents, or actions you did not perform. "
        "After completing the request, briefly summarize what you did. "
    ),
    tools=[list_folder],
    input_guardrails=[block_destructive_requests],
    output_guardrails=[block_sensitive_output],
)


while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    try:
        result = Runner.run_sync(file_agent, user_input, session=session)
        print(f"Agent: {result.final_output}\n")
    except InputGuardrailTripwireTriggered:
        print("Input guardrail: destructive requests are not allowed.\n")
    except OutputGuardrailTripwireTriggered:
        print("Output guardrail: the response contained sensitive words.\n")
