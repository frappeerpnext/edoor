

import io from 'socket.io-client';
import { websocket_port } from "../../../../../sites/common_site_config.json"

let host = window.location.hostname;
let port = ":" +  websocket_port;//window.location.port ? ':9004' : '';
 
let protocol = window.location.protocol;
 
//let url = `${protocol}//${host}${port}`;
let url = `${protocol}//${host}`;
 

const socket = io("http://192.168.10.19:9000", { withCredentials: true });
 

//let socket = io("http://192.168.10.19:9000");

 
export default socket;


