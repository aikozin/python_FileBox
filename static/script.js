$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');
    socket.on('connect', function() {
        const data = {id_session: '5f3fbc92-5149-400c-a97c-526da2380a67', type: 'web'};
        socket.emit('new_client', data);
    });
    socket.on('available_files', function(msg) {
        console.log(msg);
    });
});