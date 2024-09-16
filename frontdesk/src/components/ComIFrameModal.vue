<template>
 
    <div class="wrap-dialog iframe-modal " :class="{ 'full-height': dialogRef.data.fullheight }">
        show_sort_order_option:{{print_format?.show_sort_order_option}} | 
        short_order_field{{ sortOrderFields }}
        {{ sortOrderFields }}
        <div class="p-3" :class="(view || '') != 'ui' ? 'grid': ''">
            <div :class="(view || '') != 'ui' ? 'col-4 lg:col-3' : ''">
                <div class="grid mb-3 overflow-auto lg:overflow-hidden flex-nowrap lg:flex-wrap">
                    <div class="col" :class="(view || '') != 'ui' ? 'flex flex-column gap-2' : 'flex gap-2'">
                        <div v-if="show_letter_head">
                            <ComLetterHead :letterhead="letter_head" v-model="letter_head" @onSelect="onSelectLetterHead" />
                        </div>
                        <div v-if="hasFilter('select_user')" class="w-16rem">
                            <ComSelect        class="auto__Com_Cus w-full" 
                            optionLabel="username" optionValue="name"
                            extraFields="username" :clear="false"
                            v-model="filters.select_user" @onSelected="reloadIframe"  placeholder="Select User" doctype="User"></ComSelect>
                        </div>
                        <div v-if="hasFilter('show_vattin')">
                            <div class="relative mt-2">
                                <span class="absolute w-full">
                                    <Checkbox @input="reloadIframe" class="w-full" v-model="filters.show_vattin" :trueValue="1" :falseValue="0"  :binary="true" /></span>
                                <span class="pl-5">Show / Hide Vattin Number</span>
                            </div>        
                        </div>
                        <div v-if="hasFilter('show_business_source')">
                            <div class="relative mt-2">
                                <span class="absolute w-full">
                                    <Checkbox @input="reloadIframe" class="w-full" v-model="filters.show_business_source" :trueValue="1" :falseValue="0"  :binary="true" /></span>
                                <span class="pl-5">Show / Hide Business Source</span>
                            </div>        
                        </div>
                        <div v-if="hasFilter('show_rate_type')">
                            <div class="relative mt-2">
                                <span class="absolute w-full">
                                    <Checkbox @input="reloadIframe" class="w-full" v-model="filters.show_rate_type" :trueValue="1" :falseValue="0"  :binary="true" /></span>
                                <span class="pl-5">Show / Hide Rate Type</span>
                            </div>        
                        </div>
                        <div v-if="hasFilter('keyword')">
                            <InputText type="text" class="p-inputtext-sm w-full w-16rem" @input="reloadIframe"
                                :placeholder="$t('Search')" v-model="filters.keyword" :maxlength="50" />
                        </div>
                        <div v-if="hasFilter('start_date')">
                            <Calendar :selectOtherMonths="true" panelClass="no-btn-clear"
                                class="p-inputtext-sm w-full w-12rem" v-model="filters.start_date" placeholder="Start Date"
                                @date-select="loadIframe" showButtonBar dateFormat="dd-mm-yy" showIcon />
                        </div>
                        <div v-if="hasFilter('end_date')">
                            <Calendar :selectOtherMonths="true" :min-date="filters.start_date"
                                class="p-inputtext-sm w-full w-12rem" v-model="filters.end_date" placeholder="End Date"
                                @date-select="loadIframe" panelClass="no-btn-clear" showButtonBar dateFormat="dd-mm-yy"
                                showIcon />
                        </div>
                      
                        <div v-if="hasFilter('show_rate')">
                            <div>
                                <Checkbox v-model="filters.show_rate" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_rate" />
                            </div>
                            <div>
                                <label class="white-space-nowrap" for="show_rate">Show/Hide Rate</label>
                            </div>
                        </div>
                   
                        <div v-if="hasFilter('show_inactive_reservation')">
                            <div>
                                <Checkbox v-model="filters.show_inactive_reservation" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_inactive_reservation" />
                            </div>
                            <div>
                                <label class="white-space-nowrap" for="show_rate">Show/Hide Rate</label>
                            </div>
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
                            <ComSelect v-model="filters.floor" @onSelected="reloadIframe" placeholder="Floor"
                                doctype="Floor">
                            </ComSelect>
                        </div>
                        <div v-if="hasFilter('room_type_group')">
                            <ComSelect v-model="filters.room_type_group" @onSelected="reloadIframe"
                                placeholder="Room Type Group" doctype="Room Type Group"></ComSelect>
                        </div>
                        <div v-if="hasFilter('room_type')">
                            <ComSelect v-model="filters.room_type" extraFields="room_type" optionLabel="room_type"
                                optionValue="room_type" @onSelected="reloadIframe" placeholder="Room Type"
                                doctype="Room Type" :filters="[['property', '=', property_name]]"></ComSelect>
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
                            <ComAutoComplete v-model="filters.customer" placeholder="Customer" @onSelected="reloadIframe"
                                doctype="Customer" class="auto__Com_Cus w-full min-w-max" />
                        </div>
                        <div v-if="hasFilter('guest')">
                            <ComAutoComplete v-model="filters.guest" placeholder="Guest" @onSelected="reloadIframe"
                                doctype="Customer" class="auto__Com_Cus w-full min-w-max" />
                        </div>
                        <div v-if="hasFilter('reservation')">
                            <ComAutoComplete v-model="filters.reservation" placeholder="Reservation"
                                @onSelected="reloadIframe" doctype="Reservation" class="auto__Com_Cus w-full min-w-max" />
                        </div>
                        <div v-if="hasFilter('reservation_stay')">
                            <ComAutoComplete v-model="filters.reservation_stay" placeholder="Reservation Stay"
                                @onSelected="reloadIframe" doctype="Reservation Stay"
                                class="auto__Com_Cus w-full min-w-max" />
                        </div>
                        <div v-if="hasFilter('account_code')">
                            <ComAutoComplete v-model="filters.account_code" placeholder="Account Code"
                                @onSelected="reloadIframe" doctype="Account Code"
                                class="auto__Com_Cus w-full min-w-max" />
                        </div>
                        <div v-if="hasFilter('show_room_number')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_room_number" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_room_number" />
                            </div>
                            <div>
                                <label class="white-space-nowrap" for="show_room_number">Show/Hide Room Number</label>
                            </div>
                        </div>

                        <div v-if="hasFilter('show_account_code')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_account_code" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_account_code" />
                            </div>
                            <div>
                                <label for="show_account_code" class="white-space-nowrap">Show/Hide Account Code</label>
                            </div>
                        </div>

                        <div v-if="hasFilter('show_summary')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_summary" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_summary" />
                            </div>
                            <div>
                                <label for="show_summary" class="white-space-nowrap">Show/Hide Summary</label>
                            </div>
                        </div>
                        

                        <div v-if="hasFilter('show_all_room_rate')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_all_room_rate" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_all_room_rate" />
                            </div>
                            <div>
                                <label for="show_all_room_rate" class="white-space-nowrap">Show All Room Rate</label>
                            </div>
                        </div>
                        


                        <div v-if="hasFilter('group_by_ledger_type')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.group_by_ledger_type" :binary="true" :trueValue="1"
                                    :falseValue="0" @input="reloadIframe" inputId="group_by_ledger_type" />
                            </div>
                            <div>
                                <label for="group_by_ledger_type">Group by Ledger Type</label>
                            </div>
                        </div>

                        <div v-if="hasFilter('show_cash_float')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_cash_float" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_cash_float" />
                            </div>
                            <div>
                                <label for="show_cash_float">Show/Hide Cash Float</label>
                            </div>
                        </div>
                        
                        <div v-if="hasFilter('show_cash_count')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_cash_count" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_cash_count" />
                            </div>
                            <div>
                                <label for="show_cash_count">Show/Hide Cash Count</label>
                            </div>
                        </div>
                        <div v-if="hasFilter('show_package_breakdown')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.show_package_breakdown" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_package_breakdown" />
                            </div>
                            <div>
                                <label for="show_package_breakdown">Show Package Breakdown</label>
                            </div>
                        </div>

                        <div v-if="hasFilter('is_master')" class="flex ml-2">
                            <div>
                                <Checkbox v-model="filters.is_master" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="reloadIframe" inputId="show_master_folio_only" />
                            </div>
                            <div>
                                <label for="show_master_folio_only">Show Master Folio Only</label>
                            </div>
                        </div>

                        <div v-if="print_format && print_format?.show_sort_order_option " class="flex ml-2">
                           Order By Option
                        </div>

                    </div>
                 
                       
                        <div v-if="(view || '') == 'ui'">
                            <Button @click="loadIframe" icon="pi pi-refresh" :class="BtnClass ? BtnClass : ''"
                                class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                        </div> 
                    
                </div>
            </div>
            <div :class="(view || '') != 'ui' ? 'col' : ''">
                <div class="col flex gap-2 justify-end" v-if="(view || '') != 'ui'">
                    <div v-if="(view || '') != 'ui'">
                        <ComPrintButton
                            :BtnClassPrinter="dialogRef.data.BtnClassPrinter ? dialogRef.data.BtnClassPrinter : ''"
                            :url="url" @click="onPrint" />
                    </div>
                    <div>
                        <Button @click="loadIframe" icon="pi pi-refresh" :class="BtnClass ? BtnClass : ''"
                            class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
                <div class="widht-ifame">
                    <ComPlaceholder text="No Data" :loading="loading" :is-not-empty="true" />
                    <template v-if="!loading">
                        <div v-html="html" class="view_table_style view_srolling_table" v-if="view"></div>
                    </template>


                    <template v-if="!view">

                        <iframe class="iframe_max_height" :style="loading ? 'visibility: hidden;' : ''" @load="onIframeLoaded()"
                            style="min-height:30vh;" :id="iframe_id" width="100%" :src="url"></iframe>

                    </template>


                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, inject, onUnmounted,getDoc } from "@/plugin"
import { computed } from "vue";
const dialogRef = inject("dialogRef");
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;

const url = ref("")
const show_letter_head = ref(false)
const letter_head = ref("");
const iframe_id = "iframe_" + Math.random().toString().replace(".", "_")
const moment = inject("$moment")
const frappe = inject("$frappe")
const call = frappe.call()
const filters = ref({
    invoice_style: window.setting.folio_transaction_style_credit_debit == 1 ? "Debit/Credit Style" : "Simple Style",
    show_room_number: 1,
    start_date: moment().toDate(),
    end_date: moment().toDate(),
    show_account_code: window.setting.show_account_code_in_folio_transaction,
    show_cash_count: 1,
    show_cash_float: 1,
    show_master_folio_only: 1,
    show_vattin:0,
    show_summary:0,
    show_package_breakdown:1,
    show_business_source:0,
    show_rate_type:0

})
const show_toolbar = ref(0)
const view = ref("")
const extra_params = ref([])
const filter_options = ref([]) // list array string like ["keyword","business_source","room_type"]
const gv = inject("$gv")
const property_name = ref(window.property_name)
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const print_format = ref()


const props = defineProps({
    BtnClassPrinter: String,
    BtnClass: String,
})

const sortOrderFields = computed(()=>{
    
    if(print_format.value?.short_order_field==""){
        return []
    }else {
        return print_format.value?.short_order_field
    }
})
const loading = ref(false)

const html = ref()

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

    if (!dialogRef.value.data.view) {

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

        iframe.onload = function () {
            loading.value = false;
        }

    }
}

const param = ref({

})
const loadIframe = () => {

    loading.value = true;
    param.value.doc = decodeURIComponent(dialogRef.value.data.doctype)
    param.value.name = decodeURIComponent(dialogRef.value.data.name)
    param.value.format = decodeURIComponent(dialogRef.value.data.report_name)
    param.value._lang = localStorage.getItem("lang") || "en"
    param.value.letterhead = "No Letterhead"
    param.value.show_toolbar = 0
    param.value.view = "ui"
    param.value.settings = decodeURIComponent("%7B%7D")

    if (view.value) {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + encodeURIComponent(decodeURI( dialogRef.value.data.name)) + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=No Letterhead&show_toolbar=0&view=ui"

    } else {
        url.value = serverUrl + "/printview?doctype=" + dialogRef.value.data.doctype + "&name=" + encodeURIComponent(decodeURI( dialogRef.value.data.name)) + "&format=" + gv.getCustomPrintFormat(decodeURI(dialogRef.value.data.report_name)) + "&&settings=%7B%7D&_lang=en&letterhead=" + letter_head.value + "&show_toolbar=0"
    }
    if (extra_params.value) {
        extra_params.value.forEach(p => {
            url.value = url.value + "&" + p.key + "=" + encodeURIComponent(decodeURI( p.value))
            param.value[p.key] = p.value
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
                    url.value = url.value + "&" + p + "=" + encodeURIComponent(decodeURI( filters.value[p]))
                    param.value[p] = filters.value[p]
                }
            }
        });
    }

    if (moment(filters.value.start_date).isSame(moment(filters.value.end_date).format("yyyy-MM-DD")) || moment(filters.value.start_date).isAfter(filters.value.end_date)) {
        filters.value.end_date = moment(filters.value.start_date).add(0, 'days').toDate();
    }
    url.value = url.value + "&start_date=" + moment(filters.value.start_date).format("yyyy-MM-DD") + "&end_date=" + moment(filters.value.end_date).format("yyyy-MM-DD")
    param.value.start_date = moment(filters.value.start_date).format("yyyy-MM-DD")
    param.value.end_date = moment(filters.value.end_date).format("yyyy-MM-DD")

    url.value = url.value + "&refresh=" + (Math.random() * 16)
    if (extra_params.value?.filter(r => r.key == 'date').length == 0) {

        url.value = url.value + "&date=" + window.current_working_date
        param.value.date = window.current_working_date
    }

    if (view.value) {
        call.get("epos_restaurant_2023.www.printview.get_html_and_style", param.value).then(result => {
            html.value = result.message.html
            loading.value = false
        }).catch(err => {
            loading.value = false
        })
    } else {
 
        document.getElementById(iframe_id).contentWindow.location.replace(url.value)

    }



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
        if (e.data.action == "ComIframeModal") {
            setTimeout(() => {
                loadIframe()
            }, 1000)

        }
    };
}

onMounted(() => {
    
   
    getDoc("Print Format",decodeURIComponent(dialogRef.value.data.report_name)).then((doc)=>{
        print_format.value = doc
    })
    if (window.isMobile) {
        let elem = document.querySelectorAll(".p-dialog");
        if (elem) {
            elem = elem[elem.length - 1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', actionRefreshData, false);
    show_toolbar.value = dialogRef.value.data.show_toolbar || 1

    show_letter_head.value = dialogRef.value.data.show_letter_head == undefined ? true : dialogRef.value.data.show_letter_head
    view.value = dialogRef.value.data.view
    if (dialogRef.value.data.view == "ui") {
        show_letter_head.value = false
    }
    extra_params.value = dialogRef.value.data.extra_params
    filter_options.value = dialogRef.value.data.filter_options

    letter_head.value =  dialogRef.value.data.letterhead || ""

    loadIframe()
});

onUnmounted(() => {
    loading.value = false;
    window.removeEventListener('message', actionRefreshData, false);
})

</script>