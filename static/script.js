$(document).ready(function() {
    var socket = io.connect('http://127.0.0.1:5000');
    socket.on('connect', function() {
        const data = {id_session: '34852d9c-9e6b-49ce-9acc-08578ecc9ff5', type: 'web'};
        socket.emit('new_client', data);
    });
    socket.on('available_files', function(msg) {
        console.log(msg);
    });
});