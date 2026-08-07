# هذا هو المثال الأول لتصميم وكيل ذكي.
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

    # اعرض المجلدات أولاً، ثم الملفات، ورتّب الأسماء دون حساسية لحالة الأحرف.
    items = sorted(
        folder.iterdir(),
        key=lambda item: (item.is_file(), item.name.lower()),
    )

    results = []

    for item in items:
        item_type = "folder" if item.is_dir() else "file"

        results.append(f"[{item_type}] {item.name}")

    return "\n".join(results)


# The instructions define the agent's role and guardrails, while tools defines
# exactly which Python functions it is allowed to call.
# تحدد التعليمات دور الوكيل وضوابطه، بينما تحدد قائمة الأدوات بدقة دوال بايثون
# التي يُسمح له باستدعائها.
document_agent = Agent(
    name="Document Assistant",
    instructions=(
        "You help the user inspect files inside the folders. "
        "Use list_folder to list the contents of a folder. "
        "Never invent file names or file contents. "
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
        result = Runner.run_sync(document_agent, user_input)

        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
