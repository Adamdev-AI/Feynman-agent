from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit
from PySide6.QtCore import Qt, QSize, QThread, QObject, Signal
from PySide6.QtGui import QIcon, QKeySequence
from ai.main_ai import conversation

class AiWorker(QObject): 
    finished = Signal(str)

    def __init__(self, user_input: str):
        super().__init__()
        self.user_input = user_input

    def run(self):
        reply = conversation(self.user_input)
        self.finished.emit(reply)

class InputBar(QWidget):
    def __init__(self, chat):
        super().__init__()

        self._thread = None
        self._worker= None

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(120)

        self.chat = chat

        # Objects

        self.input_bar_widget = QWidget()
        self.input_bar = QLineEdit(placeholderText='Explain a concept in your own words to get started...')
        self.send_btn = QPushButton()   
        self.send_btn.clicked.connect(self.when_send) 

        # Designing
        self.main_layout = QHBoxLayout()
        self.input_bar_layout = QHBoxLayout(self.input_bar_widget)
        self.main_layout.addWidget(self.input_bar_widget)
        self.input_bar_layout.addWidget(self.input_bar)
        self.input_bar_layout.addWidget(self.send_btn)

        self.setStyleSheet('background-color: #121c2b; border-top: 3px solid #222834')
        self.input_bar.setStyleSheet('border: none; color: white')
        self.input_bar.setFocus()
        self.send_btn.setFixedSize(QSize(40, 40))
        self.send_btn.setIconSize(QSize(20, 20))
        self.send_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: #AEC5FE;
                border-radius: 8px;
            }

            QPushButton:hover {
                background-color: #8FB1FC;
            }

            QPushButton:pressed {
                background-color: #6D96F8;
            }

            QPushButton:disabled {
                background-color: #5A6475;
            }
        """)
        self.send_btn.setShortcut(QKeySequence("Return"))

        self.input_bar_widget.setStyleSheet('background-color: #161b21; border: 2px solid #212631; border-radius: 20px; font-size: 20px')
        self.setContentsMargins(30, 10, 30, 10)
        self.input_bar_widget.setContentsMargins(8, 0, 0, 0)
        self.input_bar_widget.setFixedHeight(80)

        self.send_btn.setIcon(QIcon("GUI\\Reasoning_Stream\\assets\\send_button.png"))

        self.setLayout(self.main_layout)

    def when_send(self):
        input_bar_text = self.input_bar.text()
        if input_bar_text:
            self.input_bar.clear()
            self.chat.show_user_message(text=input_bar_text)
            self.send_btn.setEnabled(False)

            self._thread = QThread()
            self._worker = AiWorker(input_bar_text)
            self._worker.moveToThread(self._thread)

            self._thread.started.connect(self._worker.run)
            self._worker.finished.connect(self._on_ai_response)
            self._worker.finished.connect(self._thread.quit)

            self._thread.start()

    def _on_ai_response(self, response: str):
        self.chat.show_ai_message(response, 'ai', 'reasoning engine', 'GUI\\Reasoning_Stream\\assets\\reasoning.png')
        self.send_btn.setEnabled(True)
