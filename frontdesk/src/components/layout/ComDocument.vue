<template>
    <div>
        <div class="mt-3 min-h-folio-cus" :class="{'unset-min-h' : fill}">
        <div class="flex justify-end mb-3">
            <Button class="conten-btn" label="Upload" icon="pi pi-upload" @click="onModal"></Button>
        </div>
        <div>
            <ComPlaceholder text="No Documents" :loading="loading" :isNotEmpty="data.length > 0">
                <template #default>
                    
                <div class="wrap-file-list">
                    <DataTable :value="data">
                        <Column field="file_url" header="File">
                            <template #body="slotProps"> 
                                <ComAvatar :isDisplayImage="true" size="xlarge" :image="slotProps.data.file_url" :fileName="slotProps.data.file_name" />
                            </template>
                        </Column>
                        <Column field="title" header="Title"></Column>
                        <Column field="attached_to_name" header="Attach Name">
                            <template #body="slotProps"> 
                                <Button v-if="doctype != slotProps.data.attached_to_doctype" @click="onDetail(slotProps.data)" :label="slotProps.data.attached_to_name" link size="small"/>
                            </template>
                        </Column>
                        <Column field="description" header="Description"></Column>
                        <Column field="" header="">
                            <template #body="slotProps">
                                <ComDocumentButtonAction :data="slotProps.data" @onDownload="onDownload" @onEdit="onEdit" @onDelete="onRemove"/>
                                <!-- <Button @click="downloadURI(slotProps.data.file_url, slotProps.data.file_name)" text size="small" icon="pi pi-download" severity="success" /> 
                                <Button :loading="loading" text size="small" icon="pi pi-file-edit" @click="onEdit($event,slotProps.data)" severity="primary" />
                                <Button :loading="deleting" text size="small" icon="pi pi-trash" @click="onRemove(slotProps.data.name)" severity="danger" /> -->
                            </template>
                        </Column>
                    </DataTable>
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
import {deleteDoc, getDocList,updateDoc, ref,onMounted, useConfirm, inject,useDialog,onUnmounted} from '@/plugin'
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComDocumentButtonAction from './components/ComDocumentButtonAction.vue';
const emit = defineEmits(['Documents_length'])
const props = defineProps({
    doctype:{
        type: String,
        require: true
    },
    docname: {
        type: String,
        required: true
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
    }
})
const property = JSON.parse(localStorage.getItem("edoor_property"))
const visible = ref(false)
const loading = ref(false)
const deleting = ref(false)
const saving = ref(false)
const data = ref([])
const opEdit = ref()
const selected =ref({})
const dialogConfirm = useConfirm();
const dialog = useDialog();
const dialogRef = inject("dialogRef");
function onModal(open){
    visible.value = open
}
function onSuccess(){
    visible.value = false
    window.socket.emit("RefreshData", { property: property.name, action: "refresh_document" })
}

window.socket.on("RefreshData", (arg) => {
    if (arg.property == property.name && arg.action=="refresh_document" ) {
        onLoad()
    }
})
function onLoad(){
    loading.value = true
    let dataFilter = []
    if(props.extraFilters.length > 0){
        props.extraFilters.forEach((r)=>{
            dataFilter.push(['attached_to_name','=',r[props.extraFilterFieldName]])
        })
    }
    dataFilter.push(['attached_to_name','=',props.docname])
    getDocList('File', {
        fields: ['name', 'title','description','file_size','file_url','file_name','attached_to_name','attached_to_doctype','owner',"creation"],
        orFilters: dataFilter,
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
    if(data.attached_to_doctype == 'Reservation Stay'){
        showReservationStayDetail(data.attached_to_name)
    }
 
}
function showReservationStayDetail(name) {

const dialogRef = dialog.open(ReservationStayDetail, {
    data: {
        name: name
    },
    props: {
        header: 'Reservation Stay Detail',
        contentClass: 'ex-pedd',
        style: {
            width: '80vw',
        },
        maximizable: true,
        modal: true,
        closeOnEscape: false,
        position: 'top'
    },
    onClose: (options) => {
        const data = options.data;
    }
});
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
                    window.socket.emit("RefreshData", { property: property.name, action: "refresh_document" })
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
        window.socket.emit("RefreshData", { property: property.name, action: "refresh_document" })
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
   onLoad() 
})
// onUnmounted(() => {
//     window.socket.off("RefreshData");
// })
</script>
<style lang="">
    
</style>