const https = require('https');
const WebSocket = require('ws');
const fs = require('fs');

const wss = new WebSocket.Server({
  port: 3001,
  secure: true,
  // The path to the SSL certificate file.
  cert: fs.readFileSync('/etc/letsencrypt/live/example.com/fullchain.pem'),
  // The path to the SSL private key file.
  key: fs.readFileSync('/etc/letsencrypt/live/example.com/privkey.pem')
});

wss.on('connection', function connection(ws) {
  ws.on('message', function incoming(message) {
    console.log('received: %s', message);

    ws.send('I got message from client and send it back');
    
  });
 
  ws.send('Hello from server!');
})