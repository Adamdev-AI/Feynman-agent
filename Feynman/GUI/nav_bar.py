from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt, Signal

class NavigationBar(QWidget):

    reasoning_clicked = Signal()
    knowledge_clicked = Signal()

    def __init__(self):
        super().__init__()

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setFixedHeight(65)

        # Objects
        self.hero_text = self.create_text("Feynman Agent", True)
        self.reasoning_stream = self.create_button('Reasoning Stream', self.when_reasoning_stream)
        self.knowledge_base = self.create_button('Knowledge Base', self.when_knowledge_base)

        # Designing
        self.main_layout = QHBoxLayout()

        self.main_layout.addStretch(5)
        self.add_widget(self.hero_text)
        self.main_layout.addStretch(80)
        self.add_widget(self.reasoning_stream)
        self.main_layout.addStretch(2)
        self.add_widget(self.knowledge_base)
        self.main_layout.addStretch(10)

        self.setStyleSheet('background-color: #081420; border-bottom: 1px solid grey')
        self.hero_text.setStyleSheet('color: #b1c5ec; font-size: 20px; border-bottom: none')
        self.reasoning_stream.setStyleSheet('color: #9fb6d8; border-bottom: none; font-size: 17px; border: none')
        self.knowledge_base.setStyleSheet('color: #a7afbc; border-bottom: none; font-size: 15px; border: none')

        self.setLayout(self.main_layout)

    def create_text(self, text: str, bold: bool):
        self.label = QLabel(text)
        self.font = QFont()
        self.font.setBold(bold)
        self.label.setFont(self.font)

        return self.label

    def add_widget(self, variable_name: str):
        self.main_layout.addWidget(variable_name)

    def create_button(self, text: str, when_clicked: str):
        self.button = QPushButton(text)
        self.font = QFont() 
        self.font.setBold(True)
        self.button.setFont(self.font)

        self.button.clicked.connect(when_clicked)
        
        return self.button
        
    def when_reasoning_stream(self):
        self.reasoning_stream.setStyleSheet('color: #9fb6d8; border-bottom: none; font-size: 17px; border: none')
        self.knowledge_base.setStyleSheet('color: #a7afbc; border-bottom: none; font-size: 15px; border: none')
        self.reasoning_clicked.emit()

    def when_knowledge_base(self):
        self.reasoning_stream.setStyleSheet('color: #a7afbc; border-bottom: none; font-size: 15px; border: none')
        self.knowledge_base.setStyleSheet('color: #9fb6d8; border-bottom: none; font-size: 17px; border: none')
        self.knowledge_clicked.emit()