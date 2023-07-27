<template lang="">
    <div>
         
        <ComHeader isRefresh @onRefresh="onRefresh()">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Frontdesk</div>
                        <div class="ml-8 header-title text-2xl" v-if="moment(filter.date).format('yyyy') != moment(filter.end_date).format('yyyy')">{{moment(filter.date).format('MMM DD, yyyy')}} - {{moment(filter.end_date).format('MMM DD, yyyy')}}</div>
                        <div class="ml-8 header-title text-2xl" v-else>{{moment(filter.date).format('MMM DD')}} - {{moment(filter.end_date).format('MMM DD, yyyy')}}</div>
                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 justify-content-end">
                    <Button class="bg-yellow-500 border-none" @click="showNote=!showNote">
                        <ComIcon icon="iconNoteWhite" class="me-2" style="height: 16px;" />
                        Note
                    </Button>
                    <NewFITReservationButton/>
                    <NewGITReservationButton/>
                  
                </div>
            </template>
        </ComHeader>
        <div class="flex justify-between mb-3 filter-calen-fro">
            <ComRoomChartFilterSelect @onFilterResource="onFilterResource" @onSearch="onSearch">
                <template #date>
                    <Calendar class="btn-set__h" panelClass="room-chart-celendar" v-model="selectedDate" dateFormat="dd-mm-yy" @date-select="onFilterDate" showButtonBar showIcon />
                </template>
            </ComRoomChartFilterSelect>
            <div>
                <ComRoomChartFilter :viewType="filter.view_type" @onView="onView" @onPrevNext="onPrevNext($event)" @onToday="onFilterToday()" @onFilter="onFilter($event)"/>
            </div>
        </div>
        <div style="max-width: 100%;">
            <div id="fron__desk-fixed-top">
                <div :class="showSummary ? 'flex gap-2' : ''">
                    <div v-if="showSummary" class="relative" style="width:280px">
                        <div>
                            <div class="w-full">
                                <ComPanel title="Today Guest" class="mb-3 pb-3">
                                    <div>
                                        <ComTodaySummary :date="filter.date"/>
                                    </div>
                                </ComPanel>
                                <ComPanel title="Room Status" class="pb-3 mb-3 front-house__kep">
                                    <ComHousekeepingStatus/>
                                </ComPanel>

                                <ComPanel title="Reservation Status" class="pb-3">
                                    <ReservationStatusLabel/>
                                </ComPanel>
                            </div> 
                        </div>
                    </div>
                    <div class="relative" aria-haspopup="true" aria-controls="overlay_menu" :class="showSummary ? 'chart-show-summary':''">
                       
                        <Sidebar v-model:visible="showNote" class="top-20 -mt-1 w-3" style="padding-bottom: 82px;" position="right">
                            <template #header>
                                <div class="flex justify-between items-center me-2">
                                    <div class="absolute left-5 text-xl"> Notes </div>
                                </div>
                            </template>
                            <hr class="left-0 fixed w-full">
                            <ComNoteGlobal v-if="showNote"/>    
                        </Sidebar>
                        

                        <FullCalendar ref="fullCalendar" :options="calendarOptions" class="h-full">
                            <template v-slot:eventContent="{event}"> 
                                    <div class="group relative h-full p-1" style="height: 36px"
                                  
                                    >
                                        <div class="flex">
                                            <span class="h-1rem w-1rem rounded-full" :style="{backgroundColor:event.extendedProps.reservation_color}" v-if="event.extendedProps.reservation_color">
                                                
                                            </span>
                                            <span v-if="event.extendedProps.is_master">
                                                <ComIcon style="height: 12px;" icon="iconCrown"/>
                                            </span>
                                            
                                            <div>{{event.title}}</div>
                                        </div>
                                    </div>
                            </template> 
                        </FullCalendar>

                    
                    </div>
                </div>
            </div>
        </div>
    </div>
  </template>
<script setup>
import { ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted,watch } from '@/plugin'
import FullCalendar from '@fullcalendar/vue3'
import '@fullcalendar/core/vdom' // solves problem with Vite
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';
import interactionPlugin from '@fullcalendar/interaction'

import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import iconEdoorAddGroupBooking from '../../assets/svg/icon-add-group-booking.svg'
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComRoomChartFilter from './components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from './components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from './components/ComRoomChartFilterSelect.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'
import Tooltip from 'primevue/tooltip'
import { useTippy } from 'vue-tippy'
 

 


const socket = inject("$socket");
const frappe = inject('$frappe')
const call = frappe.call();
const moment = inject('$moment')
const filter = reactive({
    peroid: 'today',
    view_type: '',
    date: '',
    end_date: ''
})
const selectedDate = ref()
const titleStartEndDate = reactive({})
const fullCalendar = ref(null)
const gv = inject("$gv")

const toast = useToast();
const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")
const initialDate = onInitialDate()
let fullcalendarInitialDate = ref(initialDate.start)
let showTooltip = ref(false)
const reservation = ref({})
const isLoading = ref(true)
const showSummary = ref(true)
const showNote = ref(false)
if (edoorShowFrontdeskSummary) {
    showSummary.value = edoorShowFrontdeskSummary == "1";
}

let eventInfo = reactive({
    isShow: false,
    left: 0,
    top: 0,
    data: null
})
let roomChartResourceFilter = reactive({
    property: property.name,
    view_type: filter.view_type // room_type = true or room = false
})

let eventKeyword = ref()

socket.on("RefresheDoorDashboard", (arg) => {
    
    if (arg == property.name) {
        onRefresh()
        toast.add({ severity: 'info', summary: 'Info', detail: "Reservation updated", life: 3000 })

    }
})

 
watch(() => filter.date, (newValue, oldValue) => {
    selectedDate.value = new Date(newValue)
})

function dateFormat(date) {
    return moment(date).format("MMM DD, YYYY")
}

const calendarOptions = reactive({
    plugins: [
        interactionPlugin,
        resourceTimelinePlugin
        
    ],
    schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
    timeZone: 'UTC',
    initialView: 'resourceTimeline',
    resourceOrder: 'sort_order',
    dateIncrement: { days: 3 },
    nowIndicator: true,
    now: working_day.date_working_day + " 12:00:00",
    initialDate: fullcalendarInitialDate.value,
    stickyHeaderDates: true,
    headerToolbar: false,
    refetchResourcesOnNavigate: true,
    loading: function(loading) {
        gv.loading = loading
    },
    visibleRange: function (currentDate) {
        const startDate = initialDate.start
        const endDate = initialDate.end
        return { start: startDate, end: endDate };
    },
    resourceAreaColumns: resourceColumn(),
     
    resources: function (info, successCallback, failureCallback) {
        call.get('edoor.api.frontdesk.get_room_chart_resource', roomChartResourceFilter).then((result) => {
            successCallback(result.message)
        }).catch((error) => {
            console.log(error)
        });
    },
    events: function (info, successCallback, failureCallback) {

        call.get('edoor.api.frontdesk.get_room_chart_calendar_event', {
            start: info.start,
            end: info.end,
            property: property.name,
            keyword: eventKeyword.value,
        }).then((result) => {
            successCallback(result.message)
        })
            .catch((error) => {
                alert("load data fiale")
            });
    },
    eventAllow: function (dropInfo, draggedEvent) {
        
     
        return draggedEvent._def.extendedProps.can_resize
    },
    selectable: true,
    editable: true,
    eventResizableFromStart: true,
    resourceAreaWidth: "250px",
    height: 'auto',
    slotDuration: {
        "hours": 12
    },
    slotLabelInterval: {
        "hours": 24
    },

    slotLabelFormat: function (date) {

        return " "
    },

    slotLabelDidMount: function (info) {

        const d = moment(info.date).format("DD")
        const day = moment(info.date).format("ddd")
        if (moment(info.date).format("yyyy-MM-DD") == working_day.date_working_day) {
            info.el.getElementsByTagName("a")[0].innerHTML = "<div class='current_day line-height-15 border-round-lg px-3 py-2'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(info.date).format("MMM") + "</span></div>"
        } else {
            if (day == "Sat" || day == "Sun") {
                info.el.getElementsByTagName("a")[0].innerHTML = "<div class='line-height-15  border-round-lg px-3 py-2' style='color:red;'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(info.date).format("MMM") + "</span></div>"
            }
            else {
                info.el.getElementsByTagName("a")[0].innerHTML = "<div class='line-height-15  border-round-lg px-3 py-2'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(info.date).format("MMM") + "</span></div>"
            }
        }
    },

    select: (($event) => {

        onSelectedDate($event)
    }),
    eventResizeStop: (($event) => {
        console.log($event)
    }),
    eventClick: ((info) => {
        const data = info.event._def.extendedProps;
        if (data.type == "stay") {
            showReservationStayDetail(data.reservation_stay)
        } else {
            alert("Open dialog of " + data.type)
        }

    }),
    eventMouseEnter: (($event) => {
        const event=$event.event._def
       
        
        if(event.extendedProps.type =="stay" || event.extendedProps.type =="room_block" ){

        
        const description=`<div style="background:red">
                                        <table>
                                            <tbody>
                                            <tr><td><div>ID: ${event.reservation || ''}</div></td></tr>
                                            <tr><td><div>Ref #: ${event.reference_number || ''}</div></td></tr>
                                            <tr><td><div>Guest: ${event.title}</div></td></tr>
                                            <tr><td><div>Start Date: ${dateFormat(event.start)}</div></td></tr>
                                            <tr><td><div>End Date: ${dateFormat(event.end)}</div></td></tr>
                                            <tr><td><div>Room: ${event.extendedProps?.room_number}</div></td></tr>
                                            <tr><td><div>Adult: ${event.extendedProps?.adult} Child: ${event.extendedProps?.child} Pax: ${event.extendedProps?.pax}</div></td></tr>
                                            </tbody>
                                        </table>
                                    </div>`
 

        const { tippyInstance } = useTippy($event.el, {
            content: description,
        })
    }
      
   
        
    }),
    eventDrop: function (info) {
        if (!confirm("Are you sure about this change?")) {
            info.revert();
        }
    }

})

function getRoomChartlocationStorage() {
    if (localStorage.getItem('reservation_chart')) {
        const result = JSON.parse(localStorage.getItem('reservation_chart'))
        filter.date = moment(result.start_date).add(1, 'days').format("yyyy-MM-DD")
        filter.end_date = result.end_date
        return result;

    } else {
        let _date = moment(working_day.date_working_day).add(-1, 'days').format("yyyy-MM-DD")
        const dataStorage = {
            view: 'room_type',
            peroid: 'today',
            start_date: _date,
            end_date: moment(_date).add(1, 'months').format("yyyy-MM-DD")
        }

        localStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
        if (localStorage.getItem('reservation_chart')) {
            const result = JSON.parse(localStorage.getItem('reservation_chart'))
            filter.date = moment(result.start_date).add(1, 'days').format("yyyy-MM-DD")
            filter.end_date = result.end_date
            return result
        }

        return ''
    }
}
function setRoomChartlocationStorage(start_date = '', end_date = '', view = '', peroid = '') {
    // set room chart localstorage

    let dataStorage = getRoomChartlocationStorage()
    if (start_date != '')
        dataStorage.start_date = start_date
    if (end_date != '')
        dataStorage.end_date = end_date
    if (view != '')
        dataStorage.view = view
    if (peroid != '')
        dataStorage.peroid = peroid



    localStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
    filter.date = moment(dataStorage.start_date).add(1, 'days').format("yyyy-MM-DD")
    filter.end_date = dataStorage.end_date
    return dataStorage

}

function onFilterToday() {
    const startDate = moment(working_day.date_working_day).subtract(1, 'days').format("yyyy-MM-DD")
    const currentViewChart = setRoomChartlocationStorage(startDate, '', '', '')
    onFilter(currentViewChart.peroid)

}

function onInitialDate() {
    const roomChartStorage = getRoomChartlocationStorage()

    return {
        start: roomChartStorage.start_date,
        end: roomChartStorage.end_date
    }

}
function onSelectedDate(event) {
    const start = event.startStr
    const end = event.endStr
    const totalSlotsSelected = Math.abs(new Date(end) - new Date(start)) / 1000 / 60 / 60 / 24

    if (totalSlotsSelected < 1) {
        return
    }

    if (event.resource._resource.extendedProps.type == "room") {
        let room_type_id =  event.resource._resource.extendedProps.room_type_id ?? ""
        
        if(room_type_id==""){
          
            room_type_id = event.resource._resource.parentId;
        }
        
        const dialogRef = dialog.open(NewReservation, {
            data: {
                arrival_date: event.start,
                departure_date: event.end,
                room_type_id: room_type_id,
                room_id: event.resource._resource.id
            },
            props: {
                header: 'New Reservation',
                style: {
                    width: '80vw',
                },
                breakpoints: {
                    '960px': '100vw',
                    '640px': '100vw'
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false
            },
            onClose: (options) => {
                const data = options.data;
                if (data != undefined) {
                    showReservationDetail(data.name)
                }
            }
        });
    }


}
function resourceColumn() {
    if (filter.view_type == 'room_type') {
        return [
            {
                labelText: 'xxx',
                headerContent: 'Room'
            },
            {
                field: 'housekeeping_status',
                width: 40,
                cellContent: function (arg) {
                    const el = arg.resource._context.calendarApi.el
                    const item = arg.resource.extendedProps
                    if (item.housekeeping_icon) {
                        el.innerHTML = `<div class="cell-status text-center" title="${arg.fieldValue}">${item.housekeeping_icon}</div>`;
                    }
                    else {
                        el.innerHTML = ''
                    }

                    let dom = [el.innerHTML]
                    return { html: dom }
                }
            }
        ]
    } else {
        return [
            {
                labelText: 'xxx',
                headerContent: 'Room'
            },
            {
                field: 'room_type_alias',
                headerContent: 'Room Type',
                cellContent: function (arg) {
                    const el = arg.resource._context.calendarApi.el
                    const item = arg.resource.extendedProps

                    if (item.room_type) {
                        el.innerHTML = `<div title="${item.room_type}">${arg.fieldValue}</div>`;
                    }
                    else {
                        el.innerHTML = ''
                    }
                    const dom = [el.innerHTML]
                    return { html: dom }
                }
            },
            {
                field: 'housekeeping_status',
                width: 40,
                cellContent: function (arg) {
                    const el = arg.resource._context.calendarApi.el
                    const item = arg.resource.extendedProps
                    if (item.housekeeping_icon) {
                        el.innerHTML = `<div class="cell-status text-center" title="${arg.fieldValue}">${item.housekeeping_icon}</div>`;
                    }
                    else {
                        el.innerHTML = ''
                    }

                    const dom = [el.innerHTML]
                    return { html: dom }
                }
            }
        ]
    }
}

function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_show_frontdesk_summary", showSummary.value ? "1" : "0")
}

function onView() {
    filter.view_type = filter.view_type == 'room_type' ? 'room' : 'room_type'
    roomChartResourceFilter.view_type = filter.view_type
    setRoomChartlocationStorage('', '', filter.view_type, '')
    const cal = fullCalendar.value.getApi()
    cal.setOption('resourceAreaColumns', resourceColumn())
    cal.refetchResources()
}
function onFilter(key) {
    filter.peroid = key
    const cal = fullCalendar.value.getApi()
    const visibleRange = cal.currentData.options.visibleRange
    if (key == 'week') {
        const currentViewChart = setRoomChartlocationStorage('', '', '', key)
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(7, 'days').subtract(1, 'days').format("yyyy-MM-DD")

        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', '')
        cal.changeView('resourceTimeline', { start: moment(setViewChart.start_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss'), end: moment(setViewChart.end_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss') });
    }
    else if (key == '14_days') {
        const currentViewChart = setRoomChartlocationStorage('', '', '', key)
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(14, 'days').subtract(1, 'days').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', '')
        cal.changeView('resourceTimeline', { start: moment(setViewChart.start_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss'), end: moment(setViewChart.end_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss') });
        // cal.changeView('resourceTimeline', { start: setViewChart.start_date, end: setViewChart.end_date });
    }
    else {
        var currentViewChart = getRoomChartlocationStorage()
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(1, 'months').subtract(1, 'days').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', key)
        cal.changeView('resourceTimeline', { start: moment(setViewChart.start_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss'), end: moment(setViewChart.end_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss') });
        // cal.changeView('resourceTimeline', { start: setViewChart.start_date, end: setViewChart.end_date });
    }
}

function onFilterDate(event) {
    filter.date = event
    const filter_date = moment(event).add(-1, 'days').format("yyyy-MM-DD")
    const setViewChart = setRoomChartlocationStorage(filter_date, '', '', '', '')
    onFilter(setViewChart.peroid)
}
function onPrevNext(key) {
    const cal = fullCalendar.value.getApi()
    const dateIncrement = cal.currentData.options.dateIncrement
    const currentViewChart = getRoomChartlocationStorage()
    if (key == 'prev') {
        const start = moment(currentViewChart.start_date).subtract(dateIncrement.days, 'days').format('yyyy-MM-DD')
        const end = moment(currentViewChart.start_end).subtract(dateIncrement.days, 'days').format('yyyy-MM-DD')
        const setCurrentViewChart = setRoomChartlocationStorage(start, end, '', '')
        onFilter(setCurrentViewChart.peroid, true)
    } else {
        const start = moment(currentViewChart.start_date).add(dateIncrement.days, 'days').format('yyyy-MM-DD')
        const end = moment(currentViewChart.start_end).add(dateIncrement.days, 'days').format('yyyy-MM-DD')
        const setCurrentViewChart = setRoomChartlocationStorage(start, end, '', '')
        onFilter(setCurrentViewChart.peroid, true)
    }
}

const onRefresh = () => {
    const cal = fullCalendar.value.getApi()
    cal.refetchEvents()
    
 
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
            position:"top"
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                if (data.action = "view_reservation_detail") {
                    showReservationDetail(data.reservation)
                }
            }
        }
    });
}



function showReservationDetail(name) {

    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top"
        },
        onClose: (options) => {
            const data = options.data;
        }
    });
}



/// filter rescource
function onFilterResource(f){ 
    roomChartResourceFilter = {
        property: property.name,
        room_type_group: f.room_type_group,
        room_type: f.room_type,
        building: f.building,
        floor: f.floor,
        room_number:f.room_number,
        view_type: filter.view_type // room_type = true or room = false
    }
    const cal = fullCalendar.value.getApi()
    cal.refetchResources()
}
// search event
function onSearch(key){
    eventKeyword.value = key 
    onRefresh()
    // cal.setOption({now:"2023-05-18"})
 
}

onMounted(() => {
 
    onInitialDate()
 
    if(!selectedDate.value){
        const currentViewChart = JSON.parse(localStorage.getItem('reservation_chart'))
        selectedDate.value = new Date(moment(currentViewChart.start_date).add(1,'days'))
    }
    // var list = document.getElementsByClassName("fc-resource")
    
})
onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
})
</script>
<style>
.fc .fc-timeline-header-row-chrono .fc-timeline-slot-frame {
    justify-content: center !important
}

.current_day {
    background: #5b029f;
    color: #fff;
}

.line-height-15 {
    line-height: 15px;
}

.room-chart-celendar .p-datepicker-buttonbar button[aria-label="Clear"] {
    display: none;
}

.room-chart-celendar .p-datepicker-buttonbar button[aria-label="Today"] {
    flex-grow: 1;
}

.chart-show-summary {
    width: calc(100% - 250px);
}

.fc-timeline-slot:hover {
  background: #DBDBDB;
  opacity: 0.4;
}
 
</style>