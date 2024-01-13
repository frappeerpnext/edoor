<template>
    <div class="wrap-dialog iframe-modal" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="p-3 view-table-iframe-dialog" style="height: 85vh;">
            <div class="grid mb-3 ">
                <div class="col flex gap-2">
                    <div>
                        <Dropdown v-model="filters.selected_folio"  :options="dialogRef.data.folios" optionLabel="name" 
                placeholder="Select Folio" class="w-full md:w-14rem" @change="onSelectFolio" />
                    </div>
                    <div>
                        
                        <ComLetterHead v-model="filters.letterHead"  @onSelect="onSelectLetterHead"/>
                        
                    </div>
                    
                    <div>
                        
                        <ComSelect v-model="filters.invoice_style" @onSelected="refreshReport" :clear="false" placeholder="Invoice Style"
                            :options="['Simple Style','Debit/Credit Style']">
                        </ComSelect>
                    
                    </div>
                </div>
                <div class="col flex grap-2">
                    <div>
                        <Checkbox v-model="filters.show_room_number" :binary="true" :trueValue="1" :falseValue="0" @input="refreshReport" inputId="show_room_number" />
                        <label for="show_room_number" >Show/Hide Room Number</label>
                    </div>
                    
                    <div>
                        <Checkbox v-model="filters.show_account_code" :binary="true" :trueValue="1" :falseValue="0" @input="refreshReport" inputId="show_account_code" />
                        <label for="show_account_code" >Show/Hide Account Code</label>
                    </div>

                    <div>
                        <Checkbox v-model="filters.show_summary" :binary="true" :trueValue="1" :falseValue="0" @input="refreshReport" inputId="show_summary" />
                        <label for="show_summary" >Show/Hide Summary</label>
                    </div>
                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view||'')!='ui'">
                        <ComPrintButton :url="url"  @click="onPrint"/>
                    </div>
                    <div >
                        <Button @click="refreshReport" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
            </div> 
            <div class="widht-ifame">
                <iframe @load="onIframeLoaded()" id="report-view" width="100%" style="min-height: 70vh;" :src="url"></iframe>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted, inject , onUnmounted , getApi} from "@/plugin"
const dialogRef = inject("dialogRef");

 
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const url = ref("")
 

const reservation_stay = ref("")
const report_name = ref("")

const filters = ref({
    invoice_style:window.setting.folio_transaction_style_credit_debit ==1?"Debit/Credit Style":"Simple Style",
    letterHead:window.setting.property.default_letter_head ,
    show_account_code:window.setting.show_account_code_in_folio_transaction,
    show_room_number:1
})

function onSelectFolio(f){
    refreshReport()
}

function onSelectLetterHead(l){
    filters.value.letterHead = l
    refreshReport()

}
const refreshReport = () => {
    if(filters.value.selected_folio){

    
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + filters.value.selected_folio.reservation_stay + "&format=" + report_name.value + "&&settings=%7B%7D&_lang=en&letterhead=" + filters.value.letterHead + "&show_toolbar=0&show_room_number=" + filters.value.show_room_number + "&show_account_code=" + filters.value.show_account_code
    url.value = url.value + "&invoice_style=" + filters.value.invoice_style
    url.value = url.value + "&show_summary=" + filters.value.show_summary || 0
    if (filters.value.selected_folio) {
        url.value = url.value + "&folio=" + filters.value.selected_folio.name
    }

    document.getElementById("report-view").contentWindow.location.replace(url.value)
    }
}
function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
}

function onPrint(){

    if (filters.value.selected_folio) {
        document.getElementById("report-view").contentWindow.print()
    }
    
}

onMounted(() => {
    if (dialogRef) {
        const params = dialogRef.value.data
        reservation_stay.value = params.reservation_stay
        report_name.value = params.report_name

        if (!params.folio) {
            filters.value.selected_folio= params.folios[0]
        } else {
            filters.value.selected_folio= params.folio
        }
        refreshReport()

    }



});

</script> 