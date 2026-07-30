from PySide6.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QFrame
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from datetime import date
from ai.signals import update_from_last_session
import sqlite3

def get_connec(db_name: str):
    try:
        return sqlite3.connect(db_name)
    except Exception as e:
        print(e)

def create_table(connection: str):
    query = """
    CREATE TABLE IF NOT EXISTS mastery_level(
        mastery_percentage INTEGER DEFAULT 0,
        last_session INTEGER DEFAULT 0,
        total_nodes INTEGER NOT NULL DEFAULT 0,
        current_streak INTEGER NOT NULL DEFAULT 0,
        last_active_date TEXT
    )
    """

    connection.execute(query)
    connection.commit()

def ensure_row_exists(connection: str):
    exists = connection.execute("SELECT 1 FROM mastery_level").fetchone()
    if not exists:
        connection.execute("INSERT INTO mastery_level DEFAULT VALUES")
        connection.commit()

def check_in(connection):
    today = date.today().isoformat()
    yesterday = date.fromordinal(date.today().toordinal() - 1).isoformat()

    current_streak, last_active_date = connection.execute(
        "SELECT current_streak, last_active_date FROM mastery_level"
    ).fetchone()

    if last_active_date == today:
        return current_streak

    current_streak = current_streak + 1 if last_active_date == yesterday else 1

    connection.execute(
        "UPDATE mastery_level SET current_streak = ?, last_active_date = ?",
        (current_streak, today),
    ) 

    connection.commit()

    return current_streak

def get_value(connection, value_name: str, is_int: int | None = None, is_str: str | None = None, table_name: str = 'mastery_level', fetchall: bool | None = None):

    if fetchall:
        value = connection.execute(f"SELECT {value_name} FROM {table_name}").fetchall()
        
        return value    

    value = connection.execute(f"SELECT {value_name} FROM {table_name}").fetchone()
    if not value:
        return None
    
    row_value = value[0]

    if is_int:
        as_int = int(row_value)
        return as_int

    elif is_str:
        as_str = str(row_value)
        return as_str

    connection.close()
    
    return value

def get_every_card_mastery_percentage():
    connection = get_connec('GUI\\Knowledge_Base\\db\\cards_info.db')
    all_cards_percen = connection.execute("SELECT progress_number FROM cards_info").fetchall()

    if not all_cards_percen:
        return 0

    all_values = []

    for card in all_cards_percen:
        value = card[0]
        all_values.append(value)

    over_all_percentage = sum(all_values) / len(all_values)

    return round(over_all_percentage)

def update_values(connection, value_in_db, new_value):
    connection.execute(f"UPDATE mastery_level SET {value_in_db} = ?",
                       (new_value,))

    connection.commit()

def main():
    connection = get_connec('GUI\\Knowledge_Base\\db\\Mastery_level.db')
    create_table(connection)
    ensure_row_exists(connection)
    check_in(connection)

main()

class header(QWidget):
    connection = get_connec('GUI\\Knowledge_Base\\db\\Mastery_level.db')

    def __init__(self, total_nodes):
        super().__init__()



        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet('background-color: #050f1c')
        self.setFixedHeight(90)

        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Mastery percentage
        self.mastery_level_header = QWidget()
        self.mastery_level_header_layout = QVBoxLayout(self.mastery_level_header)
        self.mastery_level_header_layout.setContentsMargins(60, 0, 0, 0)

        self.mastery_percentage = QLabel()
        self.mastery_level_header_layout.addWidget(self.mastery_percentage)

        # header info
        self.header_info = QWidget()
        self.header_info_layout = QHBoxLayout(self.header_info)

        # Overall mastery
        self.overall_header = QWidget()
        self.overall_header_layout = QVBoxLayout(self.overall_header)


        self.over_all_mastery = QLabel("overall mastery".upper())
        self.over_all_mastery.setStyleSheet('font-weight: bold; font-size: 15px')
        self.over_all_mastery_value = QHBoxLayout()
        self.over_all_mastery_value.setContentsMargins(0, 0, 0, 0)
        self.over_all_mastery_value.setSpacing(0)
        self.from_last_session_percen(self.over_all_mastery_value, self.get_last_session_value())
        update_from_last_session.updated.connect(self.update_value_from_last_session)
        update_values(header.connection, 'last_session', get_value(header.connection, 'mastery_percentage', True))
        self.overall_header_layout.addWidget(self.over_all_mastery)
        self.overall_header_layout.addLayout(self.over_all_mastery_value)
        self.overall_header_layout.setSpacing(0)

        self.header_info_layout.addWidget(self.overall_header)
        self.separator(self.header_info_layout)

        # Total nodes
        self.total_nodes = QWidget()
        self.total_nodes_layout = QVBoxLayout(self.total_nodes)

        update_values(header.connection, 'total_nodes', total_nodes)
        total_nodes = get_value(header.connection, 'total_nodes', is_int=True)
        if total_nodes == 0:
            total_nodes = '0'

        self.creating_labels(self.total_nodes_layout, self.total_nodes, 'total nodes', 'font-weight: bold; font-size: 15px')
        self.total_nodes_value_label = self.creating_values(self.total_nodes_layout, integer_value=total_nodes, stylesheet='font-weight: bold; font-size: 20px; color: #34d399')

        # Current streak 
        self.current_streak = QWidget()
        self.current_streak_layout = QVBoxLayout(self.current_streak)

        current_streak = get_value(header.connection, 'current_streak', False, True)
        
        self.creating_labels(self.current_streak_layout, self.current_streak, 'current streak', 'font-weight: bold; font-size: 15px;', False)
        self.creating_values(self.current_streak_layout, string_value=current_streak, stylesheet='font-weight: bold; font-size: 20px; color: #34d399')

        self.master_percentage = get_every_card_mastery_percentage()

        self.set_master_percentage(self.master_percentage)
        self.main_layout.addWidget(self.mastery_level_header, alignment=Qt.AlignmentFlag.AlignTop)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.header_info, alignment=Qt.AlignmentFlag.AlignBottom)
        self.main_layout.addStretch()
        self.setLayout(self.main_layout)


    def set_master_percentage(self, number: int):
        if number >= 70:
            self.mastery_percentage.setStyleSheet("color: #34d399; font-size: 50px; font-weight: bold")

        elif number >= 50 and number < 70:
            self.mastery_percentage.setStyleSheet("color: #fbbf24; font-size: 50px; font-weight: bold")

        elif number < 50:
            self.mastery_percentage.setStyleSheet("color: #f87171; font-size: 50px; font-weight: bold")

        self.percentage_number = str(f"{number}%")
        self.set_percentage = self.mastery_percentage.setText(self.percentage_number)
        self.set_master_percentage_inDB(connection=header.connection, number=number)

    def separator(self, layout):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.VLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet('background-color: #08121f')
        layout.addWidget(separator)

    def update_total_nodes(self, total_nodes: int):
        update_values(header.connection, 'total_nodes', total_nodes)
        self.total_nodes_value_label.setText(str(total_nodes))

    def from_last_session_percen(self, label_layout, number: int):

        self.icon_label = QLabel()
        self.last_session_text_label = QLabel()

        icon_label_layout = QHBoxLayout()

        if number >= 0:
            self.icon_label.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\up_arrow_icon.svg').pixmap(16,16))
            value = f'{number}% from last session'
            self.last_session_text_label.setStyleSheet('color: #34d399')
            self.last_session_text_label.setText(value)
            icon_label_layout.addWidget(self.icon_label)
            icon_label_layout.addSpacing(6)
            icon_label_layout.addWidget(self.last_session_text_label)
            label_layout.addLayout(icon_label_layout)

        elif number < 0:
            self.icon_label.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\down_arrow_icon.svg').pixmap(16,16))
            value = f'{number}% from last session'
            self.last_session_text_label.setStyleSheet('color: #f87171')
            self.last_session_text_label.setText(value)
            icon_label_layout.addWidget(self.icon_label)
            icon_label_layout.addSpacing(6)
            icon_label_layout.addWidget(self.last_session_text_label)
            label_layout.addLayout(icon_label_layout)

    def creating_labels(self, layout, widget, text, stylesheet, seperate = True):
        self.label = QLabel(text.upper())
        self.label.setStyleSheet(stylesheet)
        layout.addWidget(self.label)
        self.header_info_layout.addWidget(widget)

        if seperate:
            self.separator(self.header_info_layout)

            
    def creating_values(self, layout, integer_value: int | None = None, string_value: str | None = None, stylesheet: str = ""):
        if integer_value:
            self.label = QLabel(str(integer_value))

        else:
            self.label = QLabel(string_value)

        self.label.setStyleSheet(stylesheet)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        return self.label


    def set_master_percentage_inDB(self, connection, number: int):
        connection.execute("UPDATE mastery_level SET mastery_percentage = ?",
                        (number,))

        connection.commit()

    def get_last_session_value(self):
        current_session = get_value(header.connection, 'mastery_percentage', True, fetchall=True)[0][0]
        print(current_session)
        last_session = get_value(header.connection, 'last_session', True, fetchall=True)[0][0]
        print(last_session)

        change_from_last_session = current_session - last_session

        return change_from_last_session

    def update_value_from_last_session(self):
        number = self.get_last_session_value()
        style = 'color: #34d399' if number >= 0 else 'color: #f87171'
        if number >= 0:
            self.icon_label.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\up_arrow_icon.svg').pixmap(16,16))
            
        else:
            self.icon_label.setPixmap(QIcon('GUI\\Knowledge_Base\\assets\\down_arrow_icon.svg').pixmap(16,16))

        self.last_session_text_label.setStyleSheet(style)
        self.last_session_text_label.setText(f'{number}% from last session')