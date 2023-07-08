<template>
    <div class="relative com_pro__wrap">
        <div class="rounded-full overflow-hidden p-1" style="width: 120px; height: 120px;background-color: var(--bg-card-info);">
            <div class="relative w-full h-full rounded-full border-2 overflow-hidden" style="border-color: var(--bg-btn-color);">
                <div v-if="isClear || (files.length === 0 && !path)">
                    <img :src="profileImage"/>
                </div>
                <div v-else-if="files.length > 0" class="h-full rounded-full border-2 overflow-hidden">
                    <img role="presentation" class="h-full w-full object-cover" :alt="files[0].name" :src="files[0].objectURL" />
                </div>
                <div v-else-if="path" class="h-full rounded-full border-2 overflow-hidden"> 
                    <img role="presentation" class="h-full w-full object-cover" :src="path" />
                </div>
                <div class="z-2 absolute top-0 left-0 bottom-0 right-0 btn-upload-profile">
                    <FileUpload class="bg-transparent" chooseLabel="" mode="basic" name="demo[]" accept="image/*" :auto="true" :maxFileSize="1000000" @select="onSelectedFiles"></FileUpload>  
                </div> 
                <div class="z-1 top-0 transition-duration-500 absolute w-full h-full flex justify-center align-items-center bg-black-alpha-40 icon_-upload-pro">
                    <div class="">
                        <i class="pi pi-camera text-2xl text-white"></i>
                    </div>
                </div>
            </div>
        </div>
        <div v-if="path && !isClear" class="absolute profile__config_c z-3 transition-duration-500" style="right: 2px !important;top: 18px !important;">
            <Button @click="onRemove()" icon="pi pi-times" class="p-0 h-6 border-round-3xl" severity="danger"></Button>
        </div>  
    </div>
</template>

<script setup>
import { ref, inject, updateDoc } from "@/plugin";
import FileUpload from 'primevue/fileupload';
import profileImage from '@/assets/images/avatar-profile.png'


const emit = defineEmits('update:modelValue')
const frappe = inject('$frappe')
const file = frappe.file();
const files = ref([])
const isClear = ref(false)
const props = defineProps({
    modelValue: String,
    isMultiple: {
        type: Boolean,
        default: false
    },
    doctype: {
        type: String,
        default: 'Customer'
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
        default: 'photo'
    },
    path: {
        type: String,
        default: ''
    }
})

const onSelectedFiles = (event) => {
    isClear.value = false
    const fileArgs = {
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
    } 
    files.value = event.files;
    file.uploadFile(
        files.value[0],
        fileArgs
    )
    .then((r) => {
        console.log("File Upload complete",r)
        if(r.data && r.data.message){
            const result = r.data.message
            emit('update:modelValue', result.name)
            onUpdateDoctype( result.file_url)
        }
    })
    .catch(e => console.error(e))
}; 

function onRemove(){
    isClear.value = true
    files.value = []

    emit('update:modelValue', false)
}

function onUpdateDoctype(file_url){
    if(props.docname){
        const dataUpdate = {}
        dataUpdate[props.fieldname] = file_url
        updateDoc(props.doctype, props.docname, dataUpdate).then((r)=>{
            emit('update:modelValue', '')
        })
        
    }else{
        emit('update:modelValue', file_url)
    }
}
</script>
<style>
.btn-upload-profile .p-fileupload,
.btn-upload-profile .p-fileupload-choose {
    height: 100%;
    width: 100%;
    opacity: 0;
}
.btn-upload-profile:hover i {
    display:  block !important;
}
.profile__config_c span{
    font-size: 10px !important;
}
.profile__config_c button{
    width: 1.5rem !important;
}
.profile__config_c, .icon_-upload-pro{
    opacity: 0;
}
.com_pro__wrap:hover .profile__config_c, .com_pro__wrap:hover .icon_-upload-pro{
    opacity: 1;
}
</style>