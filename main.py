import sys
import time
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QComboBox
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtCore import QThread, pyqtSignal
import ollama

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
                time.sleep(0.05)  # Kontrolliert die Geschwindigkeit des Datenstroms
            self.conversation.append({'role': 'assistant', 'content': response_content})
        except Exception as e:
            self.response_signal.emit(f"Ein Fehler ist aufgetreten: {e}")

class Terminal(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conversation = []

    def initUI(self):
        self.setWindowTitle("Chat++ Terminal")
        self.setGeometry(100, 100, 1000, 700)  # Größeres Fenster
        layout = QVBoxLayout()

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("background-color: black; color: white;")
        self.output.setFont(QFont("Courier", 12))  # Größere Schriftgröße für bessere Lesbarkeit
        layout.addWidget(self.output)

        self.model_selector = QComboBox()
        self.model_selector.addItems(["chatpp2", "chatpp3", "chatpp4"])
        self.model_selector.setStyleSheet("background-color: #1e1e1e; color: #ffffff; border-radius: 5px; padding: 5px;")  # Bessere Stilgestaltung
        layout.addWidget(self.model_selector)

        self.input = QLineEdit()
        self.input.setStyleSheet(
            "background-color: #2d2d2d; color: #ffffff; border-radius: 5px; padding: 10px;"
            "border: 1px solid #3c3c3c; font-size: 14px;"
        )  # Größere und schönere Eingabebox
        self.input.returnPressed.connect(self.on_enter)
        self.input.setFont(QFont("Courier", 12))  # Größere Schriftgröße für bessere Lesbarkeit
        self.input.setPlaceholderText("Gib hier deine Nachricht ein...")  # Platzhaltertext für das Eingabefeld

        layout.addWidget(self.input)  # Direktes Hinzufügen des Eingabefeldes zum Layout

        self.setLayout(layout)

        self.append_banner()
        self.append_welcome_message()

    def append_banner(self):
        banner_text = (
            "##############################################\n"
            "#                                            #\n"
            "#           Willkommen bei Chat++            #\n"
            "#                                            #\n"
            "##############################################\n"
        )
        self.output.append(banner_text)

    def append_welcome_message(self):
        welcome_text = (
            "\nMicrosoft Windows [Version 10.0.22631.3810]\n"
            "(c) Microsoft Corporation. Alle Rechte vorbehalten.\n"
        )
        self.output.append(welcome_text)

    def on_enter(self):
        user_input = self.input.text().strip()  # Entfernt überflüssige Leerzeichen
        if not user_input:
            return  # Verhindert leere Eingaben

        if user_input.lower() == 'exit':
            self.close()
            return

        self.append_user_input(user_input)
        self.conversation.append({'role': 'user', 'content': user_input})
        self.input.clear()

        selected_model = self.model_selector.currentText().lower()
        self.worker = OllamaWorker(model=selected_model, conversation=self.conversation)
        self.worker.response_signal.connect(self.update_output)
        self.worker.start()

    def append_user_input(self, user_input):
        self.output.append(f"root@julian:~$ {user_input}\n\n")

    def update_output(self, content):
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(content)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    terminal = Terminal()
    terminal.show()
    sys.exit(app.exec())
