// worker.js
// Receive data from the main thread using onmessage event handler
onmessage = function(event) {
    // The event.data contains the data from the main thread
    const a = event.data.a;
    const b = event.data.b;
  
    // Perform some computation with the data
    const result = a + b;
    console.log("from worker")
    
    // Send the result back to the main thread using postMessage method
    postMessage(result);
  };