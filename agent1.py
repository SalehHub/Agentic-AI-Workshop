from pathlib import Path
from dotenv import load_dotenv
from agents import Agent, Runner
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


document_agent = Agent(
    name="Document Assistant",
    instructions=(
        "You help the user inspect files inside the folders. "  #
        "Use list_folder to list the contents of a folder. "  #
        "Never invent file names or file contents. "  #
    ),
    tools=[list_folder],
)


def main():

    while True:

        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        result = Runner.run_sync(document_agent, user_input)

        print(f"Agent: {result.final_output}\n")


if __name__ == "__main__":
    main()
