# Example One | المثال الأول

# هذا هو المثال الأول لتصميم وكيل الذكاء الاصطناعي.
# يمتلك الوكيل أداة واحدة فقط لاستعراض محتويات المجلدات، ولا يحتفظ بأي ذاكرة
# بين المحادثات. سننشئ في ملفات لاحقة وكلاء بقدرات وأدوات ووظائف أكثر.

from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
from agents.decorators import tool

# Load API keys and other configuration from the local .env file.
# .env تحميل مفاتيح الاتصال والإعدادات من ملف البيئة المحلي.
load_dotenv()


# Register this function as the agent's only callable tool.
# تسجيل هذه الدالة لتكون الأداة الوحيدة التي يستطيع الوكيل استدعاءها.
@tool
def list_folder(path: str = ".") -> str:

    # Expand "~" and resolve relative paths before accessing the folder.
    folder = Path(path).expanduser().resolve()

    results = []

    for item in folder.iterdir():
        item_type = "folder" if item.is_dir() else "file"

        results.append(f"[{item_type}] {item.name}")

    return "\n".join(results)


# The instructions define the agent's role and guardrails, while tools defines
# exactly which Python functions it is allowed to call.
# تحدد التعليمات دور الوكيل وضوابطه، بينما تحدد قائمة الأدوات بدقة دوال بايثون
# التي يُسمح له باستدعائها.
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
)


def main():

    # حلقة تفاعلية بسيطة تستقبل طلبات المستخدم من الطرفية.
    while True:

        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # No session or conversation history is passed here, so every request
        # is independent and the agent has no memory of earlier requests.
        # لا نمرر جلسة أو سجل محادثة هنا، لذلك يُعامل كل طلب بشكل مستقل، ولا
        # يتذكر الوكيل أي طلبات سابقة.
        result = Runner.run_sync(file_agent, user_input)

        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
