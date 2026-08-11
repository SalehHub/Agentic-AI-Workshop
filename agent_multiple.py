# Example Seven | المثال السابع

# This example adds a tool for writing text files and a second agent that
# specializes in summarizing their contents.
# يضيف هذا المثال أداة لكتابة الملفات النصية ووكيلاً ثانياً متخصصاً في تلخيص
# محتواها.

from pathlib import Path

from dotenv import load_dotenv

from agents import Agent, Runner, SQLiteSession
from agents.decorators import tool

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


# This tool creates a UTF-8 text file without overwriting an existing file.
# تنشئ هذه الأداة ملفاً نصياً بترميز UTF-8 من دون استبدال ملف موجود.
@tool
def write_file(path: str, content: str) -> str:
    """Create a UTF-8 text file without overwriting an existing file."""

    file = Path(path).expanduser().resolve()

    if not file.parent.is_dir():
        return f"Folder not found: {file.parent}"

    try:
        with file.open("x", encoding="utf-8") as output_file:
            output_file.write(content)
    except FileExistsError:
        return f"Cannot write because this path already exists: {file}"
    except OSError as error:
        return f"Cannot write file: {file} ({error})"

    return f"Created file: {file}"


# The second agent has one focused responsibility: summarizing supplied content.
# للوكيل الثاني مسؤولية محددة: تلخيص المحتوى الذي يُرسل إليه.
summary_agent = Agent(
    name="File Summarizer",
    instructions=(
        "Summarize the supplied file contents clearly and accurately. "
        "Include the main topic and the most important points. "
        "Do not add information that is not present in the content. "
        "Use the same language as the supplied content when possible. "
    ),
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
    tools=[
        list_folder,
        read_file,
        rename_file,
        write_file,
        # An agent can become a tool that another agent calls for a focused task.
        # يمكن تحويل الوكيل إلى أداة يستدعيها وكيل آخر لتنفيذ مهمة محددة.
        summary_agent.as_tool(
            tool_name="summarize_file",
            tool_description=(
                "Summarize file contents after using read_file to read the file."
            ),
        ),
    ],
)


def main():
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = Runner.run_sync(file_agent, user_input, session=session)
        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
