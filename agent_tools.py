# This example adds two tools to the first agent: one reads file contents, and
# the other renames files. The agent uses all three tools to organize a folder.
# يضيف هذا المثال أداتين إلى الوكيل الأول: أداة لقراءة محتوى الملفات، وأخرى
# لإعادة تسميتها. يستخدم الوكيل الأدوات الثلاث لتنظيم ملفات أحد المجلدات.

from pathlib import Path

from dotenv import load_dotenv

from agents import Agent, Runner
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


# This new tool lets the agent inspect a file before choosing its new name.
# تتيح هذه الأداة الجديدة للوكيل قراءة الملف قبل اختيار اسمه الجديد.
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


# This new tool changes only the file name and keeps it in the same folder.
# تغيّر هذه الأداة الجديدة اسم الملف فقط وتُبقيه داخل المجلد نفسه.
@tool
def rename_file(path: str, new_name: str) -> str:
    """Rename a file without moving it to another folder."""

    file = Path(path).expanduser().resolve()

    if not file.is_file():
        return f"File not found: {file}"

    # Accept a file name only, not another path.
    # نقبل اسم ملف فقط، وليس مساراً جديداً.
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


file_organizer_agent = Agent(
    name="File Organizer",
    instructions=(
        "The user will give you the path of a folder. "
        "Your job is to rename the files in that folder based on their content. "
        "First, use list_folder to find the files. "
        "Use read_file to read each file before choosing its new name. "
        "Use rename_file to give each file a short, descriptive name. "
        "Always preserve the original file extension. "
        "Do not rename folders or overwrite existing files. "
        "Only work inside the folder provided by the user. "
        "After finishing, summarize the old and new file names. "
    ),
    tools=[list_folder, read_file, rename_file],
)


def main():
    while True:
        user_input = input("User: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        result = Runner.run_sync(file_organizer_agent, user_input)
        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
