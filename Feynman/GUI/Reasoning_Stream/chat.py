from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QSizePolicy
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon

class MessageBubble(QFrame):
    def __init__(self, text: str, role: str = 'ai', header: str | None = None, footer: str | None = None,
                 icon_path: str | None = None):
        super().__init__()

        if role == 'user':
            self.setStyleSheet("""
                QFrame {
                    background-color: #4c7ef3;
                    border-top-left-radius: 14px;
                    border-top-right-radius: 0px;
                    border-bottom-left-radius: 14px;
                    border-bottom-right-radius: 14px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #141b2d;
                    border: 1px solid #56637e;
                    border-left: 3px solid #afc5f6;
                    border-top-left-radius: 0px;
                    border-top-right-radius: 14px;
                    border-bottom-left-radius: 0px;
                    border-bottom-right-radius: 14px;
                }
            """)

        self.setMaximumWidth(480)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        if header:
            header_row = QHBoxLayout()
            header_row.setSpacing(6)
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(16,16))
            icon_label.setStyleSheet('border: none')
            header_label = QLabel(header.upper())
            header_label.setStyleSheet(
                "color: #7aa5f7; font-size: 11px; font-weight: 600; letter-spacing: 1px; border: none;"
            )
            header_row.addWidget(icon_label)
            header_row.addWidget(header_label)
            header_row.addStretch()
            layout.addLayout(header_row)

        self.text_label = QLabel(text, wordWrap=True)
        color = '#ffffff' if role == 'user' else '#e2e6ee'
        self.text_label.setStyleSheet(
            f'color: {color}; font-size: 14px; background: transparent; border: none;'
        )
        layout.addWidget(self.text_label)

        if footer:
            footer_row = QHBoxLayout()
            footer_row.addStretch()
            footer_label = QLabel(footer)
            footer_label.setStyleSheet(
                f'color: {'#cdd9fb' if role == 'user' else '#8a97ab'};'
                f'font-size: 10px; letter-spacing: 0.5px; background: transparent;'
            )
            footer_row.addWidget(footer_label)
            layout.addLayout(footer_row)

class Chat(QWidget):
    def __init__(self):
        super().__init__()

        self.all_messages_widget = QWidget()
        self.all_messages_layout = QVBoxLayout(self.all_messages_widget)
        self.all_messages_layout.setSpacing(16)
        self.all_messages_layout.addStretch()

        self.scroll_area = QScrollArea(widgetResizable=True)
        self.scroll_area.setWidget(self.all_messages_widget)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.vscroll_area = self.scroll_area.verticalScrollBar()
        self.vscroll_area.rangeChanged.connect(self.scroll_to_bottom)
        self.scroll_area.setStyleSheet("""

            QScrollArea {
                border: none;
                background-color: transparent;
            }

            QScrollArea > QWidget > QWidget {
                background-color: transparent; /* Inner viewports */
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }

            QScrollBar::handle:vertical {
                background: #2b384e;
                min-height: 40px;
                border-radius: 3px;
            }

            QScrollBar::handle:vertical:hover {
                background: #415575;
            }

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                border: none;
            }
        """)

        self.chat_layout = QVBoxLayout(self)
        self.chat_layout.setContentsMargins(0, 0, 0, 0) 
        self.chat_layout.addWidget(self.scroll_area)

    def show_user_message(self, text: str):
        bubble = MessageBubble(text=text, role='user')
        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(bubble)
        self.all_messages_layout.insertLayout(self.all_messages_layout.count() - 1, row)

    def show_ai_message(self, text: str, role: str, header: str, icon_path: str):
        bubble = MessageBubble(text=text, role=role, header=header, icon_path=icon_path)
        row = QHBoxLayout()
        row.addWidget(bubble)
        row.addStretch()        
        self.all_messages_layout.insertLayout(self.all_messages_layout.count() - 1, row)

    @Slot(int, int)
    def scroll_to_bottom(self, minimum: int, maximum: int):
        self.vscroll_area.setValue(maximum)