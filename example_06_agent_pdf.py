# Example Six | المثال السادس

# This example enhances read_file so it can read different text encodings,
# regular PDFs, and scanned PDFs that require OCR.
# يطوّر هذا المثال أداة read_file لتقرأ ترميزات نصية مختلفة وملفات PDF العادية
# وملفات PDF الممسوحة ضوئياً التي تحتاج إلى OCR.

from pathlib import Path

import pymupdf
import pytesseract
from chardet import detect
from dotenv import load_dotenv
from PIL import Image
from pypdf import PdfReader
from pypdf.errors import FileNotDecryptedError, PdfReadError
from pytesseract import TesseractNotFoundError

from agents import Agent, Runner, SQLiteSession
from agents.decorators import tool

load_dotenv()

MAX_CONTENT_CHARACTERS = 20_000
MAX_OCR_PAGES = 20


def _limit_content(content: str) -> str:
    if len(content) <= MAX_CONTENT_CHARACTERS:
        return content

    return (
        content[:MAX_CONTENT_CHARACTERS]
        + f"\n\n[Content truncated to {MAX_CONTENT_CHARACTERS} characters.]"
    )


def _read_text(file: Path) -> str:
    try:
        data = file.read_bytes()
    except OSError as error:
        return f"Cannot read text file: {file} ({error})"

    try:
        content = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        detected_encoding = detect(data).get("encoding")

        if detected_encoding is None:
            return f"Cannot detect the text encoding: {file}"

        try:
            content = data.decode(detected_encoding)
        except (LookupError, UnicodeDecodeError):
            return f"Cannot decode text file: {file}"

    if not content:
        return "The file is empty."

    return _limit_content(content)


def _text_quality(content: str) -> float:
    if not content:
        return 0

    words = content.split()
    alphabetic_ratio = sum(character.isalpha() for character in content) / len(
        content
    )
    unique_word_ratio = len(set(words)) / len(words) if words else 0
    return alphabetic_ratio + unique_word_ratio


def _ocr_pdf_pages(file: Path, page_numbers: list[int]) -> tuple[dict[int, str], str]:
    try:
        available_languages = set(pytesseract.get_languages(config=""))
    except TesseractNotFoundError:
        return {}, "OCR is unavailable because Tesseract is not installed."

    selected_languages = [
        language for language in ("ara", "eng") if language in available_languages
    ]

    if not selected_languages:
        return (
            {},
            "OCR is unavailable because no Arabic or English language data is installed.",
        )

    note = ""

    if "ara" not in available_languages:
        note = (
            "Arabic OCR language data is not installed; "
            "Arabic text may be inaccurate."
        )

    pages = {}

    try:
        with pymupdf.open(file) as document:
            for page_number in page_numbers[:MAX_OCR_PAGES]:
                page = document.load_page(page_number - 1)
                pixels = page.get_pixmap(
                    dpi=200,
                    colorspace=pymupdf.csRGB,
                    alpha=False,
                )
                image = Image.frombytes(
                    "RGB",
                    (pixels.width, pixels.height),
                    pixels.samples,
                )
                page_text = pytesseract.image_to_string(
                    image,
                    lang="+".join(selected_languages),
                ).strip()

                if page_text:
                    pages[page_number] = page_text
    except (OSError, RuntimeError) as error:
        return {}, f"OCR could not read this PDF ({error})."

    if len(page_numbers) > MAX_OCR_PAGES:
        note = (
            f"OCR stopped after {MAX_OCR_PAGES} pages to keep the request manageable."
        )

    return pages, note


def _read_pdf(file: Path) -> str:
    try:
        reader = PdfReader(file)
        extracted_pages = {}

        for page_number, page in enumerate(reader.pages, start=1):
            page_text = (page.extract_text() or "").strip()

            if page_text:
                extracted_pages[page_number] = page_text
    except FileNotDecryptedError:
        return f"Cannot read password-protected PDF: {file}"
    except (OSError, PdfReadError) as error:
        return f"Cannot read PDF file: {file} ({error})"

    # OCR also helps when a PDF contains a damaged or unreadable text layer.
    # يساعد OCR أيضاً عندما يحتوي ملف PDF على طبقة نص تالفة أو غير مقروءة.
    page_numbers = list(range(1, len(reader.pages) + 1))
    ocr_pages, ocr_note = _ocr_pdf_pages(file, page_numbers)
    pages = []

    for page_number in page_numbers:
        extracted_text = extracted_pages.get(page_number, "")
        ocr_text = ocr_pages.get(page_number, "")

        if _text_quality(ocr_text) > _text_quality(extracted_text) + 0.05:
            page_text = ocr_text
        else:
            page_text = extracted_text or ocr_text

        if page_text:
            pages.append(f"--- Page {page_number} ---\n{page_text}")

    if not pages:
        return ocr_note or "No readable text was found in this PDF."

    if ocr_note:
        pages.append(f"[OCR note: {ocr_note}]")

    return _limit_content("\n\n".join(pages))


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
    """Read text files and extract text from regular or scanned PDF files."""

    file = Path(path).expanduser().resolve()

    if not file.is_file():
        return f"File not found: {file}"

    if file.suffix.lower() == ".pdf":
        return _read_pdf(file)

    return _read_text(file)


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
    tools=[list_folder, read_file, rename_file],
)


while True:
    user_input = input("User: ")

    if user_input.lower() in ["exit", "quit"]:
        break

    result = Runner.run_sync(file_agent, user_input, session=session)
    print(f"Agent: {result.final_output}\n")
