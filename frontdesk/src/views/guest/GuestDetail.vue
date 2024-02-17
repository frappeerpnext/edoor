<template>
    <ComDialogContent hideButtonOK :hideButtonClose="false" @onClose="onClose" :loading="loading">
        
        <div class="iframe-view guest-detail">
            <TabView lazy class="tabview-custom">
                <TabPanel header="General Information">
                    <iframe @load="onIframeLoaded('general')" id="general" style="width: 100%;"
                        :src="generalInfoUrl">
                    </iframe>
                </TabPanel>
                <TabPanel header="Stay History">
                    <iframe @load="onIframeLoaded('stay_history')" id="stay_history" style="width: 100%;"
                        :src="stayHistoryUrl">
                    </iframe>
                </TabPanel>
                <TabPanel header="POS/Misc. Sale">
                    <div style="margin-right:-1rem;">
                    <iframe @load="onIframeLoaded('pos_misc_sale')" id="pos_misc_sale" style="height:500px; width: 100%;"
                        :src="posMiscSaleUrl">
                    </iframe>
                    </div>
                </TabPanel>
                <TabPanel header="Note">
                    <iframe @load="onIframeLoaded('note')" id="note" style="width: 100%;" :src="noteUrl"></iframe>
                </TabPanel>
                <TabPanel header="Folio">
                    <iframe @load="onIframeLoaded('Folio')" id="Folio" style="width: 100%;" :src="folioUrl"></iframe>
                </TabPanel>
                <TabPanel>
                    <template #header>
                        <span class="me-2">Document</span>
                        <ComDocumentBadge :docname="name" :doctypes="['Customer']" :attacheds="[name]" v-if="name"/>
                    </template>
                        <ComDocument doctype="Customer" :docname="name" :fill="false" :attacheds="[name]"/>
                </TabPanel>
            </TabView>
        </div>
        <template #footer-left>
            <Button class="border-none" label="Edit Guest" icon="pi pi-user-edit" @click="onEditGuest"/>
            <Button class="border-none bg-red-500" label="Delete Guest" icon="pi pi-trash" @click="onDeleteGuest(name)"/>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted,computed,useDialog,deleteDoc,useConfirm,onUnmounted } from '@/plugin'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';

const confirm = useConfirm()
const dialogRef = inject("dialogRef");

const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const dialog = useDialog()
const name = ref("")
const loading = ref(false)
const gv = inject("$gv")

function onIframeLoaded(id){ 
    const iframe = document.getElementById(id);
    if (iframe){
        iframe.style.minWidth = "0px"
        iframe.style.minWidth = (iframe.contentWindow.document.body.scrollWidth - 20) + 'px';
        iframe.height = (iframe.contentWindow.document.body.scrollHeight + 53) + 'px';
    }
}


const generalInfoUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format="  + gv.getCustomPrintFormat("eDoor Guest Detail General Information") +  "&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const stayHistoryUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format="  + gv.getCustomPrintFormat("eDoor Guest Stay History") + "&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const posMiscSaleUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=eDoor%20Guest%20POS%2FMisc.%20Sale&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const noteUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format="  + gv.getCustomPrintFormat("eDoor Guest Note") + "&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})
const folioUrl =  computed(() => {
    let url = serverUrl +  "/printview?doctype=Customer&name=" + name.value + "&format=" + gv.getCustomPrintFormat("eDoor Guest Detail Folio List") +" &no_letterhead=1&letterhead=Defualt%20Letter%20Head&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    return url
})

function onEditGuest() { 
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    dialog.open(ComAddGuest, {
        props: {
            header: `Edit Guest`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        data:{
            name: name.value,
        },
    });  
}

function onDeleteGuest (name){
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    confirm.require({
        message: 'Are you sure you want to delete guest?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            deleteDoc('Customer',name)
            .then(() =>{
                loading.value = false 
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"ReservationList"},"*")
                window.postMessage({action:"GuestList"},"*")
                window.postMessage({action:"Reports"},"*")
        	    window.postMessage({action:"FolioTransactionList"},"*")


                dialogRef.value.close()
            }).catch((err)=>{
                loading.value = false
            })         
        },
    });
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="GuestDetail"){
            setTimeout(()=>{
                loadIframe()
            },1000)
            
        }
    };
}
 
onMounted(() => { 
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    if (dialogRef.value) {
        name.value = dialogRef.value.data.name;
    } 
    if (document.querySelectorAll('.guest-detail').length == 1){
        window.addEventListener('message', actionRefreshData, false);
    }
});

const onClose = () => {
    dialogRef.value.close()
}

function loadIframe() {
    if(document.getElementById("general")){
        document.getElementById("general").contentWindow.location.replace(generalInfoUrl.value + "&refresh=" + (Math.random() * 16))
    }
    else if(document.getElementById("stay_history")){
        document.getElementById("stay_history").contentWindow.location.replace(stayHistoryUrl.value + "&refresh=" + (Math.random() * 16))
    }
    else if(document.getElementById("pos_misc_sale")){
        document.getElementById("pos_misc_sale").contentWindow.location.replace(posMiscSaleUrl.value + "&refresh=" + (Math.random() * 16))
    }
    else if(document.getElementById("note")){
        document.getElementById("note").contentWindow.location.replace(noteUrl.value + "&refresh=" + (Math.random() * 16))
    }
    else if(document.getElementById("Folio")){
        document.getElementById("Folio").contentWindow.location.replace(folioUrl.value + "&refresh=" + (Math.random() * 16))
    }   
}

onUnmounted(() => {
    if (document.querySelectorAll('.guest-detail').length - 1 == 0){ 
        window.removeEventListener('message', actionRefreshData, false);
    }
})


</script>
<style scoped>
.iframe-view{
    overflow: auto !important;
    min-height: 550px !important;
    margin-right: -1rem;
    padding-right: 1rem !important;
}
</style>