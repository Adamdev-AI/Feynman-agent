from ai.main_ai import api_key
from ai.signals import new_btn_name, enable_button_clickable
from datetime import date
from GUI.Knowledge_Base.feynman_pdf_template import build_feynman_report
from GUI.Knowledge_Base.snake_game import game
from mistralai.client import Mistral
from mistralai.client.models import FunctionResultEntry
from ai.tools import run_sql_code, generate_deep_report_schema, search_schema
from ai.instructions import deep_analysis_ai_prompt
from pathlib import Path
from dotenv import load_dotenv
from tavily import TavilyClient
from PySide6.QtCore import QThreadPool, QRunnable
import os
import json
import sqlite3

load_dotenv("api.env")

tavily_api_key = os.getenv("TAVILY_CLIENT") 

current_dir = Path(__file__).resolve().parent.parent.parent / "reports"

class runDeepButton(QRunnable):
    def run(self):
        generate_deep_report()

class RunGame(QRunnable):
    def run(self):
        game()

def run_agent_in_background():
    task = runDeepButton()
    game = RunGame()
    QThreadPool.globalInstance().start(game)
    QThreadPool.globalInstance().start(task)

def get_connec(db_name):
    return sqlite3.connect(db_name)

def run_sql(query: str):
    try:
        connection = get_connec('GUI\\Knowledge_Base\\db\\cards_info.db')
        value = connection.execute(query).fetchall()

        connection.commit()

        connection.close()

        return value
    except Exception as e:
        return f"There was an error: {e}"

def search_web(query: str):
    client = TavilyClient(tavily_api_key)
    response = client.search(
        query=query,
        include_answer="advanced",
        search_depth="advanced"
    )
    return response

name = None

def generate_deep_report():
    global name

    # Change the button name when clicked
    new_btn_name.updated.emit("Wait the report will open right now...")

    with open("GUI\\Knowledge_Base\\user_info.json", 'r', encoding='utf-8') as file:
        info = json.load(file)
        UserName_check = info.get("user_name")
        if not UserName_check:
            while True:
                name = input("Please enter your name: ").capitalize()
                if not name.strip():
                    continue
                break
            info["user_name"] = name

            with open("GUI\\Knowledge_Base\\user_info.json", 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=4)

        else:
            name = info.get("user_name")

    mistral_client = Mistral(api_key=api_key)

    tools = {
        "run_sql": run_sql,
        "build_feynman_report": build_feynman_report,
        "search_web": search_web
    }

    with open('ai\\agent_info.json', 'r') as f:
        info = json.load(f)
        agent_id = info.get('deep_analysis_ai')

        if not agent_id:
            main_agent = mistral_client.beta.agents.create(
                model='mistral-medium-3-5',
                name='deep_analysis_ai',
                description='You are an agent that use pdf template to make analysis for the user performance in a pdf file.',
                tools=[run_sql_code, generate_deep_report_schema, search_schema],
                instructions=deep_analysis_ai_prompt,
                completion_args={
                    "reasoning_effort": "high"
                }
            )

            agent_id = main_agent.id
            info['deep_analysis_ai'] = agent_id
            with open('ai\\agent_info.json', 'w') as file:
                json.dump(info, file, indent=4)
        else:
            agent_id = info.get('deep_analysis_ai')


        response = mistral_client.beta.conversations.start(
            agent_id=agent_id,
            inputs=[{'role': 'user', 'content': f"Do your job., User name = {name}, today's date = {date.today()}, and here is where the reports folder (the place you will put in it the pdf file): {current_dir}"}]
        )

        message = response.outputs[-1]

        while message.type == 'function.call':
            try:
                args = json.loads(message.arguments)
                function_result = json.dumps(tools.get(message.name)(**args))

            except Exception as e:
                function_result = json.dumps({"error": f"function {message.name} failed: {e}"})
            provide_result_agent = FunctionResultEntry(
                tool_call_id = message.tool_call_id,
                result = function_result,
            )
            print(provide_result_agent)

            response = mistral_client.beta.conversations.append(
                conversation_id=response.conversation_id,
                inputs=[provide_result_agent]
            )

            message = response.outputs[-1]

            print(message)
        print(message)

        new_btn_name.updated.emit("Generate Deep Analysis")
        enable_button_clickable.updated.emit(True)