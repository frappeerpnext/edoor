<template>
    <ComDialogContent   hideButtonOK :hideButtonClose="true" @onClose="onClose" :isDialog="true">
    <iframe @load="onIframeLoaded()" id="iframe" width="100%" :src="url"></iframe>
    <template #footer-left>
        
        <SplitButton  @click="viewFolioSummaryReport" class="spl__btn_cs sp" label="Print" icon="pi pi-print" :model="print_menus" />

    </template>
    <template #footer-right>
        <Button v-if="doc.is_closed == 0" @click="onOpenCloseShift">Close Shift</Button>
    </template>
  </ComDialogContent>
</template>
<script setup>
import { ref, getApi, onMounted, inject, getDoc,useDialog,useToast } from "@/plugin"
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue"
const toast = useToast()
const dialogRef = inject("dialogRef")
const name = ref("")
const url = ref("")
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const doc = ref({})
const dialog = useDialog();
const loading = ref(false)
const print_menus = ref([])

function viewFolioSummaryReport(){
    
    dialog.open(ComPrintReservationStay, {
            data: {
                doctype: "Reservation%20Stay",
                reservation_stay: doc.value.reservation_stay,
                folio_number: name.value,
                report_name: "eDoor%20Reservation%20Stay%20Folio%20Summary%20Report",
                view: "print"
            },
            props: {
                header: "Folio Summary Report",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,

            },
        });
}


//Folio Summary Report
print_menus.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {

        viewFolioSummaryReport()
    }
})

//folio detail report
print_menus.value.push({
    label: "Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComPrintReservationStay, {
            data: {
                doctype: "Reservation%20Stay",
                reservation_stay: doc.value.reservation_stay,
                folio_number: name.value,
                report_name: "eDoor%20Reservation%20Stay%20Folio%20Detail%20Report",
                view: "print"
            },
            props: {
                header: "Folio Summary Report",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true
            },
        });
    }
})



function onIframeLoaded() {
    const iframe = document.getElementById("iframe");
    var contentWidth = iframe.contentWindow.document.body.scrollWidth;
    var windowWidth = window.innerWidth;

    if (windowWidth >= 1920) {
        iframe.style.maxWidth = 100 + '%'
    }
    else {
        iframe.style.width = contentWidth + 'px';
    }
    iframe.height = iframe.contentWindow.document.body.scrollHeight;
}

const refreshReport = () => {
            
    url.value = serverUrl + "/printview?doctype=Cashier%20Shift&name=" + name.value + "&format=eDoor%20Cashier%20Shift%20Detail%20UI&no_letterhead=0&letterhead=No Letterhead&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
    document.getElementById("iframe").contentWindow.location.replace(url.value)

}

function onOpenCloseShift(){
  
    if (doc.value.is_edoor_shift ==0){
        toast.add({ severity: 'warn', summary: "This shift is an ePOS shift. Please ask ePOS user to close their shift.", detail: '', life: 3000 })
    }else {
        window.postMessage('close_shift', '*')
    }
}

onMounted(() => {
    name.value = dialogRef.value.data.name
    getDoc("Cashier Shift", name.value).then((result)=>{
        doc.value = result
    })
    refreshReport()

})

</script>