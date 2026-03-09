const http = require('http');
const socketio = require('socket.io');
 


 
const httpServer = http.createServer();
 
const io = require('socket.io')(httpServer, {
  path: '/socketserver/socket.io',
  cors: {
    origin: '*',
  }
});


io.on('connection', (socket) => {
  socket.on("hello",(arg)=>{
    socket.emit("hello",arg)
  })
});

httpServer.listen(3000, () => {
  console.log('HTTP Server started on port 3000');
});