# Example 1.1 | المثال 1.1

# This example keeps the one-tool, no-memory agent from Example One and streams
# its response in the console as it is generated.
# يحتفظ هذا المثال بوكيل المثال الأول ذي الأداة الواحدة ومن دون ذاكرة، ويعرض
# إجابته تدريجياً في الطرفية أثناء إنشائها.

import asyncio
from pathlib import Path

from agents import Agent, Runner
from agents.decorators import tool
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent

load_dotenv()


@tool
def list_folder(path: str = ".") -> str:

    folder = Path(path).expanduser().resolve()

    results = []

    for item in folder.iterdir():
        item_type = "folder" if item.is_dir() else "file"

        results.append(f"[{item_type}] {item.name}")

    return "\n".join(results)


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


# run_streamed returns events while the model is producing the response.
# يعيد run_streamed الأحداث أثناء إنشاء النموذج للإجابة.
async def stream_response(user_input: str) -> None:
    result = Runner.run_streamed(file_agent, user_input)
    print("Agent: ", end="", flush=True)

    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(
            event.data,
            ResponseTextDeltaEvent,
        ):
            print(event.data.delta, end="", flush=True)

    print("\n")


while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    asyncio.run(stream_response(user_input))
