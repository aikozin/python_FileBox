import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from flask_socketio import SocketIO, emit
import data_controller
import session_controller
from utils.trash_collector import trash_collector
from configuration import config

app = Flask(__name__)
app.config.from_object(config)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('new_client')
def handle_new_client(data):
    # client_ip = request.remote_addr
    # print(f'New client IP address {client_ip} has been connected')
    device_sid, id_session, device_type = request.sid, data.get('id_session'), data.get('type')
    session_controller.on_connect(id_session, device_sid, device_type)


@app.route("/session/start", methods=['POST'])
def session_start():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionstart---start-sessii/
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify(error='Error in request parameters'), 400
    if 'web_ip' not in request_data or 'web_agent' not in request_data:
        return jsonify(error='Error in request parameters'), 400
    web_ip = request_data.get('web_ip')
    web_agent = request_data.get('web_agent')
    if not web_ip or not web_agent:
        return jsonify(error='Error in request parameters'), 400
    id_session = str(uuid.uuid4())
    session_controller.session_start(id_session, web_ip, web_agent)
    return jsonify(id_session=id_session)


@app.route("/session/mobile/connect", methods=['POST'])
def session_mobile_connect():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/vapv/
    """
    request_data = request.get_json()
    if not request_data:
        return jsonify(error='Error in request parameters'), 400
    if any(param not in request_data for param in ('mobile_ip', 'mobile_agent', 'id_session')):
        return jsonify(error='Error in request parameters'), 400
    mobile_ip = request_data.get('mobile_ip')
    mobile_agent = request_data.get('mobile_agent')
    id_session = request_data.get('id_session')
    infinity = request_data.get('infinity')
    if not mobile_ip or not mobile_agent or not id_session:
        return jsonify(error='Error in request parameters'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Session with such ID does not exist'), 400
    session_controller.session_mobile_connect(id_session, mobile_ip, mobile_agent)
    session_controller.update_time_end(id_session, infinity)
    session = session_controller.get_session_info(id_session)
    return jsonify(
        time_start=str(session.get('time_start')),
        time_end=str(session.get('time_end')),
        web_ip=session.get('web_ip'),
        web_agent=session.get('web_agent')
    )


@app.route("/data/send", methods=['POST'])
def send_data():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/datasend/
    """
    if 'file' not in request.files:
        return jsonify(error='File missing or error getting file'), 400
    file = request.files.get('file')
    id_session = request.args.get('id_session', '')
    type_file = request.args.get('type', '')
    source = request.args.get('source', '')
    if not id_session or not type_file or not source:
        return jsonify(error='Error in request parameters'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Session with such ID does not exist'), 400
    if type_file not in config.TYPE_FILES:
        return jsonify(error='Invalid file type'), 400
    if source not in config.SOURCE_FILES:
        return jsonify(error='Invalid file source type'), 400
    file_name_real = file.filename
    file_name_fs = ''.join((id_session[:5], str(uuid.uuid4()), os.path.splitext(file_name_real)[1]))
    data_controller.send_data_db(id_session, type_file, file_name_real, file_name_fs, source)
    data_controller.send_data_fs(file_name_fs, file)
    clients = session_controller.get_sid(id_session)
    clients_files = [(file_info.get('id'), file_info.get('file_name_real'))
                     for file_info in data_controller.get_user_files_info(id_session)]
    socketio.emit('available_files', clients_files, room=clients)
    return '', 200


@app.route("/data/get", methods=['GET'])
def get_data():
    id_session = request.args.get('id_session', '')
    id_file = request.args.get('id_file', '')
    if not id_session or not id_file:
        return jsonify(error='Error in request parameters'), 400
    if session_controller.check_free_id(id_session):
        return jsonify(error='Session with such ID does not exist'), 400
    file_info = data_controller.get_file_info(id_file, id_session)
    if not file_info:
        return jsonify(error='File not found'), 400
    return send_file(os.path.join(config.UPLOAD_FOLDER, file_info.get('file_name_fs')),
                     download_name=file_info.get('file_name_real'))


@app.route("/session/keep_alive", methods=['POST'])
def keep_alive():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionkeep-alive/
    """
    request_data = request.get_json()
    if not request_data or 'id_session' not in request_data:
        return jsonify(error='Error in request parameters'), 400
    id_session = request_data.get('id_session')
    if not id_session:
        return jsonify(error='Error in request parameters'), 400
    if not session_controller.session_is_alive(id_session):
        return jsonify(error='Session with such ID does not exist'), 400
    session_controller.keep_alive(id_session)
    return '', 200


@app.route("/session/close", methods=['POST'])
def session_close():
    """
    https://wiki.yandex.ru/homepage/moduli/rest-api/sessionclose---zakrytie-sessii-po-zhelaniju-klient/
    """
    request_data = request.get_json()
    if not request_data or 'id_session' not in request_data:
        return jsonify(error='Error in request parameters'), 400
    id_session = request_data.get('id_session')
    if session_controller.check_free_id(id_session):
        return jsonify(error='Session with such ID does not exist'), 400
    session_controller.session_close(id_session)
    return '', 200


if __name__ == "__main__":
    # trash_collector.start()
    socketio.run(app)
