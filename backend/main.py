import asyncio
import json

import aiohttp

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from helpers.db_helper import DBHelper
from helpers.gpt_helper import GPTHelper
import logging

app = Flask(__name__, static_folder='../frontend/dist')

CORS(
    app)  # Isso irá permitir que qualquer domínio acesse o backend. Em um ambiente de produção, você deve restringir isso.

socketio = SocketIO(app, cors_allowed_origins="*")

# Define a variável para controlar onde o log será gravado
log_to_console = True

# Configura o logging
if log_to_console:
    # Configuração para saída no console
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    logger = logging.getLogger()
else:
    # Configuração para saída em arquivo
    logging.basicConfig(filename='app.log', level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')
    logger = logging.getLogger()

logging.info("teste")
app.logger.info("teste2")





# return index page from vuejs
@app.route('/', methods=['GET'])
def index():
    return app.send_static_file('index.html')


@app.route('/<path:path>', methods=['GET'])
def static_proxy(path):
    return app.send_static_file(path)



@socketio.on('send_message')
def handle_message(data):
    text = data['text']
    case_id = data['case_id']
    npc_id = data['npc_id']
    session_id = request.sid

    with DBHelper() as db, GPTHelper() as gpt:
        historic = db.get_message_history(session_id, npc_id)
        case = db.get_json_caso(case_id)
        case_json = json.loads(case[0])


        historic_json = []
        for message in historic:
            historic_json.append({
                "role": message[4],
                "content": message[3]
            })

        if len(historic_json) == 0:
            prompt = gpt.gerar_prompt_suspeito(npc_id, case_json)
            historic_json.append({
                "role": "system",
                "content": prompt
            })
            print(historic_json)
            db.insert_message_history(session_id, npc_id, prompt, "system")

        db.insert_message_history(session_id, npc_id, text, "user")
        message = {
            "role": "user",
            "content": text
        }
        historic_json.append(message)

        responses = gpt.chat(historic_json, message)
        message_text = ""
        for response in responses:
            if response.choices[0].finish_reason:
                break

            text = response.choices[0].delta.content
            emit('message', text)
            message_text += text

        emit('finish_chat',message_text)


        db.insert_message_history(session_id, npc_id, message_text, "assistant")


# esse endpoint pode demorar muito para responder, pois ele vai criar um caso no GPT-4

def create_case():
    try:
        with GPTHelper() as gpt, DBHelper() as db:
            print("creating case")
            case_json = json.loads(gpt.create_case())
            print("saving case")
            case_id = db.save_case_from_json(case_json)
            return case_id
    except Exception as e:
        print(e)
        return jsonify({"error": "Ocorreu um erro ao criar o caso."}), 500



def init():
    with DBHelper() as db, GPTHelper() as gpt:
        db.create_tables()
        create_case()


init()

def create_new_case():
    with GPTHelper() as gpt, DBHelper() as db:
        cases = db.get_news_cases()

        if cases and len(cases) > 0:
            return cases[0]


# campos enviados  para o frotnend
# case_id
# npc_array
# npc_name
# npc_id
# npc_message_array
# caso_description


def format_setup_json(case, session_id):
    npc_array = []
    print(case)
    print(session_id)

    with DBHelper() as db:
        db.update_play_count(case[0])

        npcs = db.get_npcs(case[0])

        print(npcs)

        for idx, npc in enumerate(npcs):
            npc_message_array = []

            message_history = db.get_message_history(session_id, npc[0])
            print(message_history)
            for message in message_history:
                npc_message_array.append({
                    "role": message[4],
                    "content": message[3]
                })

            npc_array.append({
                "npc_name": npc[2],
                "npc_id": npc[0],
                "npc_index": idx + 1,
                "npc_message_array": npc_message_array
            })

    socketio.emit('setup', {
        "case_id": case[0],
        "npc_array": npc_array,
        "caso_description": case[1]
    })


def initialize_case(case, session_id):
    with GPTHelper() as gpt, DBHelper() as db:
        case_json_str = db.get_json_caso(case[0])
        case_json = json.loads(case_json_str[0])
        response = gpt.gerar_resumo(case_json)
        message_complete = ""
        for message in response:
            if message.choices[0].finish_reason:
                break

            text = message.choices[0].delta.content
            message_complete += text
            socketio.emit('message_officer', text)

        socketio.emit('finish_chat_officer', message_complete)

        db.insert_message_history(session_id, 0, message_complete, "Officer")




@socketio.on('setup')
def setup(data):
    if data['case_id'] is not None:
        case_id = data['case_id']
        session_id = request.sid
        with GPTHelper() as gpt, DBHelper() as db:
            case = db.get_case(case_id)
            db.insert_sessao(session_id, case_id)
        format_setup_json(case, session_id)
        initialize_case(case, session_id)
    else:
        case = create_new_case()
        session_id = request.sid
        format_setup_json(case, session_id)
        initialize_case(case, session_id)


@socketio.on('submit_answer')
def submit_answer(data):
    case_id = data['case_id']
    npc_id = data['npc_id']
    session_id = request.sid

    with DBHelper() as db:
        db.insert_answer(session_id, npc_id)
        npc = db.get_npc(npc_id)
        if npc[10]:
            socketio.emit('finish_case', "Parabéns, você prendeu o suspeito!")
        else:
            socketio.emit('finish_case', "Você prendeu o suspeito errado!")


@socketio.on('new_case')
def new_case(data):
    quantity = data['quantity']
    for i in range(0, quantity):
        create_case()
        socketio.emit('new_case', "Novo caso criado!")


if __name__ == '__main__':
    app.run(port=8000, debug=True)
