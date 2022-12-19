import os
import uuid

from flask import Flask, request, jsonify

import data_controller
import session_controller

app = Flask(__name__)


@app.route("/session/start", methods=['POST'])
def session_start():
    # получаем json информацию от клиента в массив request_data
    request_data = request.get_json()
    # вытягиваем из json web_ip и web_agent
    web_ip = request_data['web_ip']
    web_agent = request_data['web_agent']

    id = ''
    # бесконечный цикл
    while True:
        # генерируем id
        id = str(uuid.uuid4())
        # проверяем свободен ли id в БД, если свободен - выходим из цикла
        if session_controller.check_free_id(id):
            break
    # сохраняем информацию в БД методом sessionStart
    session_controller.session_start(id, web_ip, web_agent)
    # возвращаем пользователю json с id
    return jsonify(id=id)


@app.route("/session/mobile/connect", methods=['POST'])
def session_mobile_connect():
    request_data = request.get_json()
    mobile_ip = request_data['mobile_ip']
    mobile_agent = request_data['mobile_agent']
    id = request_data['id']

    session_controller.session_mobile_connect(id, mobile_ip, mobile_agent)
    session_controller.update_time_end(id)
    session = session_controller.get_session_info(id)
    return jsonify(
        time_start=session['time_start'],
        time_end=session['time_end'],
        web_ip=session['web_ip'],
        web_agent=session['web_agent']
    )


@app.route("/data/send", methods=['POST'])
def send_data():
    # получаем загружаемый файл
    try:
        file = request.files['file']
    except:
        return jsonify(error='Файл отсутствует или ошибка получения файла'), 400
    # вытягиваем id_session и type из path запроса

    id_session = request.args.get('id', '')
    type = request.args.get('type', '')
    if id_session == '' or type == '':
        return jsonify(error='Ошибка в параметрах запроса'), 400
    # получаем настоящее имя файла
    file_name_real = file.filename
    # генерируем имя для файла в файловой системе из части id_session + uuid + расширение файла
    file_name_fs = id_session[:5] + str(uuid.uuid4()) + os.path.splitext(file_name_real)[1]
    # сохраняем инфу о файле в БД
    data_controller.send_data_db(id_session, type, file_name_real, file_name_fs)
    # сохраняем файл в файловой системе
    data_controller.send_data_fs(file_name_fs, file)
    return '', 200


@app.route("/data/check", methods=['GET'])
def check_data():
    # получаем json информацию от клиента в массив request_data
    request_data = request.get_json()
    # вытягиваем из json id_session и status
    id_session = request_data['id_session']
    status = request_data['status']
    # получаем массив файлов
    result = data_controller.get_files_info(id_session, status)
    # возвращаем пользователю json с массивом файлов files
    return jsonify(files=result)


if __name__ == "__main__":
    app.run(debug=True)
