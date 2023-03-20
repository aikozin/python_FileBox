import os
import uuid

from flask import Flask, request, jsonify, send_file
import data_controller
import session_controller
import db_connector
import threading
from datetime import time

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000  # ограничение размера файла в 100 МБ

TYPE_FILES = ['text', 'file']
STATUS_FILES = ['created', 'in process', 'loaded']
UPLOAD_FOLDER = 'D:\\000FileBox'


@app.route("/session/start", methods=['POST'])
def session_start():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionstart---start-sessii/
    """

    request_data = request.get_json()
    if request_data:
        if 'web_ip' not in request_data or 'web_agent' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        web_ip = request_data['web_ip']
        web_agent = request_data['web_agent']
        if not web_ip or not web_agent:
            return jsonify(error='Ошибка в параметрах запроса'), 400
    else:
        return jsonify(error='Ошибка в параметрах запроса'), 400
    id_session = str(uuid.uuid4())
    session_controller.session_start(id_session, web_ip, web_agent)
    return jsonify(id_session=id_session)


@app.route("/session/mobile/connect", methods=['POST'])
def session_mobile_connect():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/vapv/
    """

    request_data = request.get_json()
    if request_data:
        if 'mobile_ip' not in request_data or 'mobile_agent' not in request_data or 'id_session' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        mobile_ip = request_data['mobile_ip']
        mobile_agent = request_data['mobile_agent']
        id_session = request_data['id_session']
        if not mobile_ip or not mobile_agent or not id_session:
            return jsonify(error='Ошибка в параметрах запроса'), 400
    else:
        return jsonify(error='Ошибка в параметрах запроса'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Такая сессия не существует'), 400

    session_controller.session_mobile_connect(id_session, mobile_ip, mobile_agent)
    session_controller.update_time_end(id_session)
    session = session_controller.get_session_info(id_session)
    return jsonify(
        time_start=session['time_start'],
        time_end=session['time_end'],
        web_ip=session['web_ip'],
        web_agent=session['web_agent']
    )


@app.route("/data/send", methods=['POST'])
def send_data():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/datasend/
    """

    if 'file' not in request.files:
        return jsonify(error='Файл отсутствует или ошибка получения файла'), 400
    file = request.files['file']
    id_session = request.args.get('id_session', '')
    type_file = request.args.get('type', '')
    if not id_session or not type_file:
        return jsonify(error='Ошибка в параметрах запроса'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Такая сессия не существует'), 400
    if type_file not in TYPE_FILES:
        return jsonify(error='Тип файла не действителен'), 400

    file_name_real = file.filename
    file_name_fs = id_session[:5] + str(uuid.uuid4()) + os.path.splitext(file_name_real)[1]
    data_controller.send_data_db(id_session, type_file, file_name_real, file_name_fs)
    data_controller.send_data_fs(file_name_fs, file)
    return '', 200


@app.route("/data/check", methods=['GET'])
def check_data():
    """

    """

    request_data = request.get_json()
    if request_data:
        if 'id_session' not in request_data or 'status' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        id_session = request_data['id_session']
        status = request_data['status']
        if not id_session or not status:
            return jsonify(error='Ошибка в параметрах запроса'), 400
    else:
        return jsonify(error='Ошибка в параметрах запроса'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Такая сессия не существует'), 400
    if status not in STATUS_FILES:
        return jsonify(error='Статус файла не действителен'), 400

    result = data_controller.get_user_files_info(id_session, status)
    return jsonify(files=result)


@app.route("/data/get", methods=['GET'])
def get_data():
    """

    """

    id_session = request.args.get('id_session', '')
    id_file = request.args.get('id_file', '')
    file_info = data_controller.get_file_info(id_file, id_session)
    return send_file(os.path.join(UPLOAD_FOLDER, file_info['file_name_fs']), download_name=file_info['file_name_real'])


class TrashCollector(threading.Thread):
    def __init__(self):
        super().__init__()
        self.stop = threading.Event()

    def run(self):
        while not self.stop.wait(10):
            proc_to_call()


def proc_to_call():
    print('trash_collector in progress...', time)
    db = db_connector.create_connection()
    query = 'SELECT id_session FROM session WHERE now() > time_end'
    with db.cursor() as cursor:
        cursor.execute(query)
        deletes_sessions = tuple((id_session for id_session in cursor.fetchall()))

    data_query = 'SELECT file_name_fs FROM data WHERE id_session = %s'
    deletes_data = set()
    for value in deletes_sessions:
        with db.cursor() as cursor:
            cursor.execute(data_query, value)
            # deletes_data.add(*cursor.fetchall())
            [deletes_data.add(name) for name in cursor.fetchall()]
    data_query = 'SELECT file_name_fs FROM data WHERE now() > time_death'
    with db.cursor() as cursor:
        cursor.execute(data_query)
        [deletes_data.add(name) for name in cursor.fetchall()]

    session_query = 'DELETE FROM session WHERE id_session = %s'
    for value in deletes_sessions:
        with db.cursor() as cursor:
            cursor.execute(session_query, value)
            db.commit()
    db.close()
    [os.remove(*file_path) for file_path in deletes_data if os.path.exists(*file_path)]
    return deletes_sessions


trash_collector = TrashCollector()

if __name__ == "__main__":
    trash_collector.start()
    app.run(debug=True)
