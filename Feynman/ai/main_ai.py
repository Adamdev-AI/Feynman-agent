from mistralai.client import Mistral
from mistralai.client.models import FunctionResultEntry
from dotenv import load_dotenv
from ai.tools import feedbacks, card, run_sql_code, search_schema
from ai.instructions import prompt
from ai.signals import signals, update_nodes, cards_info
from PySide6.QtCore import QObject, Signal, Slot
from tavily import TavilyClient
import os
import json
import sqlite3

load_dotenv('ai\\api.env')
api_key = os.getenv('MISTRAL_CLIENT')
tavily_api_key = os.getenv("TAVILY_CLIENT")

mistral_client = Mistral(api_key=api_key)

def get_connec(db_name):
    return sqlite3.connect(db_name)

def run_sql(query: str):
    connection = get_connec('GUI\\Knowledge_Base\\db\\cards_info.db')
    value = connection.execute(query).fetchall()

    connection.commit()

    signals.refresh_card.emit()

    connection.close()

    update_nodes.update_total_nodes.emit()

    return value

def search_web(query: str):
    client = TavilyClient(tavily_api_key)
    response = client.search(
        query=query,
        include_answer="advanced",
        search_depth="advanced"
    )
    return response

tools = {
    "run_sql": run_sql,
    "search_web": search_web
}

messages = []

_card_signal = None

class handle_card_signal(QObject):
    card_signal = Signal(str, str, str, int, list, list, str)

    def __init__(self, card):
        super().__init__()

        self.card = card
        self.card_signal.connect(self.call_card)

    def call_card(self, card_name, verified_or_wrong, header_category_name, progress_number: int, Key_concepts, Probes, identified_gap_text):
        self.card(card_name, verified_or_wrong, header_category_name, progress_number, Key_concepts, Probes, identified_gap_text)

def ai_adding_card(card):
    global _card_signal
    _card_signal = handle_card_signal(card)
    tools['add_card'] = lambda card_name, verified_or_wrong, header_category_name, progress_number, Key_concepts, Probes, identified_gap_text : (
        _card_signal.card_signal.emit(card_name, verified_or_wrong, header_category_name, progress_number, Key_concepts, Probes, identified_gap_text) or 'Card Added'
    )


class SideBarBridge(QObject):
    feedback_signal = Signal(str, str, str)

    def __init__(self, sidebar):
        super().__init__()
        self.sidebar = sidebar
        self.feedback_signal.connect(self.handle_feedback)

    @Slot(str, str, str)
    def handle_feedback(self, role, text, note):
        self.sidebar.ai_message_feedback(role, text, note)

_bridge = None

def register_sidebar(sidebar_instance):
    global _bridge
    _bridge = SideBarBridge(sidebar_instance)
    tools['feedbacks_func'] = lambda role, text, note: (
        _bridge.feedback_signal.emit(role, text, note) or 'Done.'
    )

with open('ai\\agent_info.json', 'r') as f:
    info = json.load(f)
    agent_id = info.get('agent_id')

    if not agent_id:
        main_agent = mistral_client.beta.agents.create(
            model='mistral-medium-3-5',
            name='Feynman Agent',
            description='You are an agent that use Feynman Technique, to test learners.',
            tools=[feedbacks, card, run_sql_code, search_schema],
            instructions=prompt,
            completion_args={
                "reasoning_effort": "high"
            }
        )

        agent_id = main_agent.id
        info['agent_id'] = agent_id
        with open('ai\\agent_info.json', 'w') as file:
            json.dump(info, file, indent=4)
    else:
        agent_id = info.get('agent_id')

conversation_id = None

def conversation(text: str):
    global conversation_id
    messages.append({'role': 'user', 'content': text})
    if conversation_id is None:

        response = mistral_client.beta.conversations.start(
            agent_id=agent_id,
            inputs=[{'role': 'user', 'content': text}]
        )
        conversation_id = response.conversation_id

    else:
        response = mistral_client.beta.conversations.append(
            conversation_id=conversation_id,
            inputs=[{'role': 'user', 'content': text}]
        )
        
    message = response.outputs[-1]

    pending_card = None
    last_card = None

    while message.type == 'function.call':

        try:
            args = json.loads(message.arguments)
            function_result = json.dumps(tools.get(message.name)(**args))

            if message.name == "add_card":
                pending_card = args
                last_card = message.name

        except Exception as e:
            function_result = json.dumps({"error": f"function {message.name} failed: {e}"})
        provide_result_agent = FunctionResultEntry(
            tool_call_id = message.tool_call_id,
            result = function_result,
        )

        print(f"{message.name} will be called, And this is it's id: {message.tool_call_id}")

        response = mistral_client.beta.conversations.append(
            conversation_id=response.conversation_id,
            inputs=[provide_result_agent]
        )

        message = response.outputs[-1]

        print(message)

    messages.append({'role': 'assistant', 'content': str(message)})

    for output in message.content:  
        if output.type == 'text':
            if last_card:
                cards_info.updated.emit(
                    pending_card["card_name"],
                    pending_card["verified_or_wrong"],
                    pending_card["header_category_name"],
                    pending_card["progress_number"],
                    pending_card["Key_concepts"],
                    pending_card["Probes"],
                    pending_card["identified_gap_text"],
                    messages
                )
            return output.text

def new_chat():
    global conversation_id
    conversation_id = None