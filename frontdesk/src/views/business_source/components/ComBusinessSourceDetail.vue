<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" style="max-height: 80vh;">
        <iframe @load="onIframeLoaded()" id="iframe" style="width: 100%;" :src="url">
        </iframe>
        <template #footer-right>
            <Button class="border-none" @click="onEdit"> 
                <i class="pi pi-pencil me-2"/> Edit
            </Button>
            <Button class="bg-red-500 border-none" @click="onDelete"> <i class="pi pi-trash me-2" /> Delete</Button>
        </template>
    </ComDialogContent>

</template>
 <script setup>
import { ref, inject, useDialog, onMounted,deleteDoc,useConfirm,computed } from '@/plugin'
import ComAddBusinessSource from './ComAddBusinessSource.vue';
const dialogRef = inject("dialogRef")
const gv = inject('$gv');
const dialog = useDialog()
const loading = ref(false)
const confirm = useConfirm()
const name = ref()
const setting =JSON.parse( localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Business%20Source&name="+ name.value +"&format=" + gv.getCustomPrintFormat("eDoor Business Source Detail")  + "&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})

function onIframeLoaded(){ 
    const iframe = document.getElementById("iframe");
    iframe.height = iframe.contentWindow.document.body.scrollHeight;

}

function onEdit() { 
    dialog.open(ComAddBusinessSource, {
        data: {
            name: name.value
        },
        props: {
            header: `Edit Business Source: ${name.value}`,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                name.value = data
                loading.value = false
            }
        }
    });
}

function onDelete() {
    confirm.require({
        message: 'Are you sure you want to delete business source?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
             deleteDoc('Business Source',name.value)
                 .then((r) =>{ 
                    dialogRef.value.close(r)
                    window.socket.emit("RefreshData", {property:property.name,action:"refresh_business_source"});
                    
                 } ).catch((err)=>{
                    loading.value = false
                 })         
        },
    });
}

onMounted(() => {
    name.value = dialogRef.value.data.name
})

</script>