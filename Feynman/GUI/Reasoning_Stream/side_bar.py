from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame, QSizePolicy, QScrollArea, QPushButton
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from ai.main_ai import new_chat

class FeedBack(QFrame):
    def __init__(self, role: str, icon: str, text: str, note: str):
        super().__init__()

        self.main_layout = QVBoxLayout(self)
        self.header = QHBoxLayout()
        self.FeedBack_message_widget = QFrame()
        self.FeedBack_message = QVBoxLayout(self.FeedBack_message_widget)

        if role == 'error':

            self.FeedBack_message_widget.setStyleSheet("""
                background-color: #2d1a1d;
                border: 1px solid #f87171;
                border-left: 3px solid #f87171;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                border-bottom-left-radius: 6px;
            """)

            self.icon = QLabel()
            self.icon.setStyleSheet('border: none;')
            self.icon.setPixmap(QIcon(icon).pixmap(16,16))

            self.text = QLabel(text, wordWrap=True)
            self.text.setStyleSheet('color: #EEF2F6; font-size: 13px; font-weight: bold; border: none')

            self.note = QLabel(note)
            self.note.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.note.setStyleSheet('background-color: #3d2327; color: #f87171; border-radius: 4px; padding: 4px 8px; font-size: 10px; font-weight: bold; border: 1px solid transparent')

            self.main_layout.addLayout(self.header)

            self.FeedBack_message.addWidget(self.icon)
            self.FeedBack_message.addWidget(self.text)
            self.FeedBack_message.addWidget(self.note)
            self.main_layout.addWidget(self.FeedBack_message_widget)

        elif role == 'weak':

            self.FeedBack_message_widget.setStyleSheet("""
                    background-color: #2e2311;
                    border: 1px solid #fbbf24;
                    border-left: 3px solid #fbbf24;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    border-bottom-left-radius: 6px;
            """)

            self.icon = QLabel()
            self.icon.setStyleSheet('border: none;')
            self.icon.setPixmap(QIcon(icon).pixmap(16,16))

            self.text = QLabel(text, wordWrap=True)
            self.text.setStyleSheet('color: #EEF2F6; font-size: 13px; font-weight: bold; border: none')

            self.note = QLabel(note)
            self.note.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.note.setStyleSheet('background-color: #3d2f16; color: #fbbf24; border-radius: 4px; padding: 4px 8px; font-size: 10px; font-weight: bold; border: 1px solid #423726')

            self.main_layout.addLayout(self.header)

            self.FeedBack_message.addWidget(self.icon)
            self.FeedBack_message.addWidget(self.text)
            self.FeedBack_message.addWidget(self.note)
            self.main_layout.addWidget(self.FeedBack_message_widget)

        elif role == 'verified':

            self.FeedBack_message_widget.setStyleSheet("""
                    background-color: #064e3b;
                    border: 1px solid #34d399;
                    border-left: 3px solid #34d399;
                    border-top-left-radius: 6px;
                    border-top-right-radius: 6px;
                    border-bottom-right-radius: 6px;
                    border-bottom-left-radius: 6px;
            """)

            self.icon = QLabel()
            self.icon.setStyleSheet('border: none;')
            self.icon.setPixmap(QIcon(icon).pixmap(16,16))

            self.text = QLabel(text, wordWrap=True)
            self.text.setStyleSheet('color: #EEF2F6; font-size: 13px; font-weight: bold; border: none')

            self.note = QLabel(note)
            self.note.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.note.setStyleSheet('background-color: #065f46; color: #34d399; border-radius: 4px; padding: 4px 8px; font-size: 10px; font-weight: bold; border: 1px solid #184241')

            self.main_layout.addLayout(self.header)

            self.FeedBack_message.addWidget(self.icon)
            self.FeedBack_message.addWidget(self.text)
            self.FeedBack_message.addWidget(self.note)
            self.main_layout.addWidget(self.FeedBack_message_widget)

class SideBar(QWidget):
    def __init__(self, chat):
        super().__init__()

        self.chat = chat

        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #161b21')

        # Header 
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.header_widget = QWidget()
        self.header_layout = QVBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(20, 20, 20, 20)

        self.row_1 = QHBoxLayout()
        self.header_text = QLabel('Critical Feedback')
        self.header_text.setStyleSheet('font-size: 20px; color: #d6dce8')
        font = self.header_text.font()
        font.setBold(True)
        self.header_text.setFont(font)
        self.row_1.setContentsMargins(0, 0, 0, 10)
        self.row_1.addWidget(self.header_text)

        self.row_2 = QHBoxLayout()

        self.header_layout.addLayout(self.row_1)
        self.header_layout.addLayout(self.row_2)

        self.seperator = QFrame()
        self.seperator.setFixedHeight(2)
        self.seperator.setStyleSheet("background-color: #2a3040; border: none;")

        self.seperator_2 = QFrame()
        self.seperator_2.setFixedHeight(2)
        self.seperator_2.setStyleSheet("background-color: #2a3040; border: none;")

        self.ai_feedbacks_widget = QWidget()
        self.scroll_area = QScrollArea(widgetResizable=True)
        self.scroll_area.setWidget(self.ai_feedbacks_widget)
        self.scroll_area.setStyleSheet('border: none;')
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.ai_feedbacks = QVBoxLayout(self.ai_feedbacks_widget)
        self.ai_feedbacks.setContentsMargins(0, 0, 0, 0)

        self.errors_section = QVBoxLayout()
        self.weak_section = QVBoxLayout()
        self.verified_section = QVBoxLayout()

        self.errors_header = QLabel('ERRORS')
        self.errors_header.setStyleSheet('font-weight: bold; font-size: 10px; color: #f87171; margin-left: 7px; margin-top: 3px;')
        self.weak_header = QLabel('WEAK')
        self.weak_header.setStyleSheet('font-weight: bold; font-size: 10px; color: #fbbf24; margin-left: 7px; margin-top: 3px;')
        self.verified_header = QLabel('VERIFIED')
        self.verified_header.setStyleSheet('font-weight: bold; font-size: 10px; color: #34d399; margin-left: 7px; margin-top: 3px;')

        self.build_state_labels()

        for header, section in [(self.errors_header, self.errors_section),
                                (self.weak_header, self.weak_section),
                                (self.verified_header, self.verified_section)]:

                                header.hide()
                                self.ai_feedbacks.addWidget(header)
                                self.ai_feedbacks.addLayout(section)

        self.ai_feedbacks.addStretch()

        self.re_chat_widget = QWidget()
        self.re_chat_widget.setStyleSheet('background-color: #091421')
        self.re_chat_layout = QHBoxLayout(self.re_chat_widget)
        self.re_chat_layout.setContentsMargins(20, 20, 20, 20)

        self.re_chat_button = QPushButton('re-chat')
        self.re_chat_button.clicked.connect(self.when_re_chat)
        self.re_chat_button.setIcon(QIcon('GUI\\Reasoning_Stream\\assets\\re_sync.svg'))
        self.re_chat_button.setStyleSheet("""
            QPushButton {
                background-color: #34d399;
                color: #091421;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #10b981;
            }
            QPushButton:pressed {
                background-color: #059669;
            }
        """)

        self.re_chat_layout.addWidget(self.re_chat_button)

        self.main_layout.addWidget(self.header_widget)
        self.main_layout.addWidget(self.seperator)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.seperator_2)
        self.main_layout.addWidget(self.re_chat_widget)

        self.setLayout(self.main_layout)

    def state_label(self, text, background_color, text_color):
        label = QLabel(text)
        label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        label.setStyleSheet(f'font-size: 9px; background-color: {background_color}; color: {text_color}; padding: 5px; border-radius: 5px; border: 1.5px solid {text_color};')
        return label

    def feedback_message(self, role, icon, text, note):
        try:
            self.feedback = FeedBack(role, icon, text, note)

            section, header = {
                'error': (self.errors_section, self.errors_header),
                'weak': (self.weak_section, self.weak_header),
                'verified': (self.verified_section, self.verified_header),
            }.get(role)

            section.insertWidget(0, self.feedback)
            self.refresh_counts()
            header.show()
            return "Done."
        
        except Exception as e:
            return f"There was an problem: {e}"
        
    def ai_message_feedback(self, role, text, note):
        if role == 'error':
            self.feedback_message('error', 'GUI\\Reasoning_Stream\\assets\\wrong_icon.svg', text, note)
            return "Done."
        elif role == 'weak':
            self.feedback_message('weak', 'GUI\\Reasoning_Stream\\assets\\weak_icon.svg', text, note)
            return "Done."
        elif role == 'verified':
            self.feedback_message('verified', 'GUI\\Reasoning_Stream\\assets\\verified_icon.svg', text, note)
            return "Done."
        else:
            return f'The role should be either error or weak or verified note: {role}'

    def refresh_counts(self):
        self.errors.setText(f'{self.get_num(self.errors_section)} ERRORS')
        self.weak_points.setText(f'{self.get_num(self.weak_section)} WEAK')
        self.verified.setText(f'{self.get_num(self.verified_section)} VERIFIED')

    def get_num(self, layout):
        return layout.count()

    def build_state_labels(self):
        self.errors_num = str(self.get_num(self.errors_section))
        self.weak_points_num = str(self.get_num(self.weak_section))
        self.verified_num = str(self.get_num(self.verified_section))

        self.errors = self.state_label(f'{self.errors_num} ERRORS', '#311319', '#9e7374')
        self.weak_points = self.state_label(f'{self.weak_points_num} WEAK', '#3b311c', '#ac8e58')
        self.verified = self.state_label(f'{self.verified_num} VERIFIED', '#0f3732', '#479a7e')

        self.row_2.addWidget(self.errors)
        self.row_2.addWidget(self.weak_points)
        self.row_2.addWidget(self.verified)
        self.row_2.addStretch()

    def when_re_chat(self):
        self._clear_layout(self.chat.all_messages_layout)
        self.chat.all_messages_layout.addStretch()

        for section, header in [(self.errors_section, self.errors_header),
                                (self.weak_section, self.weak_header),
                                (self.verified_section, self.verified_header)]:
            self._clear_layout(section)
            header.hide()

        self.refresh_counts()
        new_chat()

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())