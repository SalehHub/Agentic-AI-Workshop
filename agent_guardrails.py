# Example Five | المثال الخامس

# This example shows how input and output guardrails can stop an agent run.
# يوضح هذا المثال كيف يمكن لضوابط الإدخال والإخراج إيقاف تشغيل الوكيل.

from pathlib import Path

from dotenv import load_dotenv

from agents import (
    Agent,
    GuardrailFunctionOutput,
    InputGuardrailTripwireTriggered,
    OutputGuardrailTripwireTriggered,
    RunContextWrapper,
    Runner,
)
from agents.decorators import input_guardrail, output_guardrail, tool

# Load API keys and other configuration from the local .env file.
# تحميل مفاتيح الاتصال والإعدادات من ملف البيئة المحلي .env.
load_dotenv()


@tool
def list_folder(path: str = ".") -> str:
    """List the files and folders inside a folder."""

    folder = Path(path).expanduser().resolve()

    items = sorted(
        folder.iterdir(),
        key=lambda item: (item.is_file(), item.name.lower()),
    )

    results = []

    for item in items:
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
    user_input: str,
) -> GuardrailFunctionOutput:
    blocked_words = (
        "delete",
        "remove",
        "erase",
        "حذف",
        "احذف",
        "امسح",
        "إزالة",
    )
    matched_words = [word for word in blocked_words if word in user_input.lower()]

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


def main():
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            result = Runner.run_sync(file_agent, user_input)
            print(f"Agent: {result.final_output}\n")
        except InputGuardrailTripwireTriggered:
            print("Input guardrail: destructive requests are not allowed.\n")
        except OutputGuardrailTripwireTriggered:
            print("Output guardrail: the response contained sensitive words.\n")


if __name__ == "__main__":
    main()
