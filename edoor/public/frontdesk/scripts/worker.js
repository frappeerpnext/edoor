// worker.js
// Receive data from the main thread using onmessage event handler
onmessage = function(event) {
    // The event.data contains the data from the main thread
    const a = event.data.a;
    const b = event.data.b;
 
    const result = a + b;
 
    postMessage(result);
  };