<template>
    <ComDialogContent @onOK="onUpload" @onClose="onClose" :loading="loading">
        <div>
            <div class="grid w-full m-0">
                <div class="col-5 h-full">
                    <div class="border-round-md overflow-hidden">
                        <div class="border-round-md overflow-hidden border-1">
                            <video id="video" width="640" style="height:480px" autoplay></video>
                        </div>
                    </div>
                </div>
                <div class="col-2 flex justify-content-center align-items-center">
                    <div>
                        <Button class="w-max bg-transparent border-circle p-3" icon="pi pi-camera" @click="onCaptureImage">
                            <ComIcon icon="iconCamera" class="" height="40px" />
                        </Button>
                    </div>
                </div>
                <div class="col-5">
                    <div class="border-round-md overflow-hidden border-1">
                        <canvas id="canvas" width="640" height="480"></canvas>
                    </div>
                    <div class="mt-3">
                        <InputText type="text" class="p-inputtext-sm w-full mb-2" placeholder="title"  v-model="myFile.title" :maxlength="50" />
                        <Textarea v-model="myFile.description" rows="3"  placeholder="Description" class="w-full"/>
                    </div>
                </div>
            </div>
        </div>



    </ComDialogContent>
</template>
<script setup>
import { onMounted, inject, ref, uploadFiles, useToast, onUnmounted } from '@/plugin';
import { FrappeApp } from 'frappe-js-sdk';
const frappe = new FrappeApp()
const dialogRef = inject("dialogRef");
const data = ref({})
const myFile = ref({})
const loading = ref(false)
const toast = useToast()

let streams;
function initializeWebcam() {
    const video = document.getElementById("video");
    const canvas = document.getElementById("canvas");
    const captureButton = document.getElementById("capture");

    navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
            video.srcObject = stream;
            streams = stream;
        })
        .catch((error) => {
            console.error(error);
        });
}
function onCaptureImage() {
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    const blob = dataURLtoBlob(canvas.toDataURL('image/jpeg'));
    myFile.value = new File([blob], 'image.png', { type: 'image/jpeg' });
    myFile.value.title = "Image Title" 
} 
function dataURLtoBlob(dataurl) {
    // Split the data URL into parts
    var parts = dataurl.split(',');
    // Get the MIME type and the base64 data
    var mime = parts[0].match(/:(.*?);/)[1];
    var data = parts[1];
    // Decode the base64 data
    var binData = atob(data);
    // Create an array buffer to store the binary data
    var buffer = new ArrayBuffer(binData.length);
    // Create a view of the buffer
    var view = new Uint8Array(buffer);
    // Copy the binary data to the buffer
    for (var i = 0; i < binData.length; i++) {
        view[i] = binData.charCodeAt(i);
    }
    // Create a blob from the buffer and the MIME type
    var blob = new Blob([buffer], { type: mime });
    // Return the blob
    return blob;
}



onMounted(() => {
    initializeWebcam()

    data.value = dialogRef.value.data



})


const onUpload = () => {
    
    if(!myFile.value?.name){
        toast.add({ severity: 'warn', summary: "Please take photo", life: 3000 })
        return
    } 

    loading.value = true
    uploadFiles([myFile.value], {
        "folder": "Home",
        "doctype": data.value.doctype,
        "docname": data.value.docname,
    }).then(() => {
        loading.value = false
        stopWebcam(); // Stop the webcam stream
        window.postMessage({ "action": "refresh_document_count" }, "*")
        window.postMessage({ "action": "refresh_document" }, "*")
        dialogRef.value.close();
        
    }).catch(error => {
        loading.value = false
    })

    
}

const onClose = () => {
    dialogRef.value.close();
}

function stopWebcam() {
  if (streams) {
    const tracks = streams.getTracks();
    tracks.forEach((track) => {
      track.stop(); // Stop each track in the stream
    });
  }
}

onUnmounted(() => {
    stopWebcam();
})
</script>
<style scoped>
img,
video {
    max-width: unset !important;
}
</style>