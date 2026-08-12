# Example 3.1 | المثال 3.1

# This variant replaces the three separate file tools with one unrestricted cmd
# tool. It can execute any shell command, which makes it powerful and dangerous.
# يستبدل هذا المثال أدوات الملفات الثلاث بأداة cmd واحدة وغير مقيّدة. تستطيع
# تنفيذ أي أمر في النظام، وهذا يجعلها قوية وخطيرة.

import subprocess

from agents import Agent, Runner, SQLiteSession
from agents.decorators import tool
from dotenv import load_dotenv

load_dotenv()


@tool
def cmd(command: str) -> str:
    """Execute any command in the operating system shell."""

    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout

    if result.stderr:
        output += f"\nErrors:\n{result.stderr}"

    return f"Exit code: {result.returncode}\n{output}"


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
    tools=[cmd],
)


while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    result = Runner.run_sync(file_agent, user_input, session=session)
    print(f"Agent: {result.final_output}\n")
