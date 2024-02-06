<template>
    <div class="wrap-dialog iframe-modal " style="overflow: auto;" :class="{ 'full-height': dialogRef.data.fullheight }">
        <div class="p-3 " >
            <div class="grid mb-3 ">
                <div class="col flex gap-2">
                  
                    <div v-if="show_letter_head">
                        <ComLetterHead v-model="letter_head" @onSelect="onSelectLetterHead" />
                    </div>
                    <div v-if="hasFilter('keyword')">
                        <InputText type="text" class="p-inputtext-sm w-full w-16rem"
                            @input="reloadIframe" placeholder="Keyword" v-model="filters.keyword" :maxlength="50" />
                    </div>
                    <div v-if="hasFilter('start_date')">
                        <Calendar :selectOtherMonths="true" panelClass="no-btn-clear" 
                            class="p-inputtext-sm w-full w-12rem" v-model="filters.start_date" placeholder="Start Date"
                            @date-select="loadIframe" showButtonBar dateFormat="dd-mm-yy" showIcon/>
                    </div>
                    <div v-if="hasFilter('end_date')">
                        <Calendar :selectOtherMonths="true" :min-date="filters.start_date"
                            class="p-inputtext-sm w-full w-12rem" v-model="filters.end_date" placeholder="End Date"
                            @date-select="loadIframe" panelClass="no-btn-clear" showButtonBar dateFormat="dd-mm-yy"
                            showIcon />
                    </div>
                    <!-- invoice style for print invoice document credsit debit styoe or simple style -->
                    <div v-if="hasFilter('invoice_style')">
                        <ComSelect v-model="filters.invoice_style" @onSelected="reloadIframe" :clear="false" placeholder="Invoice Style"
                            :options="['Simple Style','Debit/Credit Style']">
                        </ComSelect>
                    </div>
                    <div v-if="hasFilter('business_source')" class="w-16rem">
                        <ComAutoComplete v-model="filters.business_source" placeholder="Business Source"
                            @onSelected="reloadIframe" doctype="Business Source" class="auto__Com_Cus w-full" />
                    </div>
                    <div v-if="hasFilter('city_ledger_type')" class="w-16rem">
                        <ComAutoComplete v-model="filters.city_ledger_type" placeholder="City Ledger Type"
                            @onSelected="reloadIframe" doctype="City Ledger Type" class="auto__Com_Cus w-full" />
                    </div>
                    <div v-if="hasFilter('building')">
                        <ComSelect v-model="filters.building" @onSelected="reloadIframe" placeholder="Building"
                            doctype="Building" :filters="[['property', '=', property_name]]">
                        </ComSelect>
                    </div>
                    <div v-if="hasFilter('floor')">
                        <ComSelect v-model="filters.floor" @onSelected="reloadIframe" placeholder="Floor" doctype="Floor">
                        </ComSelect>
                    </div>
                    <div v-if="hasFilter('room_type_group')">
                        <ComSelect v-model="filters.room_type_group" @onSelected="reloadIframe"
                            placeholder="Room Type Group" doctype="Room Type Group"></ComSelect>
                    </div>
                    <div v-if="hasFilter('room_type')">
                        <ComSelect v-model="filters.room_type" extraFields="room_type" optionLabel="room_type"
                            optionValue="room_type" @onSelected="reloadIframe" placeholder="Room Type" doctype="Room Type"
                            :filters="[['property', '=', property_name]]"></ComSelect>
                    </div>
                    <div v-if="hasFilter('reservation_status')">
                        <ComSelect v-model="filters.reservation_status" placeholder="Reservation Status"
                            @onSelected="reloadIframe" doctype="Reservation Status" />
                    </div>
                    <div v-if="hasFilter('housekeeping_status')">
                        <ComSelect v-model="filters.housekeeping_status" placeholder="Housekeeping Status"
                            @onSelected="reloadIframe" doctype="Housekeeping Status" />
                    </div>
                    <div v-if="hasFilter('transportation_mode')">
                        <ComSelect v-model="filters.transportation_mode" placeholder="Transportation Mode"
                            @onSelected="reloadIframe" doctype="Transportation Mode" />
                    </div>
                    <div v-if="hasFilter('transportation_company')">
                        <ComSelect v-model="filters.transportation_mode" placeholder="Pickup Location"
                            @onSelected="reloadIframe" doctype="Transportation Company" />
                    </div>
                    <div v-if="hasFilter('customer')"> 
                        <ComAutoComplete v-model="filters.customer" placeholder="Customer"
                            @onSelected="reloadIframe" doctype="Customer" class="auto__Com_Cus w-full min-w-max" />
                    </div>
                    <div v-if="hasFilter('guest')"> 
                        <ComAutoComplete v-model="filters.guest" placeholder="Guest"
                            @onSelected="reloadIframe" doctype="Customer" class="auto__Com_Cus w-full min-w-max" />
                    </div>
                    <div v-if="hasFilter('reservation')">
                        <ComAutoComplete v-model="filters.reservation" placeholder="Reservation"
                            @onSelected="reloadIframe" doctype="Reservation" class="auto__Com_Cus w-full min-w-max" />
                    </div>
                    <div v-if="hasFilter('reservation_stay')"> 
                        <ComAutoComplete v-model="filters.reservation_stay" placeholder="Reservation Stay"
                            @onSelected="reloadIframe" doctype="Reservation Stay" class="auto__Com_Cus w-full min-w-max" />
                    </div>
                    <div v-if="hasFilter('show_room_number')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.show_room_number" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_room_number" />
                        </div>
                        <div>
                            <label for="show_room_number" >Show/Hide Room Number</label>
                        </div>
                    </div>
                    
                    <div v-if="hasFilter('show_account_code')" class="flex ml-2">
                        <div>
                        <Checkbox v-model="filters.show_account_code" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_account_code" />
                        </div>
                        <div>
                        <label for="show_account_code" >Show/Hide Account Code</label>
                        </div>
                    </div>

                    <div v-if="hasFilter('show_summary')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.show_summary" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_summary" />
                        </div>
                        <div>
                            <label for="show_summary" >Show/Hide Summary</label>
                        </div>
                    </div>
                    
                    <div v-if="hasFilter('group_by_ledger_type')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.group_by_ledger_type" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_summary" />
                        </div>
                        <div>
                            <label for="group_by_ledger_type" >Group by Ledger Type</label>
                        </div>
                    </div>
                    
                    <div v-if="hasFilter('show_cash_float')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.show_cash_float" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_summary" />
                        </div>
                        <div>
                            <label for="show_cash_float" >Show/Hide Cash Float</label>
                        </div>
                    </div>
                   
                    <div v-if="hasFilter('show_cash_count')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.show_cash_count" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_summary" />
                        </div>
                        <div>
                            <label for="show_cash_count" >Show/Hide Cash Count</label>
                        </div>
                    </div>

                    <div v-if="hasFilter('is_master')" class="flex ml-2">
                        <div>
                            <Checkbox v-model="filters.is_master" :binary="true" :trueValue="1" :falseValue="0" @input="reloadIframe" inputId="show_master_folio_only" />
                        </div>
                        <div>
                            <label for="show_master_folio_only" >Show Master Folio Only</label>
                        </div>
                    </div>

                </div>
                <div class="col flex gap-2 justify-end">
                    <div v-if="(view || '') != 'ui'">
                        <ComPrintButton :BtnClassPrinter="dialogRef.data.BtnClassPrinter ? dialogRef.data.BtnClassPrinter : ''" :url="url" @click="onPrint" />
                    </div>
                    <div>
                        <Button @click="loadIframe" icon="pi pi-refresh"
                            :class="BtnClass ? BtnClass:''" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
            </div>
            <div class="widht-ifame">
                <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="true">
      
           </ComPlaceholder>
                <iframe :class="dialogRef?.data?.iframe_class" :style="loading ? 'visibility: hidden;':''"  @load="onIframeLoaded()" style="min-height:30vh;padding-bottom:30px;" :id="iframe_id" width="100%" :src="url"></iframe>
            </div>
           

        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, inject, onUnmounted } from "@/plugin"
const dialogRef = inject("dialogRef");
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const url = ref("")
const show_letter_head = ref(false)
const letter_head = ref("");
const iframe_id = "iframe_" + Math.random().toString().replace(".", "_")
const moment = inject("$moment")
const filters = ref({
    invoice_style: window.setting.folio_transaction_style_credit_debit ==1?"Debit/Credit Style":"Simple Style",
    show_room_number:1,
    start_date: moment().toDate(),
    end_date: moment().toDate(),
    show_account_code:window.setting.show_account_code_in_folio_transaction,
    show_cash_count:1,
    show_cash_float:1,
    show_master_folio_only:1
    
})
const show_toolbar = ref(0)
const view = ref("")
const extra_params = ref([])
const filter_options = ref([]) // list array string like ["keyword","business_source","room_type"]
const gv = inject("$gv")
const property_name = ref(window.property_name)
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const props = defineProps({
    BtnClassPrinter: String,
    BtnClass: String,
})
const loading = ref(false)
function onSelectLetterHead(l) {
    letter_head.value = l
    loadIframe()
}
const hasFilter = ref((f) => {
    if (filter_options.value) {
        return filter_options.value.includes(f.trim())
    }
    return false

});
function onIframeLoaded() {
    
    const iframe = document.getElementById(iframe_id);
    var contentWidth = iframe.contentWindow.document.body.scrollWidth;
    var windowWidth = window.innerWidth;
    if (iframe.contentWindow.document.body.scrollWidth < iframe.offsetWidth) {
        iframe.style.overflowX = 'hidden';
    } else {
        iframe.style.overflowX = 'auto';
    }
    iframe.style.minWidth = "0px"
    iframe.style.minWidth = iframe.contentWindow.document.body.scrollWidth + 'px';
loading.value = true;
    iframe.style.height = '0px';
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    iframe.onload = function() {
        loading.value = false;
    }


}
const loadIframe = () => {
    loading.value = true;
    if (view.value) {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=No Letterhead&show_toolbar=0&view=ui"

    } else {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + dialogRef.value.data.name + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=" + letter_head.value + "&show_toolbar=0"
    }
    if (extra_params.value) {
        extra_params.value.forEach(p => {
            url.value = url.value + "&" + p.key + "=" + p.value
        });
    }
    let start_date = moment().add(-50, "years").format("YYYY-MM-DD")
    let end_date = moment().add(50, "years").format("YYYY-MM-DD") 
    if (Object.keys(filters.value)) { 
        Object.keys(filters.value).forEach(p => {
            if (filters.value[p]) {
                if (p == "start_date") {
                    start_date = moment(filters.value[p]).format("YYYY-MM-DD")
                } else if (p == "end_date") {
                    end_date = moment(filters.value[p]).format("YYYY-MM-DD")
                } else {
                    url.value = url.value + "&" + p + "=" + filters.value[p]
                } 
            } 
        });
    } 

    if (moment(filters.value.start_date).isSame(moment(filters.value.end_date).format("yyyy-MM-DD")) || moment(filters.value.start_date).isAfter(filters.value.end_date)) {
        filters.value.end_date = moment(filters.value.start_date).add(0, 'days').toDate();
    }
    url.value = url.value + "&start_date=" + moment(filters.value.start_date).format("yyyy-MM-DD") + "&end_date=" + moment(filters.value.end_date).format("yyyy-MM-DD")
    url.value = url.value + "&refresh=" + (Math.random() * 16)
    if (extra_params.value?.filter(r => r.key == 'date').length == 0) {

        url.value = url.value + "&date=" + window.current_working_date
    }
    document.getElementById(iframe_id).contentWindow.location.replace(url.value)  
}
function onPrint() {
    document.getElementById(iframe_id).contentWindow.print()
}
const reloadIframe = debouncer(() => {
    loadIframe()
}, 500);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ComIframeModal"){
            setTimeout(()=>{
                loadIframe()
            },1000)
            
        }
    };
}

onMounted(() => { 
    window.addEventListener('message', actionRefreshData, false); 
    show_toolbar.value = dialogRef.value.data.show_toolbar || 1
  
    show_letter_head.value = dialogRef.value.data.show_letter_head ==undefined?true:dialogRef.value.data.show_letter_head 
    view.value = dialogRef.value.data.view
    if (dialogRef.value.data.view=="ui"){
        show_letter_head.value = false
    }
    extra_params.value = dialogRef.value.data.extra_params 
    filter_options.value = dialogRef.value.data.filter_options
    
    loadIframe()
});

onUnmounted(() => { 
    loading.value = false;
    window.removeEventListener('message', actionRefreshData, false);
})

</script> 
<style scoped>
.full-height {
    height: 85vh;
}
</style>