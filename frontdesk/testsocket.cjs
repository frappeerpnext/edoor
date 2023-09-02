const fs = require('fs');
const http = require('http');
const https = require('https');
const socketio = require('socket.io');
const express = require('express');

const options = {
  key: fs.readFileSync('privkey.pem'),
  cert: fs.readFileSync('fullchain.pem')
};

const app = express();
const httpServer = http.createServer(app);
const httpsServer = https.createServer(options, app);

const io = socketio(httpsServer);

io.on('connection', (socket) => {
  socket.on("hello",(arg)=>{
    console.log("hello from client")
  })
});

httpsServer.listen(3000, () => {
  console.log('HTTPS Server started on port 3000');
});