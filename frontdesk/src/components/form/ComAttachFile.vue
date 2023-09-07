<template>
    <div>
        <FileUpload name="demo[]" @clear="onClear" @upload="onTemplatedUpload($event)" :multiple="true" accept="image/*,.pdf,.doc,.docx,.xlsx,.xls" :maxFileSize="1000000000" @select="onSelectedFiles">
            <template #header="{ chooseCallback, uploadCallback, clearCallback, files }">
                <div class="flex flex-wrap justify-content-between align-items-center flex-1 gap-2">
                    <div class="flex gap-2">
                        <Button @click="chooseCallback()" icon="pi pi-images" rounded outlined></Button>
                        <Button @click="clearCallback()" icon="pi pi-times" rounded outlined severity="danger" :disabled="!files || files.length === 0"></Button>
                    </div> 
                </div>
            </template>
            <template #content="{ files, uploadedFiles, removeUploadedFileCallback, removeFileCallback }">
                <div v-if="files.length > 0"> 
                    <div class="flex flex-wrap p-0 gap-5">
                        <div v-for="(file, index) of files" :key="file.name + file.type + file.size" class="card m-0 p-3 rounded-md flex flex-column border-1 surface-border gap-3">
                            <div class="flex"> 
                                <ComAvatar size="xlarge" :image="file.objectURL" :fileName="file.name" align="justify-start">
                                    <div class="text-sm">
                                        <div class="font-bold">{{ file.name }} </div>
                                        <span class="text-red-600">({{ formatSize(file.size) }})</span>
                                    </div>
                                </ComAvatar> 
                                <Button text size="small" icon="pi pi-trash" @click="onRemoveTemplatingFile(file, removeFileCallback, index)" severity="danger" />
                            </div>
                            <!-- <div>
                                <InputText type="text" class="p-inputtext-sm w-full mb-2" placeholder="title"  v-model="file.title" :maxlength="50" />
                                <Textarea v-model="file.description" rows="3"  placeholder="Description" class="w-full"/>
                            </div> -->
                        </div>
                    </div> 
                    </div>
            </template>
            <template #empty>
                <div class="flex align-items-center justify-content-center flex-column">
                    <i class="pi pi-cloud-upload border-2 border-circle p-5 text-8xl text-400 border-400" />
                    <p class="mt-4 mb-0">Drag and drop files to here to upload.</p>
                </div>
            </template>
        </FileUpload>
        <div class="border-t border-gray-200 py-2">
            <div>
                <div class="flex justify-end items-center">
                    <div class="flex gap-2">
                        <Button class="border-none" @click="onUpload()" :label="titleButtonOK" :loading="loading">
                            <img class="mr-2" style="height: 14px;"  :src="BtnOkIcon"/> Save
                        </Button>
                        <Button class="border-none bg-og-edoor" @click="onClose()" :label="titleButtonClose" :disabled="loading" >
                            <img class="btn-si__icon mr-2" :src="BtnCloseIcon"/> Close
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, inject, uploadFiles } from "@/plugin";
import BtnCloseIcon from '@/assets/svg/icon-close.svg' 
import BtnOkIcon from '@/assets/svg/icon-save.svg' 
import FileUpload from 'primevue/fileupload';
const emit = defineEmits(['onSuccess','onClose'])
const dialogRef = inject("dialogRef");
const gv = inject('$gv')
const files = ref()
const loading = ref(false)
const props = defineProps({
    modelValue: String,
    isMultiple: {
        type: Boolean,
        default: false
    },
    doctype: {
        type: String,
        default: ''
    },
    folder: {
        type: String,
        default: 'Home'
    },
    isPrivate: {
        type: Boolean,
        default: false
    },
    docname: {
        type: String,
        default: ''
    },
    fieldname: {
        type: String,
        default: ''
    }
})

const onSelectedFiles = (event) => {
    files.value = event.files;
    files.value.forEach((file) => {
        totalSize.value += parseInt(formatSize(file.size));
    });
}; 
function onClear(){
    files.value = []
}
function onClose(){
    emit('onClose')
}
function onUpload(){
    loading.value = true
    const fileArgs = ref({
        /** If the file access is private then set to TRUE (optional) */
        "isPrivate": props.isPrivate,
        /** Folder the file exists in (optional) */
        "folder": props.folder,
        /** File URL (optional) */
        "file_url": "",
        /** Doctype associated with the file (optional) */
        "doctype": props.doctype,
        /** Docname associated with the file (mandatory if doctype is present) */
        "docname": props.docname,
        /** Field in the document **/
        "fieldname": props.fieldname
    })

    if(files.value.length > 0){
        uploadFiles(files.value, fileArgs.value).then(()=>{
            loading.value = false
            emit("onSuccess")
           
        })
    }else{
        loading.value = false
        gv.toast('warn','Please choose files.')
        
    }
    
}
const totalSize = ref(0);
const totalSizePercent = ref(0);

const onRemoveTemplatingFile = (file, removeFileCallback, index) => {
    removeFileCallback(index);
    totalSize.value -= parseInt(formatSize(file.size));
    totalSizePercent.value = totalSize.value / 10;
};

const formatSize = (bytes) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
};
</script>