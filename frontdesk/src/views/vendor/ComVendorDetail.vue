<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" style="max-height: 80vh;">
        <iframe @load="onIframeLoaded()" id="iframeVendorDetail" style="width: 100%;" :src="url">
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
import { ref, inject, useDialog, onMounted,deleteDoc,useConfirm,computed,onUnmounted } from '@/plugin'
import ComAddVendor from '@/views/vendor/ComAddVendor.vue';
const dialogRef = inject("dialogRef")
const gv = inject('$gv');
const dialog = useDialog()
const loading = ref(false)
const confirm = useConfirm()
const name = ref()

const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const url =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Vendor&name="+ name.value +"&format=" + gv.getCustomPrintFormat("eDoor Vendor Detail")  + "&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})

function onIframeLoaded(){ 
    const iframe = document.getElementById("iframeVendorDetail");
    iframe.height = iframe.contentWindow.document.body.scrollHeight;

}

function onEdit() { 
    dialog.open(ComAddVendor, {
        data: {
            name: name.value,
            is_city_ledger: false
        },
        props: {
            header: `Edit Vendor: ${name.value}`,
            style: {
                width: '50vw',
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
        message: 'Are you sure you want to delete vendor?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
             deleteDoc('Vendor',name.value)
                 .then((r) =>{ 
                    dialogRef.value.close(r)
                    window.postMessage({action:"Vendor"},"*")
                 } ).catch((err)=>{
                    loading.value = false
                 })         
        },
    });
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ComVendorDetail"){
            setTimeout(()=>{
                document.getElementById("iframeVendorDetail").contentWindow.location.replace(url.value + "&refresh=" + (Math.random() * 16))
            },1000*10)
            
        }
    };
}

onMounted(() => {
    name.value = dialogRef.value.data.name
    window.addEventListener('message', actionRefreshData, false);
})

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})

</script>