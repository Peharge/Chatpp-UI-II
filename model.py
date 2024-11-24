import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QComboBox, QScrollArea, QFrame
from PyQt6.QtGui import QTextCursor, QFont, QIcon, QKeyEvent
from PyQt6.QtCore import QThread, pyqtSignal, Qt
import ollama
import ctypes
from PyQt6.QtGui import QFont, QColor
from PyQt6 import QtGui


def fetch_models():
    return {
        "Chat++ mini | mini | 9b  | 8k": "Chatpp-mini",
        "Chat++ 3.0  | mini | 8b  | 8k": "Chatpp3",
        "Chat++ 4.0  | mini | 8b  | 8k": "Chatpp4"
    }


class OllamaWorker(QThread):
    response_signal = pyqtSignal(str)

    def __init__(self, model, conversation):
        super().__init__()
        self.model = model
        self.conversation = conversation

    def run(self):
        try:
            response_stream = ollama.chat(model=self.model, messages=self.conversation, stream=True)
            response_content = ""
            for chunk in response_stream:
                content = chunk['message']['content']
                response_content += content
                self.response_signal.emit(content)
                time.sleep(0.05)
            self.conversation.append({'role': 'assistant', 'content': response_content})
        except Exception as e:
            self.response_signal.emit(f"Ein Fehler ist aufgetreten: {e}")


class CustomTextEdit(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self.on_enter()
                event.accept()
                return
        super().keyPressEvent(event)

    def on_enter(self):
        # Dies kann in der Unterklasse überschrieben werden
        pass


class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conversation = []
        self.models = fetch_models()
        self.populate_model_selector()

    def initUI(self):
        self.setWindowTitle('X++ ❤️')
        self.setGeometry(100, 100, 800, 800)

        self.setWindowIcon(QtGui.QIcon(
            'C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.4.ico'))

        myappid = u'mycompany.myproduct.subproduct.version'  # Arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

        background_color = QColor(30, 30, 30)
        self.setStyleSheet("background-color: rgb({},{},{})".format(
            background_color.red(), background_color.green(),
            background_color.blue()))

        self.setWindowOpacity(1)

        glass_frame = QFrame(self)
        glass_frame.setGeometry(0, 0, 1920, 1000)
        glass_frame.setStyleSheet("""
            background-color: #1e1e1e; 
            color: #ffffff;
        """)

        icon_path = "C:\\Users\\julia\\OneDrive - Gewerbeschule Lörrach\\Pictures\\software\\peharge-logo3.4.ico"
        self.setWindowIcon(QIcon(icon_path))

        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        layout = QVBoxLayout()

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #ffffff;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #ffffff;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
            }
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                background: none;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border: none;")
        self.output.setFont(QFont("Courier New", 12))
        self.output.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)

        self.scroll_content = QWidget()
        self.scroll_content_layout = QVBoxLayout()
        self.scroll_content_layout.addWidget(self.output)
        self.scroll_content.setLayout(self.scroll_content_layout)
        self.scroll_area.setWidget(self.scroll_content)

        layout.addWidget(self.scroll_area)

        self.model_selector = QComboBox()
        self.model_selector.setFont(QFont("Courier", 12))
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 5px;
                padding-right: 35px;
            }
            QComboBox:focus {
                background-color: #2e2e2e;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 35px;
                border-left: 1px solid #555555;
                background-color: #2b2b2b;
            }
            QComboBox::down-arrow {
                image: url("C:/Users/julia/PycharmProjects/X++/peharge-logo3.4.png");
                width: 20px;
                height: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e1e1e;
                color: #ffffff;
                border-radius: 8px;
                selection-background-color: #2e2e2e;
                selection-color: #ffffff;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        layout.addWidget(self.model_selector)

        self.input = CustomTextEdit()
        self.input.setFont(QFont("Courier", 12))
        self.input.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                padding: 5px;
                border: 2px solid #333;
                border-radius: 5px;
                color: #e0e0e0;
                selection-background-color: #0078d7;
                selection-color: #ffffff;
            }
            QTextEdit:focus {
                background-color: #2e2e2e;
            }
            QScrollArea {
                border: none;
                background-color: #ffffff;
            }
            QScrollBar:vertical {
                background-color: #ffffff;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background-color: #ffffff;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background: none;
            }
            QScrollBar::up-arrow:vertical,
            QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: none;
            }
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background: none;
            }
            QScrollBar::left-arrow:horizontal,
            QScrollBar::right-arrow:horizontal {
                background: none;
            }
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        self.input.setPlaceholderText("Gib hier deine Nachricht ein...")
        self.input.setToolTip("Gib hier deine Nachricht ein und drücke Enter.")
        self.input.textChanged.connect(self.adjust_height)
        self.input.setFixedHeight(40)

        # Verbinde die benutzerdefinierte on_enter-Methode der CustomTextEdit-Klasse
        self.input.on_enter = self.on_enter

        layout.addWidget(self.input)
        self.setLayout(layout)

        self.append_banner()
        self.append_welcome_message()

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
            if event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self.on_enter()
                event.accept()
                return
        super().keyPressEvent(event)

    def adjust_height(self):
        document = self.input.document()
        desired_height = int(
            document.size().height() + self.input.contentsMargins().top() + self.input.contentsMargins().bottom())
        self.input.setFixedHeight(min(200, max(40, desired_height)))  # Maximale Höhe auf 200px begrenzen

    def on_enter(self):
        user_input = self.input.toPlainText().strip()
        if not user_input:
            return

        if user_input.lower() == 'exit':
            self.close()
            return

        self.append_user_input(user_input)
        self.conversation.append({'role': 'user', 'content': user_input})
        self.input.clear()

        selected_model_key = self.model_selector.currentText()
        selected_model = self.models[selected_model_key]
        self.worker = OllamaWorker(model=selected_model, conversation=self.conversation)
        self.worker.response_signal.connect(self.update_output)
        self.worker.start()

    def append_user_input(self, user_input):
        self.output.append(f"<p style='color: white;'><br>User: {user_input}<br><br>X++> </p>")

    def update_output(self, content):
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(content)
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.ensureCursorVisible()

    def update_model_info(self, model_name):
        # HTML-Tag für roten Text
        model_info = f"<p style='color: red;'><br>Ausgewähltes Modell: {model_name}</p>"
        self.output.append(model_info)

    def populate_model_selector(self):
        for model_name in self.models.keys():
            self.model_selector.addItem(model_name)
        self.model_selector.currentTextChanged.connect(self.update_model_info)
        self.update_model_info(self.model_selector.currentText())

    def append_banner(self):

        banner_text = (
            "\n"
            "  _      _                                     \n"
            "/_/\    /\ \           _             _         \n"
            "\ \ \   \ \_\         /\ \          /\ \       \n"
            " \ \ \__/ / /      ___\ \_\      ___\ \_\      \n"
            "  \ \__ \/_/      /___/\/_/_    /___/\/_/_     \n"
            "   \/_/\__/\      \__ \/___/\   \__ \/___/\    \n"
            "    _/\/__\ \       /\/____\/     /\/____\/    \n"
            "   / _/_/\ \ \      \ \_\         \ \_\        \n"
            "  / / /   \ \ \      \/_/          \/_/        \n"
            " / / /    /_/ /                                \n"
            " \/_/     \_\/                                 \n"
        )
        self.output.append(banner_text)

    def append_welcome_message(self):
        welcome_text = (
            "\nMicrosoft Windows [Version 10.0.22631.3810]\n"
            "(c) Microsoft Corporation. Alle Rechte vorbehalten.\n"
            "(c) And welcome from Peharge\n"
            "\nroot@julian:/Chat++~$ run x++"
        )
        self.output.append(welcome_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec())
