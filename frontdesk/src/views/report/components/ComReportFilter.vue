<template>
    <div v-if="showFilter" class="p-3">
    <div  class="grid justify-between">
        <div class="grid w-full">
            <div class="col" v-if="hasFilter('filter_date_by')">
                <label>Filters</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.filter_date_by" placeholder="Filter By Date"
                                    :options="['Arrival Date', 'Departure Date', 'Reservation', 'Stay']" :clear="false" />
            </div> 

            <div class="col" v-if="hasFilter('start_date')">
                <label>Start Date</label><br/>
                <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date" dateFormat="dd-mm-yy"
                    showIcon />
            </div>
            <div class="col" v-if="hasFilter('end_date')">
                <label>End date</label><br>
                <Calendar class="w-full" :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date" dateFormat="dd-mm-yy"
                    showIcon />
            </div>
            <div class="col" v-if="hasFilter('select_filter')">
                <label>Select Filter</label><br>
                <ComSelect class="w-full"  v-model="filter.select_filter" placeholder="Select Filter"
                :options="['Reservation','Reservation Stay','Reservation Room Rate','Guest','Reservation Folio','Folio Transaction']" />
            </div>
            <div class="col" v-if="hasFilter('reservation_type')">
                <label>Reservation Type</label><br>
                <ComSelect class="w-full"   v-model="filter.reservation_type" placeholder="Select Reservation Type" :showClear="true"
                :options="['FIT','GIT']" />
            </div>
            <div class="col"  v-if="hasFilter('business_source')">
                <label>Business Source</label><br>
                <ComAutoComplete v-model="filter.business_source" placeholder="Business Source" doctype="Business Source"
                class="auto__Com_Cus w-full" :filters="{ property: property.name }" />
            </div>
            <div class="col"  v-if="hasFilter('reservation_status')">
                <label>Reservation Status</label><br>
                <ComSelect v-model="filter.reservation_status" placeholder="Reservation Status" doctype="Reservation Status"
                class="auto__Com_Cus w-full" :isMultipleSelect="true" maxWidth="30rem" :maxSelectLabel="10" />
            </div>
            <div class="col"  v-if="hasFilter('room_type')">
                <label>Room Type</label><br>
                
                <ComSelect        class="auto__Com_Cus w-full" 
                optionLabel="room_type" optionValue="room_type"
                extraFields="room_type"
                    v-model="filter.room_type"   placeholder="Room Type" doctype="Room Type"
                    :filters="{ property: property.name }" ></ComSelect>
            </div>
            <div class="col"  v-if="hasFilter('room_type_name')">
                <label>Room Type</label><br>
                
                <ComSelect        class="auto__Com_Cus w-full" 
                optionLabel="room_type" optionValue="name"
                extraFields="room_type"
                    v-model="filter.room_type_name"   placeholder="Room Type" doctype="Room Type"
                    :filters="{ property: property.name }" :isMultipleSelect="true"  maxWidth="30rem" :maxSelectLabel="10" ></ComSelect>
            </div>
            <div class="col"  v-if="hasFilter('arrival_modes')">
                <label>Arrival Mode</label><br>
                
                <ComSelect        class="auto__Com_Cus w-full" 
                    v-model="filter.arrival_modes"   placeholder="Arrival Mode" doctype="Transportation Mode"
                    ></ComSelect>
            </div>
            <div class="col"  v-if="hasFilter('departure_mode')">
                <label>Departure Mode</label><br>
                
                <ComSelect        class="auto__Com_Cus w-full" 
                    v-model="filter.departure_mode"   placeholder="Departure Mode" doctype="Transportation Mode"
                    ></ComSelect>
            </div>
        </div>
        <div class="grid w-full">
            <div class="col mt-4"  v-if="hasFilter('is_active_reservation')">
                <div class="h-full" >
                    <div class="py-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                    <div>
                        <label for="filter_is_active" class="font-medium cursor-pointer">Is Active Reservation</label>
                    </div>
                    <div>
                        <Checkbox input-id="filter_is_active" class="mx-3" v-model="filter.is_active_reservation" :binary="true" trueValue="1"
                                falseValue="0" /> 
                    </div>
                    </div>
                </div>   
            </div>
            <div class="col" v-if="hasFilter('guest')">
                <label>Guest</label><br/>
                <ComSelect        class="auto__Com_Cus w-full" 
                optionLabel="customer_name_en" optionValue="name"
                extraFields="customer_name_en"
                    v-model="filter.guest"   placeholder="Guest" doctype="Customer"></ComSelect>
            </div> 
            <div class="col" v-if="hasFilter('select_user')">
                <label>Select User</label><br/>
                <ComSelect        class="auto__Com_Cus w-full" 
                optionLabel="username" optionValue="name"
                extraFields="username"
                    v-model="filter.select_user"   placeholder="Select User" doctype="User"></ComSelect>
            </div> 
            <div class="col" v-if="hasFilter('group_by')">
                <label>Group By</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.group_by" placeholder="Group By"
                    :options="['Arrival Date', 'Departure Date', 'Reservation','Reservation Date','Reservation Type','Guest','Room Type','Business Source','Business Source Type','Nationality','Rate Type','Reservation Status']" 
                     />
            </div> 
            <div class="col" v-if="hasFilter('order_by')">
                <label>Order By</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.order_by" placeholder="Order By"
                    :options="['Last Update On', 'Created On', 'Reservation','Reservation Stay','Arrival Date','Departure Date','Room Type','Reservation Status']" 
                    :default="['Last Update On']" 
                    :clear="false"/>
            </div>
            <div class="col" v-if="hasFilter('audit_order')">
                <label>Order By</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.audit_order" placeholder="Order By"
                    :options="['Last Update On', 'Created On', 'Reference Document','Reference Name','Audit Date','Subject','Description','Created By']" 
                    :clear="false"/>
            </div>
            <div class="col" v-if="hasFilter('sort_order')">
                <label>Sort Order</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.sort_order" placeholder="Sort"
                    :options="['ASC', 'DESC']" 
                    :clear="false" />
            </div> 
            <div class="col" v-if="hasFilter('summary_filter')">
                <label>Summary By</label><br/>
                <ComSelect class="auto__Com_Cus w-full" v-model="filter.summary_filter" placeholder="Summary By"
                    :options="['Arrival Date', 'Departure Date', 'Reservation' , 'Reservation Date','Reservation Type','Guest','Room Type','Business Source','Business Source Type','Nationality','Rate Type','Reservation Status']" 
                    :default="['Business Source']"/>
            </div>
        </div>
        </div>
        <div class="w-full items-center flex justify-end p-3 pb-0">
            <div class="flex justify-end gap-2">
                <Button class= "white-space-nowrap content_btn_b w-3rem justify-center"  @click="customReport" ><i class="pi pi-cog text-xl "/></Button>
                <div class="border-left-1 border-primary-100"></div>
                <Button class= "white-space-nowrap content_btn_b" @click="onSearch"><i class="pi pi-file me-2"/> Preview Report</Button>
            </div>
        </div>
        <OverlayPanel ref="showCustomReport" style="width:50rem">
        <ComOverlayPanelContent title="Advance Custom Report" hideButtonOK="true"  :hideButtonClose="false" @onCancel="onCloseCustomReport">
            <div class="grid">
            <div class="col-6">
                <label>Letter Head</label><br>
                <ComLetterHead v-model="filter.letterhead"  @onSelect="onSelectLetterHead"/>
            </div>
            <div class="col-6">
                <label>Language</label><br>
                <ComSelect :clear="false" v-model="filter._lang" doctype="Language" optionLabel="language_name" optionValue="name"
                :filters="[['enabled', '=', 1]]" />
            </div>
            </div>
        </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
        <div class="reactive border-bottom-1 w-full" style="height:20px;">
        <i @click="onShowfilter" :class="showFilter ? 'pi-chevron-up': 'pi-chevron-down' " class="pi h-1rem text-sm cursor-pointer  w-full text-center" style="left:56%;margin-top:-15px;"></i>
        <hr class="mt-3"/>
        </div>

</template>
<script setup>
import { ref, inject,onMounted } from "@/plugin"
import Calendar from 'primevue/calendar';
import Checkbox from 'primevue/checkbox';
const emit = defineEmits(['onFilter'])

const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const user = JSON.parse(localStorage.getItem("edoor_user"))
const property = setting.property
const moment = inject("$moment")
const showFilter = ref(true)
const props = defineProps({
    selectedReport: Object,
    filter: Object
})

function onShowfilter() {
    showFilter.value = !showFilter.value
    localStorage.setItem("edoor_show_filter", showFilter.value ? "1" : "0")
    onRefresh()
}
const showCustomReport = ref()

const customReport = (event) => {
    showCustomReport.value.toggle(event);
}
const onCloseCustomReport = () => {
    showCustomReport.value.hide()
}
const showAdvanceSearch = ref()
const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const filter = ref({
    _lang: user.language || "en",
    start_date: moment().toDate(),
    end_date: moment().toDate(),
    order_by:"Last Update On",
    audit_order:"Last Update On",
    is_active_reservation: "1" ,
    sort_order: "ASC",
    filter_date_by:"Arrival Date",
    summary_filter:"Business Source",

})
function onSelectLetterHead(l){
    filter.value.letterhead = l
}
const hasFilter = ref((f) => {
    if (props.selectedReport) {
        return props.selectedReport.filter_option?.includes(f)
    }
    return false

});

function onSearch() {
    let f = {}
   
    const filter_option = props.selectedReport.filter_option + ",_lang,letterhead"
    if (filter_option) {
        filter_option.split(",").forEach(r => {

            f[r.trim()] = filter.value[r.trim()]

        })
    }

    if (f.start_date) {
        f.start_date = moment(f.start_date).format("YYYY-MM-DD")
    }

    if (f.end_date) {
        f.end_date = moment(f.end_date).format("YYYY-MM-DD")
    }
    window.report_filter = filter.value
    emit("onFilter", f)
}

onMounted(() => {
    onSearch()
})
</script>