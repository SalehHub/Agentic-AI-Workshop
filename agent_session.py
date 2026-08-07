# This example adds a persistent session to the previous agent. Its conversation
# history is stored on disk, so it remains available after the program closes.
# يضيف هذا المثال جلسة دائمة إلى الوكيل السابق. يُحفظ سجل المحادثة على القرص،
# لذلك يبقى متاحاً بعد إغلاق البرنامج وتشغيله مرة أخرى.

import os
from pathlib import Path

from dotenv import load_dotenv

from agents import Agent, Runner, SQLiteSession
from agents.decorators import tool

# Load variables from the .env file.
load_dotenv()


@tool
def list_folder(path: str = ".") -> str:

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


# SQLiteSession saves the conversation in history.db. Reusing the same
# session_id opens the same conversation; a different ID starts another one.
# تحفظ SQLiteSession المحادثة في history.db. يؤدي استخدام معرّف الجلسة نفسه
# إلى فتح المحادثة نفسها، بينما يبدأ المعرّف المختلف محادثة أخرى.
session = SQLiteSession(
    session_id="history",
    db_path="history.db",
)

document_agent = Agent(
    name="Document Assistant",
    instructions=(
        "You help the user inspect files inside the folders. "  #
        "Use list_folder to list the contents of a folder. "
        "Never invent file names or file contents. "
    ),
    tools=[list_folder],
)


def main():

    while True:

        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        # Passing the session loads earlier messages and saves the new exchange.
        # For example, the agent can recall your name after you close and reopen it.
        # عند تمرير الجلسة، تُحمّل الرسائل السابقة وتُحفظ المحادثة الجديدة. لذلك
        # يمكن للوكيل تذكّر اسمك حتى بعد إغلاقه وتشغيله مرة أخرى.
        result = Runner.run_sync(document_agent, user_input, session=session)

        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
