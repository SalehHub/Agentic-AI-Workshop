# Example Eight | المثال الثامن

# This final example gives the file agent a desktop chat interface. Users can
# attach paths, create saved conversations, and watch responses stream live.
# يمنح هذا المثال الأخير وكيل الملفات واجهة محادثة مكتبية. يمكن للمستخدم إرفاق
# المسارات وإنشاء عدة محادثات محفوظة ومشاهدة الإجابات تظهر مباشرة.

import asyncio
import json
import sqlite3
from pathlib import Path
from uuid import uuid4

from agents import Agent, Runner, SQLiteSession
from agents.decorators import tool
from dotenv import load_dotenv
from openai.types.responses import ResponseTextDeltaEvent
from PySide6.QtCore import QDir, Qt, QThread, QTimer, Signal
from PySide6.QtGui import QKeyEvent, QTextCursor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileSystemModel,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

load_dotenv()

DATABASE_PATH = Path(__file__).with_name("gui_history.db")


@tool
def list_folder(path: str = ".") -> str:
    """List the files and folders inside a folder."""

    folder = Path(path).expanduser().resolve()

    if not folder.is_dir():
        return f"Folder not found: {folder}"

    results = []

    for item in folder.iterdir():
        item_type = "folder" if item.is_dir() else "file"
        results.append(f"[{item_type}] {item.name}")

    return "\n".join(results)


@tool
def read_file(path: str) -> str:
    """Read and return the contents of a UTF-8 text file."""

    file = Path(path).expanduser().resolve()

    if not file.is_file():
        return f"File not found: {file}"

    try:
        return file.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return f"Cannot read this file as UTF-8 text: {file}"
    except OSError as error:
        return f"Cannot read file: {file} ({error})"


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


summary_agent = Agent(
    name="File Summarizer",
    instructions=(
        "Summarize the supplied file contents clearly and accurately. "
        "Include the main topic and the most important points. "
        "Do not add information that is not present in the content. "
        "Use the same language as the supplied content when possible. "
    ),
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
        summary_agent.as_tool(
            tool_name="summarize_file",
            tool_description=(
                "Summarize file contents after using read_file to read the file."
            ),
        ),
    ],
)


def initialize_database() -> None:
    setup_session = SQLiteSession("setup", db_path=DATABASE_PATH)
    setup_session.close()

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS gui_conversations (
                session_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def create_conversation() -> str:
    session_id = uuid4().hex

    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO agent_sessions (session_id) VALUES (?)",
            (session_id,),
        )
        connection.execute(
            "INSERT INTO gui_conversations (session_id, title) VALUES (?, ?)",
            (session_id, "New Conversation"),
        )

    return session_id


def get_conversations() -> list[tuple[str, str]]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        return connection.execute(
            """
            SELECT session_id, title
            FROM gui_conversations
            ORDER BY updated_at DESC
            """
        ).fetchall()


def delete_conversation(session_id: str) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "DELETE FROM agent_messages WHERE session_id = ?",
            (session_id,),
        )
        connection.execute(
            "DELETE FROM gui_conversations WHERE session_id = ?",
            (session_id,),
        )
        connection.execute(
            "DELETE FROM agent_sessions WHERE session_id = ?",
            (session_id,),
        )


def update_conversation(session_id: str, title: str | None = None) -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        if title is None:
            connection.execute(
                """
                UPDATE gui_conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
                """,
                (session_id,),
            )
        else:
            connection.execute(
                """
                UPDATE gui_conversations
                SET title = ?, updated_at = CURRENT_TIMESTAMP
                WHERE session_id = ?
                """,
                (title, session_id),
            )


def get_messages(session_id: str) -> list[tuple[str, str]]:
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute(
            """
            SELECT message_data
            FROM agent_messages
            WHERE session_id = ?
            ORDER BY id
            """,
            (session_id,),
        ).fetchall()

    messages = []

    for (message_data,) in rows:
        try:
            item = json.loads(message_data)
        except json.JSONDecodeError:
            continue

        role = item.get("role")

        if role not in {"user", "assistant"}:
            continue

        content = item.get("content", "")

        if isinstance(content, str):
            text = content
        else:
            text = "\n".join(
                part.get("text", "")
                for part in content
                if part.get("type") in {"input_text", "output_text"}
            )

        if text:
            messages.append((role, text))

    return messages


class MessageInput(QPlainTextEdit):
    send_requested = Signal()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            event.key() in {Qt.Key.Key_Return, Qt.Key.Key_Enter}
            and event.modifiers() & Qt.KeyboardModifier.ControlModifier
        ):
            self.send_requested.emit()
            return

        super().keyPressEvent(event)


class PathPickerDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Attach files or folders | إرفاق ملفات أو مجلدات")
        self.resize(760, 500)

        self.file_model = QFileSystemModel(self)
        self.file_model.setFilter(
            QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot
        )
        self.file_model.setRootPath(QDir.rootPath())

        self.file_tree = QTreeView()
        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(self.file_model.index(QDir.rootPath()))
        self.file_tree.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.file_tree.setColumnWidth(0, 380)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText(
            "Attach selected | إرفاق المحدد"
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self.file_tree)
        layout.addWidget(buttons)

    def selected_paths(self) -> list[str]:
        selected_rows = self.file_tree.selectionModel().selectedRows(0)
        return [self.file_model.filePath(index) for index in selected_rows]


class AgentWorker(QThread):
    response_delta = Signal(str)
    response_ready = Signal(str)
    request_failed = Signal(str)

    def __init__(self, session_id: str, agent_input: str) -> None:
        super().__init__()
        self.session_id = session_id
        self.agent_input = agent_input

    def run(self) -> None:
        session = SQLiteSession(self.session_id, db_path=DATABASE_PATH)

        try:
            asyncio.run(self.stream_response(session))
        except Exception as error:  # noqa: BLE001
            self.request_failed.emit(str(error))
        finally:
            session.close()

    async def stream_response(self, session: SQLiteSession) -> None:
        # Each text delta is sent to the GUI while the complete result is saved.
        # يُرسل كل جزء نصي إلى الواجهة، ثم تُحفظ النتيجة الكاملة في الجلسة.
        result = Runner.run_streamed(
            file_agent,
            self.agent_input,
            session=session,
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(
                event.data,
                ResponseTextDeltaEvent,
            ):
                self.response_delta.emit(event.data.delta)

        self.response_ready.emit(str(result.final_output or ""))


class AgentWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.current_session_id = ""
        self.worker: AgentWorker | None = None
        self.streaming_message_label: QLabel | None = None
        self.streaming_response = ""

        self.setWindowTitle("File Assistant | مساعد الملفات")
        self.resize(1100, 720)

        self.conversation_list = QListWidget()
        self.conversation_list.currentItemChanged.connect(self.open_conversation)
        self.conversation_list.setContextMenuPolicy(
            Qt.ContextMenuPolicy.CustomContextMenu
        )
        self.conversation_list.customContextMenuRequested.connect(
            self.show_conversation_menu
        )

        self.new_chat_button = QPushButton("+ New Chat | محادثة جديدة")
        self.new_chat_button.clicked.connect(self.new_conversation)

        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.addWidget(self.new_chat_button)
        sidebar_layout.addWidget(self.conversation_list)

        self.chat_history = QScrollArea()
        self.chat_history.setWidgetResizable(True)
        self.chat_history.setFrameShape(QFrame.Shape.NoFrame)

        self.chat_messages = QWidget()
        self.chat_messages.setObjectName("chatMessages")
        self.chat_messages_layout = QVBoxLayout(self.chat_messages)
        self.chat_messages_layout.setContentsMargins(16, 16, 16, 16)
        self.chat_messages_layout.setSpacing(12)
        self.chat_messages_layout.addStretch()
        self.chat_history.setWidget(self.chat_messages)

        self.message_input = MessageInput()
        self.message_input.setPlaceholderText(
            "Write a message... | اكتب رسالتك...\nCtrl+Enter to send | للإرسال Ctrl+Enter"
        )
        self.message_input.setMaximumHeight(110)
        self.message_input.send_requested.connect(self.send_message)

        self.attach_button = QPushButton("Attach | إرفاق")
        self.attach_button.clicked.connect(self.pick_paths)

        self.send_button = QPushButton("Send | إرسال")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.send_message)

        attachment_buttons = QHBoxLayout()
        attachment_buttons.addWidget(self.attach_button)
        attachment_buttons.addStretch()

        input_row = QHBoxLayout()
        input_row.addWidget(self.message_input)
        input_row.addWidget(self.send_button)

        chat_panel = QWidget()
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.addWidget(self.chat_history)
        chat_layout.addLayout(attachment_buttons)
        chat_layout.addLayout(input_row)

        splitter = QSplitter()
        splitter.addWidget(sidebar)
        splitter.addWidget(chat_panel)
        splitter.setSizes([260, 840])

        self.setCentralWidget(splitter)
        self.apply_styles()
        self.refresh_conversations()

    def apply_styles(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background: #f7f7f8;
                color: #202123;
                font-family: Arial;
                font-size: 14px;
            }
            QListWidget, QPlainTextEdit {
                background: white;
                border: 1px solid #d9d9e3;
                border-radius: 8px;
                padding: 8px;
            }
            QScrollArea {
                background: white;
                border: 1px solid #d9d9e3;
                border-radius: 8px;
            }
            QWidget#chatMessages {
                background: white;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #e7f3ef;
                color: #202123;
            }
            QPushButton {
                background: white;
                border: 1px solid #c7c7d1;
                border-radius: 7px;
                padding: 9px 12px;
            }
            QPushButton:hover {
                background: #eeeeF2;
            }
            QPushButton:disabled {
                color: #9a9aa1;
                background: #ececf1;
            }
            QPushButton#sendButton {
                background: #10a37f;
                color: white;
                border: none;
                min-width: 90px;
            }
            """
        )

    def refresh_conversations(self, selected_id: str | None = None) -> None:
        self.conversation_list.blockSignals(True)
        self.conversation_list.clear()

        conversations = get_conversations()

        if not conversations:
            selected_id = create_conversation()
            conversations = get_conversations()

        selected_row = 0

        for row, (session_id, title) in enumerate(conversations):
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, session_id)
            self.conversation_list.addItem(item)

            if session_id == selected_id:
                selected_row = row

        self.conversation_list.blockSignals(False)
        self.conversation_list.setCurrentRow(selected_row)

        if self.conversation_list.currentItem() is not None:
            self.open_conversation(self.conversation_list.currentItem())

    def new_conversation(self) -> None:
        session_id = create_conversation()
        self.message_input.clear()
        self.refresh_conversations(session_id)

    def show_conversation_menu(self, position) -> None:
        item = self.conversation_list.itemAt(position)

        if item is None:
            return

        menu = QMenu(self)
        delete_action = menu.addAction("Delete Chat | حذف المحادثة")
        selected_action = menu.exec(
            self.conversation_list.viewport().mapToGlobal(position)
        )

        if selected_action == delete_action:
            self.delete_selected_conversation(item)

    def delete_selected_conversation(self, item: QListWidgetItem) -> None:
        session_id = item.data(Qt.ItemDataRole.UserRole)
        answer = QMessageBox.question(
            self,
            "Delete Chat | حذف المحادثة",
            "Permanently delete this conversation and all its messages?\n"
            "هل تريد حذف هذه المحادثة وجميع رسائلها نهائياً؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        delete_conversation(session_id)
        self.message_input.clear()
        self.current_session_id = ""
        self.refresh_conversations()

    def open_conversation(
        self,
        current: QListWidgetItem | None,
        _previous: QListWidgetItem | None = None,
    ) -> None:
        if current is None:
            return

        self.current_session_id = current.data(Qt.ItemDataRole.UserRole)
        self.clear_chat()

        for role, text in get_messages(self.current_session_id):
            self.add_message(role, text)

    def clear_chat(self) -> None:
        while self.chat_messages_layout.count() > 1:
            item = self.chat_messages_layout.takeAt(0)

            if item.widget() is not None:
                item.widget().deleteLater()

    def add_message(self, role: str, text: str) -> QLabel:
        if role == "user":
            label = "You | أنت"
            color = "#e7f3ef"
            border_color = "#c9e5dc"
            alignment = "right"
        else:
            label = "Agent | الوكيل"
            color = "#f0f0f4"
            border_color = "#dcdce4"
            alignment = "left"

        bubble = QFrame()
        bubble.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Preferred,
        )
        bubble.setStyleSheet(
            f"""
            QFrame {{
                background: {color};
                border: 1px solid {border_color};
                border-radius: 14px;
            }}
            QLabel {{
                background: transparent;
                border: none;
            }}
            """
        )

        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(16, 12, 16, 12)
        bubble_layout.setSpacing(5)

        sender_label = QLabel(label)
        sender_label.setStyleSheet("font-weight: bold;")

        message_label = QLabel(text)
        message_label.setTextFormat(Qt.TextFormat.PlainText)
        message_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        message_label.setWordWrap(True)
        message_label.setMaximumWidth(600)

        bubble_layout.addWidget(sender_label)
        bubble_layout.addWidget(message_label)

        message_row = QWidget()
        message_row.setStyleSheet("background: transparent;")
        row_layout = QHBoxLayout(message_row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        if alignment == "right":
            row_layout.addStretch()
            row_layout.addWidget(bubble)
        else:
            row_layout.addWidget(bubble)
            row_layout.addStretch()

        self.chat_messages_layout.insertWidget(
            self.chat_messages_layout.count() - 1,
            message_row,
        )
        QTimer.singleShot(
            0,
            lambda: self.chat_history.verticalScrollBar().setValue(
                self.chat_history.verticalScrollBar().maximum()
            ),
        )
        return message_label

    def pick_paths(self) -> None:
        picker = PathPickerDialog(self)

        if picker.exec() == QDialog.DialogCode.Accepted:
            self.add_attachments(picker.selected_paths())

    def add_attachments(self, paths: list[str]) -> None:
        resolved_paths = [str(Path(path).expanduser().resolve()) for path in paths]

        if not resolved_paths:
            return

        current_message = self.message_input.toPlainText().rstrip()
        path_list = "\n".join(f"- {path}" for path in resolved_paths)
        separator = "\n\n" if current_message else ""
        self.message_input.setPlainText(
            f"{current_message}{separator}Attached paths:\n{path_list}"
        )
        self.message_input.moveCursor(QTextCursor.MoveOperation.End)
        self.message_input.setFocus()

    def send_message(self) -> None:
        message = self.message_input.toPlainText().strip()

        if not message:
            return

        self.add_message("user", message)
        self.message_input.clear()
        self.set_busy(True)

        title = message.replace("\n", " ")[:40]
        update_conversation(self.current_session_id, title)

        self.streaming_response = ""
        self.streaming_message_label = self.add_message("assistant", "")
        self.worker = AgentWorker(self.current_session_id, message)
        self.worker.response_delta.connect(self.receive_response_delta)
        self.worker.response_ready.connect(self.receive_response)
        self.worker.request_failed.connect(self.show_error)
        self.worker.finished.connect(self.worker_finished)
        self.worker.start()

    def receive_response_delta(self, delta: str) -> None:
        self.streaming_response += delta

        if self.streaming_message_label is not None:
            self.streaming_message_label.setText(self.streaming_response)

        self.chat_history.verticalScrollBar().setValue(
            self.chat_history.verticalScrollBar().maximum()
        )

    def receive_response(self, response: str) -> None:
        self.streaming_response = response

        if self.streaming_message_label is not None:
            self.streaming_message_label.setText(response)

        update_conversation(self.current_session_id)

    def show_error(self, error: str) -> None:
        QMessageBox.critical(self, "Agent Error | خطأ في الوكيل", error)

    def worker_finished(self) -> None:
        selected_id = self.current_session_id
        self.worker = None
        self.streaming_message_label = None
        self.streaming_response = ""
        self.set_busy(False)
        self.refresh_conversations(selected_id)
        self.message_input.setFocus()

    def set_busy(self, busy: bool) -> None:
        self.send_button.setDisabled(busy)
        self.message_input.setDisabled(busy)
        self.new_chat_button.setDisabled(busy)
        self.conversation_list.setDisabled(busy)
        self.attach_button.setDisabled(busy)


initialize_database()

app = QApplication([])
window = AgentWindow()
window.show()
app.exec()
