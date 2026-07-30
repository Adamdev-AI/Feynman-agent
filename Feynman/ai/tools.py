# Creating FeedBacks

feedbacks = {
    "type": "function",
    "function": {
        "name": "feedbacks_func",
        "description": "show feedback messages for the user, and it's only three things: error, weak, verified, you will use the error when the user user have responded error, And the weak when the user responded in weak explination and verified when he is true",
        "parameters": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "error/weak/verified",
                },
                "text": {
                    "type": "string",
                    "description": "Your reply about the user response maximum 120 Characters, and in it will be what he got wrong, weak wrong, or everything is right, and things like this",
                },
                "note": {
                    "type": "string",
                    "description": "Enter a 2 maximum words would be something like: Missing concept, or Not clear, Amazing, clear explination, and things like this."
                }
            },
            "required": ["role",
                         "text",
                         "note"],
        },
    },
}

# Make a card in the knowledge base

card = {
    "type": "function",
    "function": {
        "name": "add_card",
        "description": "Here you will put an card that contain informations that in the future you can ask the user about these topics, and it's will be also visible for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "card_name": {
                    "type": "string",
                    "description": "The name of the card, (Make it about a small topic for example: Backpropagation, or Probabilitys)",
                },
                "verified_or_wrong": {
                    "type": "string",
                    "description": "Here you will put that did the user last time answered true or not, (THIS SHOULD BE ONLY EITHER verified OR failed)",
                },
                "header_category_name": {
                    "type": "string",
                    "description": "The category of the card could be math, neural networks, etc."
                },
                "progress_number": {
                    "type": "integer",
                    "description": "The progress of the user to understand this topic, (FROM 0 TO 100)."
                },
                "Key_concepts": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list of 2-5 short tags naming the core ideas of this topic, each tag 2-4 words max (e.g. 'LIFO order', 'push/pop operations') — NOT full sentences or explanations."
                },
                "Probes": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "A list containing EXACTLY ONE value: 'passed', 'probing', or 'failed' — your overall verdict for how the student did on this topic as a whole."
                },
                "identified_gap_text" : {
                    "type": "string",
                    "description": "If there is gaps in the user understanding, don't make it short or to long, and if there is not leave it by: None"
                }
            },
            "required": ["card_name",
                         "verified_or_wrong",
                         "header_category_name",
                         "progress_number",
                         "Key_concepts",
                         "Probes",
                         "identified_gap_text"],
        },
    },
}

run_sql_code = {
    "type": "function",
    "function": {
        "name": "run_sql",
        "description": "Will make you able to run sqlite3 python code on user database, To get all of his cards informations",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The sqlite3 code",
                },
            },
            "required": ["query"]
        },
    },
}

cmd = {
    "type": "function",
    "function": {
        "name": "run_cmd_commands",
        "description": "Will make you able to run CMD commands on the user terminal, you can install packages, libraries, code",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command prompt",
                },
            },
            "required": ["command"]
        },
    },
}

search_schema = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Will make you able to search on google with a query and get results, Use this tool when you don't understand or not sure from something",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The thing you want to search",
                },
            },
            "required": ["query"]
        },
    },
}

make_file = {
    "type": "function",
    "function": {
        "name": "write_file",
        "description": "Will make you able to create files",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path you want the file to be in",
                },
                "content": {
                    "type": "string",
                    "description": "The content of the file"
                },
            },
            "required": ["path", "content"]
        },
    },
}

generate_deep_report_schema = {
    "type": "function",
    "function": {
        "name": "build_feynman_report",
        "description": "Will make you able to create pdf file using a template",
        "parameters": {
            "type": "object",
            "properties": {
                "cards": {
                    "type": "array",
                    "description": "All the cards.",
                },
                "output_path": {
                    "type": "string",
                    "description": "The path you want the file to be."
                },
                "student_name": {
                    "type": "string",
                    "description": "the student name."
                },
                "narrative": {
                    "type": "string",
                    "description": "The narrative things in the user explination."
                }
            },
            "required": ["cards", "output_path", "student_name", "narrative"]
        },
    },
}

