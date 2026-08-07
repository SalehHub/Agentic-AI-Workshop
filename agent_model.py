# Example Four | المثال الرابع

# This example builds on agent_tools.py and shows how to select a model and
# configure its behavior with ModelSettings.
# يعتمد هذا المثال على agent_tools.py ويوضح كيفية اختيار النموذج وضبط سلوكه
# باستخدام ModelSettings.

from pathlib import Path

from dotenv import load_dotenv
from openai.types.shared import Reasoning

from agents import Agent, ModelSettings, Runner
from agents.decorators import tool

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


@tool
def read_file(path: str) -> str:
    """Read and return the contents of a text file."""

    file = Path(path).expanduser().resolve()

    if not file.is_file():
        return f"File not found: {file}"

    try:
        return file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Cannot read this file as UTF-8 text: {file}"


@tool
def rename_file(path: str, new_name: str) -> str:
    """Rename a file without moving it to another folder."""

    file = Path(path).expanduser().resolve()

    if not file.is_file():
        return f"File not found: {file}"

    if not new_name or new_name in {".", ".."} or Path(new_name).name != new_name:
        return "The new name must be a file name without a folder path."

    new_file = file.with_name(new_name)

    if new_file == file:
        return f"The file already has this name: {new_name}"

    if new_file.suffix.lower() != file.suffix.lower():
        return f"The new name must keep the original extension: {file.suffix}"

    if new_file.exists():
        return f"Cannot rename because this file already exists: {new_file}"

    file.rename(new_file)
    return f"Renamed: {file.name} -> {new_file.name}"


# Active configuration: choose a GPT-5.6 model and how much reasoning it uses.
# الإعداد الفعّال: اختر نموذجاً من GPT-5.6 وحدد مقدار الاستدلال الذي يستخدمه.
# https://developers.openai.com/api/docs/models
SELECTED_MODEL = "gpt-5.6-sol"
SELECTED_MODEL_SETTINGS = ModelSettings(
    reasoning=Reasoning(effort="medium"),
)

# Temperature controls randomness and variation, not reasoning. Not every model
# supports it. To try a more creative configuration, comment out the active
# configuration above and uncomment these two lines:
# تتحكم temperature في العشوائية والتنوع، وليس الاستدلال، ولا تدعمها جميع
# النماذج. لتجربة إعداد أكثر إبداعاً، عطّل الإعداد السابق وفعّل السطرين التاليين:
# SELECTED_MODEL = "gpt-4.1"
# SELECTED_MODEL_SETTINGS = ModelSettings(temperature=0.9)


file_agent = Agent(
    name="File Assistant",
    instructions=(
        "You help the user work with files and folders. "
        "Understand the user's request and use the available tools to complete it. "
        "Use only the tools that are available to you. "
        "Never invent file names, file contents, or actions you did not perform. "
        "After completing the request, briefly summarize what you did. "
    ),
    model=SELECTED_MODEL,
    model_settings=SELECTED_MODEL_SETTINGS,
    tools=[list_folder, read_file, rename_file],
)


def main():
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = Runner.run_sync(file_agent, user_input)
        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
