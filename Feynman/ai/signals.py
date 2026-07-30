from PySide6.QtCore import QObject, Signal

class global_signals(QObject):
    refresh_card = Signal()

signals = global_signals()

class update_total_nodes_from_sql(QObject):
    update_total_nodes = Signal()

update_nodes = update_total_nodes_from_sql()

class from_last_session_signal(QObject):
    updated = Signal()

update_from_last_session = from_last_session_signal()

class add_cards_info_to_db_signal(QObject):
    updated = Signal(str, str, str, int, list, list, str, list)

cards_info = add_cards_info_to_db_signal()

class ChangeButtonNameWhenClicked(QObject):
    updated = Signal(str)

new_btn_name = ChangeButtonNameWhenClicked()

class enable_the_button(QObject):
    updated = Signal(bool)

enable_button_clickable = enable_the_button()