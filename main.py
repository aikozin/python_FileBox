import uuid

from flask import Flask, request, jsonify

import sessionController

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
        # проверяем свободен ли id в БД. Если свободен - выходим из цикла
        if sessionController.check_free_id(id):
            break
    # сохраняем информацию в БД методом sessionStart
    sessionController.session_start(id, web_ip, web_agent)
    # возвращаем пользователю json с id
    return jsonify(id=id)


if __name__ == "__main__":
    app.run(debug=True)
