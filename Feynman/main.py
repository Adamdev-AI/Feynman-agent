from GUI.nav_bar import NavigationBar
from GUI.Reasoning_Stream.input_bar import InputBar
from PySide6.QtWidgets import QWidget, QVBoxLayout, QApplication, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from GUI.Reasoning_Stream.chat import Chat 
from GUI.Reasoning_Stream.side_bar import SideBar
from GUI.Knowledge_Base.knowledge import KnowledgeBase
from ai.main_ai import register_sidebar
from ai.signals import update_from_last_session
import sys

class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Feynman Agent')
        self.setWindowIcon(QIcon('GUI\\Reasoning_Stream\\assets\\Feynman Icon.jpg'))

        # Objects
        # Reasoning Stream
        self.nav_bar = NavigationBar()
        self.chat = Chat()
        
        self.input_bar = InputBar(self.chat)
        self.side_bar = SideBar(self.chat)
        register_sidebar(self.side_bar)

        # Knowledge Base
        self.knowledge = KnowledgeBase()

        # Designing
        self.main_layout = QVBoxLayout()
        self.reasoning_stream_layout = QHBoxLayout()
        self.knowledge_base_layout = QHBoxLayout()
        self.chat_layout = QVBoxLayout()

        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.reasoning_stream_layout.setContentsMargins(0, 0, 0, 0)
        self.reasoning_stream_layout.setSpacing(0)
        self.chat_layout.setContentsMargins(0, 0, 0, 0)

        self.knowledge_base_layout.addWidget(self.knowledge, 6)

        self.chat_layout.addWidget(self.chat)
        self.chat_layout.addWidget(self.input_bar)
        self.reasoning_stream_layout.addLayout(self.chat_layout, stretch=6)
        self.reasoning_stream_layout.addWidget(self.side_bar, stretch=2)

        self.reasoning_stream_widget = QWidget()
        self.reasoning_stream_widget.setLayout(self.reasoning_stream_layout)
        self.knowledge_base_widget = QWidget()
        self.knowledge_base_widget.setLayout(self.knowledge_base_layout)
        self.knowledge_base_layout.setContentsMargins(0, 0, 0, 0)
        self.knowledge_base_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.stack.addWidget(self.reasoning_stream_widget)
        self.stack.addWidget(self.knowledge_base_widget)

        self.nav_bar.reasoning_clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.nav_bar.knowledge_clicked.connect(lambda: self.stack.setCurrentIndex(1))

        self.main_layout.addWidget(self.nav_bar, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.addWidget(self.stack)

        self.setStyleSheet('background-color: #0b0e15')
        self.setLayout(self.main_layout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.exec()