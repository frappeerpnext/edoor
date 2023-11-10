<template>
    <div>
        <div class="mt-3 min-h-folio-cus" :class="{'unset-min-h' : fill}">
        <div class="flex justify-end mb-3">
            <div class="flex gap-2">
                <div>
                    <Button v-if="!onUrl" class="conten-btn" label="Webcam" icon="pi pi-camera" @click="onModalWebcam"></Button>
                </div>
                <div>
                    <Button class="conten-btn" label="Upload" icon="pi pi-upload" @click="onModal"></Button>
                </div>
            </div>
        </div>
        <div>
            <ComPlaceholder text="No Documents" :loading="loading" :isNotEmpty="data.length > 0">
                <template #default>
                    
                <div class="wrap-file-list">
                    <DataTable 
                        :value="data">
                        <Column field="file_url" header="File" headerStyle="width: 25px">
                            <template #body="slotProps"> 
                                <ComAvatar :isDisplayImage="true" size="xlarge" :image="slotProps.data.file_url" :fileName="slotProps.data.file_name" />
                            </template>
                        </Column>
                        <Column field="title" header="Title"></Column>
                        <Column v-if="showAttach" field="attached_to_name" header="Attach Name">
                            <template #body="slotProps"> 
                                <Button v-if="doctype != slotProps.data.attached_to_doctype" @click="onDetail(slotProps.data)" :label="slotProps.data.attached_to_name" link size="small"/>
                            </template>
                        </Column>
                        <Column field="description" header="Description" headerStyle="max-width: 80%">
                            <template #body="slotProps">
                                <div class="break-words whitespace-break-spaces">
                                    {{ slotProps.data.description }}
                                </div>
                            </template>
                        </Column>
                        <Column field="modified" header="Last Modified">
                            <template #body="slotProps">
                                   <ComTimeago :date='slotProps.data.modified' />
                                   
                                
                            </template>
                        </Column>
                        <Column field="" header="">
                            <template #body="slotProps">
                                <ComDocumentButtonAction :data="slotProps.data" @onDownload="onDownload" @onEdit="onEdit" @onDelete="onRemove"/>
                            </template>
                        </Column>
                    </DataTable>
                    <div>
                        <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords"
                            :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
                            <template #start="slotProps">
                                <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                            </template>
                        </Paginator>
                    </div>
                </div>
                </template>
            </ComPlaceholder>
        </div>
        <OverlayPanel ref="opEdit">
            <ComOverlayPanelContent :loading="saving"  @onCancel="onEdit($event,{})" @onSave="onSave">
                <div class="mb-2">
                    <label>Title</label><br />
                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="Title" v-model="selected.title" />
                </div>
                <div>
                    <label>Description</label>
                    <Textarea v-model="selected.description" rows="5" placeholder="Descrpition" cols="30" class="w-full border-round-xl" />
                </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
        <Dialog v-model:visible="visible" modal header="Documents" :style="{ width: '50vw' }">
            <ComDialogContent hideFooter> 
                <ComAttachFile :docname="docname" :doctype="doctype" @onSuccess="onSuccess" @onClose="onModal(false)"/>
            </ComDialogContent>
        </Dialog>
        
         
        </div>
    </div>
</template>
<script setup>
import {deleteDoc, getDocList,updateDoc, ref,onMounted, useConfirm, inject,useDialog,onUnmounted,getCount,useToast} from '@/plugin'

import ComDocumentButtonAction from './components/ComDocumentButtonAction.vue';
import Paginator from 'primevue/paginator';
import ComAttachWebcam from '@/components/form/ComAttachWebcam.vue';

const toast = useToast()

const props = defineProps({
    doctype:{
        type: String,
        require: true
    },
    doctypes:{
        type: Object,
    },

    docname: {
        type: String,
        required: true
    },
    attacheds:{
        type: [String,Array]
    },
    extraFilters: {
        type: Array,
        default: []
    },
    extraFilterFieldName: {
        type: String,
        default: 'name'
    },
    fill: {
        type: Boolean,
        default: true
    },
    showAttach: {
        type: Boolean,
        default: true
    }
})
const property = JSON.parse(localStorage.getItem("edoor_property"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port
const visible = ref(false)
const visibleWebcam = ref(false)
const loading = ref(false)
const deleting = ref(false)
const saving = ref(false)
const data = ref([])
const opEdit = ref()
const selected =ref({})
const dialogConfirm = useConfirm();
const dialog = useDialog();
const onUrl = ref(false)
const pageState = ref({ page: 0, rows: 20, totalRecords: 0, activePage: 0 })
function onModal(open){
    visible.value = open
}

function onModalWebcam(open){
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        const dialogRef = dialog.open(ComAttachWebcam, {
            data: {
                doctype: props.doctype,
                docname: props.docname
            },
            props: {
                header: 'Upload Photo by Webcam',
                style: {
                    width: '80vw',
                },
                breakpoints: {
                    '960px': '100vw',
                    '640px': '100vw'
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: "top"
            }, 
        });
    }
    else{
        toast.add({ severity: 'warn', summary: "Please setup your webcam", life: 3000 })
        return
    }
}


function onSuccess(){
    visible.value = false
    window.postMessage({action:"refresh_document"})
} 

function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows
    onLoad()
}
function getTotalDocument(){
    let dataFilter = []
    let ref_doctypes = [props.doctype]
    ref_doctypes = ref_doctypes.concat(props.doctypes || [])


    dataFilter.push(['attached_to_doctype','in',ref_doctypes])
    dataFilter.push(['attached_to_name','in',props.attacheds])
    dataFilter.push(["custom_show_in_edoor","=",1])
    
    getCount('File', dataFilter, true)
  .then((count) => pageState.value.totalRecords = count)

   
}
function onLoad(showLoading=true){
    loading.value = showLoading
    let dataFilter = []

    let ref_doctypes = [props.doctype]
    ref_doctypes = ref_doctypes.concat(props.doctypes || [])

    dataFilter.push(['attached_to_doctype','in',ref_doctypes])
    dataFilter.push(['attached_to_name','in',props.attacheds])
    dataFilter.push(["custom_show_in_edoor","=",1])
    

    getTotalDocument()
    getDocList('File', {
        fields: ['name', 'title','description','file_size','file_url','file_name','attached_to_name','attached_to_doctype','owner',"creation","modified"],
        filters: dataFilter,
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
        limit: pageState.value?.rows || 20,
        orderBy: {
            field: 'creation',
            order: 'desc',
        }
    }).then((r)=>{
        data.value = r
        loading.value = false
        emit('Documents_length',data.value.length)
    }).catch((err)=>{
        loading.value = false
    })
}

function onDetail(data){
   
        
        window.postMessage("view_" + data.attached_to_doctype.replaceAll(" ","_").toLowerCase() +"_detail|" + data.attached_to_name,"*")
     
 
}

function onDownload(data){
    downloadURI(data.file_url, data.file_name)
}
function onRemove(selected){
    dialogConfirm.require({
        message: 'Do you want to delete this record?',
        header: 'Delete Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleting.value = true
            deleteDoc('File', selected.name).then((doc) => {
                if(doc){
                    deleting.value = false
                    onLoad()
                    window.postMessage({"action":"refresh_document_count", docname:props.docname},"*")
                }
            }).catch((err)=>{
                deleting.value = false
            })
        }
    })
}
function onEdit($event,r){
    selected.value = JSON.parse(JSON.stringify(r))
    opEdit.value.toggle($event)
}
function onSave(){
    saving.value = true
    updateDoc('File',selected.value.name,{
        title: selected.value.title,
        description: selected.value.description
    }).then((r)=>{
        saving.value = false
        opEdit.value.hide()
        onLoad()
        window.socket.emit("FolioTransactionDetail", { property:window.property_name, name: window.folio_transaction_number})
        window.socket.emit("ReservationDetail", window.reservation)
        window.socket.emit("GuestDetail", window.property_name)
        window.socket.emit("ReservationStayDetail", {reservation_stay:window.reservation_stay})
        
    }).catch((err)=>{
        saving.value = false
    })
}
const downloadURI = (uri, name) => {
  const link = document.createElement("a");
  link.download = name;
  link.href = uri;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}
onMounted(() => {
    window.addEventListener('message', actionHandler, false);
    onLoad() 
    onUrl.value = isHTTPS(serverUrl)
})

function isHTTPS(serverUrl) {
  return serverUrl.startsWith("https://");
}

const actionHandler = async function (e) {
       if (e.isTrusted ) {
        if(e.data.action=='refresh_document'){
            onLoad(false)
        }
   }
}
 
onUnmounted(() => {
    window.removeEventListener('message', actionHandler, false);
   
})


</script>
<style lang="">
    
</style>