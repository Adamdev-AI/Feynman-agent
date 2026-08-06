from PySide6.QtWidgets import QWidget, QVBoxLayout, QLayout, QSizePolicy, QHBoxLayout, QLabel, QFrame, QScrollArea, QPushButton
from GUI.Knowledge_Base.mastery_level import header, get_every_card_mastery_percentage
from GUI.Knowledge_Base.generate_ai_deep_analysis import run_agent_in_background
from PySide6.QtCore import Qt, QRect, QSize, QMargins, QPoint, QRectF, Slot
from PySide6.QtGui import QColor, QPainter, QPen, QFont, QIcon
from ai.main_ai import ai_adding_card, messages
from ai.signals import signals, update_nodes, cards_info, new_btn_name, enable_button_clickable
import sqlite3
import json

class FlowLayout(QLayout): # From Qt Example: https://doc.qt.io/qtforpython-6/examples/example_widgets_layouts_flowlayout.html
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        return y + line_height - rect.y()

class CircualProgress(QWidget):
    def __init__(self, value: int = 0, size: int = 50, parent=None):
        super().__init__(parent)
        self._value = value
        self.setMaximumSize(size, size)

    def get_value(self) -> int:
        return self._value

    def set_value(self, v: int):
        self._value = max(0, min(100, v))
        self.update() # Calls PaintEvent and schedule the painting when ready 

    def _color_for_value(self) -> QColor:
        if self._value >= 80:
            return QColor("#2ecc71")
        elif self._value >= 50:
            return QColor("#f1c40f")
        elif self._value < 50:
            return QColor("#e74c3c")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing) # Smooth curve

        side = min(self.width(), self.height())
        pen_width = side * 0.10

        rect = QRectF(pen_width / 2, pen_width / 2, side - pen_width, side - pen_width)

        bg_pen = QPen(QColor("#2b2f3a"), pen_width)
        bg_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(bg_pen)
        painter.drawArc(rect, 0, 360 * 16)

        pen = QPen(self._color_for_value(), pen_width)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        start_angle = 90 * 16
        span_angle = -int(360 * 16 * (self._value / 100))
        painter.drawArc(rect, start_angle, span_angle)

        painter.setPen(QColor("#ffffff"))
        painter.setFont(QFont("Arial", int(side * 0.18), QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, f"{self._value}%")

    def sizeHint(self):
        return QSize(100, 100)


# SQL

def connec(db_name: str):
    return sqlite3.connect(db_name)

def create_table(connection):
    connection.execute("""
        CREATE TABLE IF NOT EXISTS cards_info(
            id INTEGER PRIMARY KEY,
            card_name TEXT NOT NULL,
            verified_or_wrong TEXT NOT NULL,
            header_category_name TEXT NOT NULL,
            progress_number INTEGER NOT NULL,
            key_concepts TEXT NOT NULL,
            last_probes TEXT NOT NULL,
            gap TEXT NOT NULL,
            chat_history TEXT NOT NULL
    )""")

    connection.commit()

def delete_table(connection, table_name: str):
    connection.execute(f'DROP TABLE IF EXISTS {table_name}')

    connection.commit()

def run_sql(connection, query: str):
    value = connection.execute(query).fetchone()

    connection.commit()

    return value


def get_value(connection, value_name):
    value = connection.execute(f"""
        SELECT {value_name} FROM cards_info 
    """).fetchone()

    if value is None:
        return None

    return value[0]

def update_value(connection, value_name, new_value):
    connection.execute(f"""
        UPDATE cards_info SET {value_name} = ?
    """,
    (new_value,))

    connection.commit()

def get_all_values(connection):
    all_rows = connection.execute("SELECT * FROM cards_info").fetchall()
    return all_rows

def main_sql():
    connection = connec('GUI\\Knowledge_Base\\db\\cards_info.db')
    create_table(connection)

main_sql()


def convert_lists(list: list):
    converted_list = json.dumps(list)

    return converted_list

def convert_str_to_list(string: str):
    retrived_list = json.loads(string)
    
    return retrived_list

class Card(QFrame):
    def __init__(self, card_name, verified_or_wrong = None, header_category_name = None, progress_number: int = 0, key_concepts: list | None = None, probes: list | None = None, identified_gap_text: str = ''): 
        super().__init__()

        self.key_concepts_data = key_concepts or []
        self.probes_data = probes or []
        self.probes_data_len = len(self.probes_data)

        # card settings
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setFixedWidth(340)
        self.setStyleSheet("""
            background-color: rgba(22, 27, 34, 0.8);
            border-radius: 10px;
        """)
        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        
        # Card header
        self.card_header = QWidget()
        self.card_header.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.card_header_layout = QHBoxLayout(self.card_header)
        self.card_header_layout.setContentsMargins(16, 16, 16, 16)

        # Card name
        self.card_name_layout = QVBoxLayout()
        self.card_name(card_name, """color: #d9e3f6;
            font-family: "Inter", sans-serif;
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.2px;
            background: transparent;
            border: none;
            padding: 0px;
        """)
        self.card_header_layout.addLayout(self.card_name_layout)

        # header labels
        self.header_labels_layout = QHBoxLayout()

        self.card_header_info_label(verified_or_wrong, None)
        self.card_header_info_label(None, header_category_name)
        self.header_labels_layout.addStretch()

        self.card_name_layout.addLayout(self.header_labels_layout)
        self.card_name_layout.addStretch()

        # Progress in the header
        self.progress_layout = QVBoxLayout()
        self.progress_card(progress_number)

        self.card_header_layout.addLayout(self.progress_layout)

        # Body
        self.body = QWidget()
        self.body.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self.body_layout = QVBoxLayout(self.body)
        self.body_layout.setContentsMargins(16, 16, 16, 16)

        # Key concepts
        self.key_concepts = FlowLayout()
        self.key_concepts_hero = QLabel('key concepts'.upper())
        self.key_concepts_hero.setStyleSheet("""
            color: #c2c6d6;
            font-family: "Geist", sans-serif;
            margin-top: 5px;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
        """)
        self.body_layout.addWidget(self.key_concepts_hero)
        for concept in self.key_concepts_data:
            self.create_key_concept(concept)
        self.body_layout.addLayout(self.key_concepts)

        # Last probes
        self.last_probes = QHBoxLayout()
        self.last_probes_hero = QLabel('recent probes'.upper())
        self.last_probes_hero.setStyleSheet("""
            color: #c2c6d6;
            font-family: "Geist", sans-serif;
            font-size: 10px;
            font-weight: 600;
            letter-spacing: 0.5px;
            background: transparent;
            border: none;
            margin-top: 12px;
            margin-bottom: 4px;
        """)
        self.body_layout.addWidget(self.last_probes_hero)

        if self.probes_data_len < 3:
            self.left = 3 - self.probes_data_len

            for probe in self.probes_data:
                self.create_probes(probe)

            for _ in range(self.left):
                self.create_probes('none')
        else:
            for probe in self.probes_data:
                self.create_probes(probe)

        self.body_layout.addLayout(self.last_probes)

        # Identified Gaps
        self.indentified_gap_widget = QFrame()
        self.identified_gap = QVBoxLayout(self.indentified_gap_widget)
        self.identified_gap_header = QHBoxLayout()

        self.identified_gap_icon = QLabel()
        self.identified_gap_icon.setStyleSheet("""
            color: #ffb4ab;
            background: transparent;
            border: none;
        """)
        self.identified_gap_icon.setPixmap(QIcon("GUI\\Knowledge_Base\\assets\\identified_gap.svg").pixmap(18, 18))
        self.identified_gap_header.addWidget(self.identified_gap_icon)

        self.identified_gap_label = QLabel('identified gap'.upper())
        self.identified_gap_label.setStyleSheet("""
            color: #ffb4ab;
            font-size: 12px;
            font-weight: 600;
            background: transparent;
            border: none;
        """)
        self.identified_gap_header.addWidget(self.identified_gap_label)
        self.identified_gap_header.addStretch()

        self.indentified_gap_widget.setStyleSheet("""
            background-color: rgba(147, 0, 10, 25);
            border-left: 2px solid #ffb4ab;
            border-top-left-radius: 0px;
            border-bottom-left-radius: 0px;
            border-top-right-radius: 4px;
            border-bottom-right-radius: 4px;
        """)
        
        self.identified_gap.addLayout(self.identified_gap_header)

        self.set_idenified_gap(text=identified_gap_text)
        self.body_layout.addSpacing(15)
        self.body_layout.addWidget(self.indentified_gap_widget)

        self.main_layout.addWidget(self.card_header)
        self.Hseparate(self.main_layout)
        self.main_layout.addWidget(self.body)

        self.setMinimumHeight(self.main_layout.heightForWidth(340))

    def card_name(self, card_name: str, stylesheet: str):
        self.card_name_label = QLabel(card_name, wordWrap=True)
        self.card_name_label.setStyleSheet(stylesheet)
        self.card_name_layout.addWidget(self.card_name_label)

    def card_header_info_label(self, label_name: str = None, category_name: str = None):
        if label_name:
            if label_name == 'verified':
                self.label_name = QLabel(label_name.upper())
                self.label_name.setStyleSheet("""
                    background-color: rgba(0, 165, 114, 0.2);
                    color: #4edea3;
                    border: 1px solid rgba(78, 222, 163, 0.3);
                    border-radius: 3px;
                    font-family: "Geist", "Inter", sans-serif;
                    font-size: 8px;
                    font-weight: 600;
                    padding: 3px 7px;
                """)
                self.label_name.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.header_labels_layout.addWidget(self.label_name)

            elif label_name == 'failed':
                self.label_name = QLabel(label_name.upper())
                self.label_name.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.label_name.setStyleSheet("""
                    background-color: rgba(147, 0, 10, 0.2);
                    color: #ffb4ab;
                    border: 1px solid rgba(255, 180, 171, 0.3);
                    border-radius: 3px;
                    font-family: "Geist", "Inter", sans-serif;
                    font-size: 8px;
                    font-weight: 600;
                    padding: 3px 7px;
                """)
                self.header_labels_layout.addWidget(self.label_name)

        if category_name:
            self.card_category = QLabel(category_name.upper())
            self.card_category.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            self.card_category.setStyleSheet("""
                    background-color: #2b3544;
                    color: #c2c6d6;
                    border: 1px solid #424754;
                    border-radius: 3px;
                    font-family: "Geist", "Inter", sans-serif;
                    font-size: 8px;
                    font-weight: 600;
                    padding: 3px 7px;
                """)
            self.header_labels_layout.addWidget(self.card_category)

    def progress_card(self, value: int):
        circular_progress = CircualProgress(value, 49)
        self.progress_layout.addWidget(circular_progress, alignment=Qt.AlignmentFlag.AlignRight)

    def Hseparate(self, layout):
        line = QFrame()
        line.setFixedHeight(2)
        line.setStyleSheet('background-color: #424754;')
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

    def create_key_concept(self, concept: str):
        chip = QFrame()
        chip.setStyleSheet("""
            QFrame {
                background-color: #212b39;
                border: 1px solid #424754;
                border-radius: 4px;
            }
        """)
        
        layout = QHBoxLayout(chip)
        layout.setContentsMargins(10, 3, 10, 3) 
        layout.setSpacing(7)                    
        
        dot = QFrame()
        dot.setFixedSize(5, 5)
        dot.setStyleSheet("""
            QFrame {
                background-color: #4edea3;
                border-radius: 2px;
                border: none;
            }
        """)
        
        label = QLabel(concept)
        label.setStyleSheet("""
            QLabel {
                color: #d9e3f6;
                font-family: "Inter", sans-serif;
                font-size: 11px;
                font-weight: 400;
                background: transparent;
                border: none;
                padding: 0px;
            }
        """)
        
        layout.addWidget(dot, alignment=Qt.AlignVCenter)
        layout.addWidget(label, alignment=Qt.AlignVCenter)
        self.key_concepts.addWidget(chip)

    def create_probes(self, state: str = None):
        if state == 'none':
            none = QFrame()
            none.setStyleSheet("""
                background-color: #121c2a;
                border: 1px solid #424754;
                border-radius: 4px;
            """)
            none_layout = QVBoxLayout(none)
            none.setFixedSize(98, 56)
            none_layout.setContentsMargins(7, 7, 7, 7)
            none_layout.setSpacing(3)
            none_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            none_icon = QLabel()
            none_icon.setStyleSheet("""
                color: #8c909f;
                background: transparent;
                border: none;
            """)
            none_icon.setPixmap(QIcon("GUI\\Knowledge_Base\\assets\\none_icon.svg").pixmap(20, 20))
            none_layout.addWidget(none_icon, alignment=Qt.AlignmentFlag.AlignCenter)

            none_text = QLabel("NOT TESTED")
            none_text.setStyleSheet("""
                color: #8c909f;
                font-size: 9px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)

            none_layout.addWidget(none_text, alignment=Qt.AlignmentFlag.AlignCenter)

            self.last_probes.addWidget(none)
            return

        probes = QFrame()
        probes.setStyleSheet("""
            background-color: #121c2a;
            border: 1px solid #38c98c;
            border-radius: 4px;
        """)
        layout = QVBoxLayout(probes)
        probes.setFixedSize(98, 56)
        layout.setContentsMargins(7, 7, 7, 7)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if state == "passed":
            verified_icon = QLabel()
            verified_icon.setStyleSheet("""
                color: #4edea3;
                background: transparent;
                border: none;            
            """)
            verified_icon.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\passed_icon.svg').pixmap(20, 20))

            verified_text = QLabel('passed'.upper())
            verified_text.setStyleSheet("""
                color: #c2c6d6;
                font-size: 9px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)

            layout.addWidget(verified_icon, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(verified_text, alignment=Qt.AlignmentFlag.AlignCenter)

            self.last_probes.addWidget(probes)

        elif state == "probing":
            probing = QFrame()
            probing.setFixedSize(98, 56)
            probing.setStyleSheet("""
                background-color: #121c2a;
                border: 1px solid #ffb95f;
                border-radius: 4px;
            """)
            probing_layout = QVBoxLayout(probing)
            probing_layout.setContentsMargins(7, 7, 7, 7)
            probing_layout.setSpacing(3)
            probing_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            probing_icon = QLabel()
            probing_icon.setStyleSheet("""
                color: #ffb95f;
                background: transparent;
                border: none;        
            """)
            probing_icon.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\probing_icon.svg').pixmap(20, 20))
            probing_layout.addWidget(probing_icon, alignment=Qt.AlignmentFlag.AlignCenter)

            probing_text = QLabel('probing'.upper())
            probing_text.setStyleSheet("""
                color: #ffb95f;
                font-size: 9px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)

            probing_layout.addWidget(probing_text, alignment=Qt.AlignmentFlag.AlignCenter)

            self.last_probes.addWidget(probing)

        elif state == "failed":
            failed = QFrame()
            failed.setStyleSheet("""
                background-color: #121c2a;
                border: 1px solid #ffb4ab;
                border-radius: 4px;
            """)
            failed_layout = QVBoxLayout(failed)
            failed.setFixedSize(98, 56)
            failed_layout.setContentsMargins(7, 7, 7, 7)
            failed_layout.setSpacing(3)
            failed_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            failed_icon = QLabel()
            failed_icon.setStyleSheet("""
                color: #ffb4ab;
                background: transparent;
                border: none;
            """)
            failed_icon.setPixmap(QIcon("GUI\\Knowledge_Base\\assets\\failed_icon.svg").pixmap(20, 20))
            failed_layout.addWidget(failed_icon, alignment=Qt.AlignmentFlag.AlignCenter)

            failed_text = QLabel("FAILED")
            failed_text.setStyleSheet("""
                color: #ffb4ab;
                font-size: 9px;
                font-weight: 600;
                background: transparent;
                border: none;
            """)

            failed_layout.addWidget(failed_text,alignment=Qt.AlignmentFlag.AlignCenter)

            self.last_probes.addWidget(failed)

    def set_idenified_gap(self, text: str):
        identified_gap_text = QLabel(text, wordWrap=True)
        identified_gap_text.setStyleSheet("""
            color: #c2c6d6;
            font-size: 14px;
            font-weight: 400;
            background: transparent;
            margin-bottom: 5px;
            border: none;
        """)
        self.identified_gap.addWidget(identified_gap_text)

class KnowledgeBase(QWidget):

    connection = connec('GUI\\Knowledge_Base\\db\\cards_info.db')

    def __init__(self):
        super().__init__()

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.setStyleSheet('background-color: #0b0e15;')

        ###############################
        #            CARDS
        ###############################
        self.scroll_area = QScrollArea(widgetResizable=True)
        self.scroll_area.setStyleSheet('border: none;')
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.vscroll_area = self.scroll_area.verticalScrollBar()
        self.vscroll_area.rangeChanged.connect(self.scroll_to_bottom)

        self.cards_container_widget = QWidget()
        self.cards_container_widget.setContentsMargins(150, 20, 20, 20)
        self.scroll_area.setWidget(self.cards_container_widget)
        self.cards_container_layout = FlowLayout(self.cards_container_widget)
        self.cards_container_layout.setSpacing(20)

        self.arguments = QWidget()
        self.arguments_layout = QVBoxLayout(self.arguments)

        ai_adding_card(self.add_card)
        cards_info.updated.connect(self.add_to_db)

        self.build_cards()
        signals.refresh_card.connect(self.refresh)
        update_nodes.update_total_nodes.connect(self.total_nodes)

        self.mastery_level = header(self.total_nodes())
        self.main_layout.addWidget(self.mastery_level, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.addSpacing(20)
        self.main_layout.addWidget(self.scroll_area)
        self.main_layout.addWidget(self.arguments)
        self.deep_analysis_button(run_agent_in_background, self.total_nodes())
        new_btn_name.updated.connect(self.change_button_name)
        enable_button_clickable.updated.connect(self.enable_button)

        self.setLayout(self.main_layout)

    def total_nodes(self) -> int:
        total_nodes = self.cards_container_layout.count()
        return total_nodes

    def build_cards(self):
        self.all_values = get_all_values(KnowledgeBase.connection)
        self.all_values_without_id = [value[1:] for value in self.all_values]
        for row in self.all_values_without_id:
            card_name, verified_or_wrong, header_category_name, progress_number, key_concepts, probes, identified_gap_text, chat_history = row

            past_cards = Card(card_name, verified_or_wrong, header_category_name, progress_number, convert_str_to_list(key_concepts), convert_str_to_list(probes), identified_gap_text)
            self.cards_container_layout.addWidget(past_cards)

    def refresh(self):
        while self.cards_container_layout.count():
            item = self.cards_container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.build_cards()
        self.mastery_level.set_master_percentage(get_every_card_mastery_percentage())
        self.mastery_level.update_total_nodes(self.total_nodes())

    def add_card(self, card_name, verified_or_wrong, header_category_name, progress_number: int, Key_concepts, Probes, identified_gap_text):

        card = Card(card_name, verified_or_wrong, header_category_name, progress_number, Key_concepts, Probes, identified_gap_text)

        self.cards_container_layout.addWidget(card)
        self.mastery_level.update_total_nodes(self.total_nodes())

        return card

    def add_to_db(self, card_name, verified_or_wrong, header_category_name, progress_number, key_concepts, probes, identified_gap_text, chat_history):

        chat_history = messages.copy()
        messages.clear()

        key_concepts = convert_lists(key_concepts)
        probes = convert_lists(probes)

        KnowledgeBase.connection.execute("""
            INSERT INTO cards_info(
                card_name,
                verified_or_wrong,
                header_category_name,
                progress_number,
                key_concepts,
                last_probes,
                gap,
                chat_history
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """,(card_name, verified_or_wrong, header_category_name, progress_number, key_concepts, probes, identified_gap_text, convert_lists(chat_history)))

        KnowledgeBase.connection.commit()

        self.mastery_level.set_master_percentage(get_every_card_mastery_percentage())
        self.mastery_level.update_value_from_last_session()

    def deep_analysis_button(self, connection, cards_number: int):
        self.button = QPushButton("Generate Deep Analysis")
        self.button.clicked.connect(connection)
        self.button.setObjectName("deepAnalysisBtn")
        self.button.setStyleSheet("""
            QPushButton#deepAnalysisBtn {
                background-color: #34d399;      
                color: #00563b; 
                font-weight: bold;
                font-size: 14px;
                border: none;
                border-radius: 12px;     
                padding: 16px 24px;
            }

            QPushButton#deepAnalysisBtn:hover {
                background-color: #10b981;
                border: 2px solid #10b981;
            }

            QPushButton#deepAnalysisBtn:pressed {
                background-color: #059669;     
            }
        """)

        self.arguments_layout.addWidget(self.button)

    def change_button_name(self, new_name: str):
        self.button.setText(new_name)
        self.button.setEnabled(False)

    def enable_button(self, enabled: bool = False):
        self.button.setEnabled(enabled)

    @Slot(int, int)
    def scroll_to_bottom(self, minimum: int, maximum: int):
        self.vscroll_area.setValue(maximum)
