import os
import uuid

from flask import Flask, request, jsonify

import data_controller
import session_controller

app = Flask(__name__)
# ограничение размера файла в 100 МБ
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000

TYPE_FILES = ['text', 'file']
STATUS_FILES = ['created', 'in process', 'loaded']
UPLOAD_FOLDER = 'D:\\000FileBox'


@app.route("/session/start", methods=['POST'])
def session_start():
    # получаем json информацию от клиента в массив request_data
    request_data = request.get_json()
    # вытягиваем из json web_ip и web_agent
    if request_data:
        if 'web_ip' not in request_data or 'web_agent' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        web_ip = request_data['web_ip']
        web_agent = request_data['web_agent']
        if web_ip == '' or web_agent == '':
            return jsonify(error='Ошибка в параметрах запроса'), 400
    else:
        return jsonify(error='Ошибка в параметрах запроса'), 400

    # бесконечный цикл
    while True:
        # генерируем id
        id_session = str(uuid.uuid4())
        # проверяем свободен ли id в БД, если свободен - выходим из цикла
        if session_controller.check_free_id(id_session):
            break
    # сохраняем информацию в БД методом sessionStart
    session_controller.session_start(id_session, web_ip, web_agent)
    # возвращаем пользователю json с id
    return jsonify(id_session=id_session)


@app.route("/session/mobile/connect", methods=['POST'])
def session_mobile_connect():
    request_data = request.get_json()
    if request_data:
        if 'mobile_ip' not in request_data or 'mobile_agent' not in request_data or 'id_session' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        mobile_ip = request_data['mobile_ip']
        mobile_agent = request_data['mobile_agent']
        id_session = request_data['id_session']
        if mobile_ip == '' or mobile_agent == '' or id_session == '':
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
    # получаем загружаемый файл
    if 'file' not in request.files:
        return jsonify(error='Файл отсутствует или ошибка получения файла'), 400
    file = request.files['file']
    # вытягиваем id_session и type из path запроса
    id_session = request.args.get('id_session', '')
    type_file = request.args.get('type', '')
    if id_session == '' or type_file == '':
        return jsonify(error='Ошибка в параметрах запроса'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Такая сессия не существует'), 400
    if type_file not in TYPE_FILES:
        return jsonify(error='Тип файла не действителен'), 400

    # получаем настоящее имя файла
    file_name_real = file.filename
    # генерируем имя для файла в файловой системе из части id_session + uuid + расширение файла
    file_name_fs = id_session[:5] + str(uuid.uuid4()) + os.path.splitext(file_name_real)[1]
    # сохраняем информацию о файле в БД
    data_controller.send_data_db(id_session, type_file, file_name_real, file_name_fs)
    # сохраняем файл в файловой системе
    data_controller.send_data_fs(file_name_fs, file)
    return '', 200


@app.route("/data/check", methods=['GET'])
def check_data():
    # получаем json информацию от клиента в массив request_data
    request_data = request.get_json()
    if request_data:
        if 'id_session' not in request_data or 'status' not in request_data:
            return jsonify(error='Ошибка в параметрах запроса'), 400
        id_session = request_data['id_session']
        status = request_data['status']
        if id_session == '' or status == '':
            return jsonify(error='Ошибка в параметрах запроса'), 400
    else:
        return jsonify(error='Ошибка в параметрах запроса'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Такая сессия не существует'), 400
    if status not in STATUS_FILES:
        return jsonify(error='Статус файла не действителен'), 400

    # получаем массив файлов
    result = data_controller.get_files_info(id_session, status)
    # возвращаем пользователю json с массивом файлов files
    return jsonify(files=result)


if __name__ == "__main__":
    app.run(debug=True)
