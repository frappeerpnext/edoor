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
                    <Button label='Uncomming Note' :badge="totalNotes" badgeClass="bg-white text-600 badge-rs" class="bg-yellow-500 border-none" @click="showNote=!showNote">
                      <ComIcon icon="iconNoteWhite" class="me-2" height="18px" />  Uncomming Note <Badge
                      style="font-weight: 600 !important;" class="badge-rs bg-white text-500" :value="totalNotes"
                      severity="warning">
                    </Badge>
                    </Button>
                    <NewFITReservationButton/>
                    <NewGITReservationButton/>
                </div>
            </template>
        </ComHeader>
        <div class="flex justify-between mb-3 filter-calen-fro"> 
            <div class="flex gap-2">
                <div>
                    <Calendar class="w-full" v-model="filter.date" @date-select="onFilterDate" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
                </div>
                <div>
                    <span class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText class="btn-set__h w-full" v-model="keyword.room_number" placeholder="All Rooms" v-debounce="onSearchRoom"/>
                    </span>
                </div>
                <div>
                    <span class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText class="btn-set__h w-full"  placeholder="Keyword" v-debounce="onSearch"/>
                    </span>
                </div>
                <div>
                    <Button icon="pi pi-sliders-h" class="content_btn_b" @click="onOpenAdvanceSearch"/>
                </div> 
                <div v-if="isFilter">
                    <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter"/>
                </div>
            </div>
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
                                        <ComTodaySummary :date="working_day.date_working_day"/>
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
                        <div class="mt-2" style="height: 22px;"></div>
                    </div>
                    <div class="relative" aria-haspopup="true" aria-controls="overlay_menu" :class="showSummary ? 'chart-show-summary':''">
                       
                        <Sidebar v-model:visible="showNote" class="top-20 -mt-1 lg:w-5 w-full xl:w-3" style="padding-bottom: 82px;" position="right">
                            <template #header>
                                <div class="flex justify-between items-center me-2">
                                    <div class="absolute left-5 line-height-1">
                                        <div class="text-sm">Uncomming</div>    
                                        <div class="text-xl">Notes</div>
                                    </div>
                                </div>
                            </template>
                            <hr class="left-0 fixed w-full">
                            <ComNoteGlobal v-if="showNote"/> 
                        </Sidebar>
                        <FullCalendar ref="fullCalendar" :options="calendarOptions" class="h-full">
                            <template v-slot:eventContent="{event}"> 
                                    <div class="group relative h-full p-1" :class="event.extendedProps.type" style="height: 36px">
                                        <div class="flex">
                                            <!-- <span class="ml-1 display-block stay-identify-position" :style="{backgroundColor:event?.extendedProps?.group_color}" v-if="event?.extendedProps?.group_color"></span> -->
                                            <span class="ml-1 display-block stay-identify-position" :style="{backgroundColor:event.extendedProps.reservation_color}" v-if="event.extendedProps.reservation_color">
                                                
                                            </span>
                                            <span class="wrp-statu-icon">
                                                <span v-if="event.extendedProps.is_master" class="stay-bar-status mr-1">
                                                    <ComIcon style="height: 12px;" icon="iconCrown"/>
                                                </span>
                                                <span v-if="event.extendedProps.reservation_type=='GIT'" class="stay-bar-status mr-1">
                                                    <ComIcon style="height: 12px;" icon="iconUserGroup"/>
                                                </span>
                                            </span>
                                            <div class="geust-title">
                                                {{event.title}}
                                            </div>
                                        </div>
                                    </div>
                            </template> 
                        </FullCalendar>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
        <ComRoomChartFilterSelect headerClass="grid" bodyClass="col-4"></ComRoomChartFilterSelect>
    </OverlayPanel>
    </template>
<script setup>
import { ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted, watch, getApi, getCount, provide, computed, getDocList } from '@/plugin'
import '@fullcalendar/core/vdom' // solves problem with Vite
import FullCalendar from '@fullcalendar/vue3'
import interactionPlugin from '@fullcalendar/interaction'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';

import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import iconEdoorAddGroupBooking from '../../assets/svg/icon-add-group-booking.svg'
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComConfirmChangeStay from "@/views/frontdesk/components/ComConfirmChangeStay.vue"
import ComRoomChartFilter from './components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from './components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from './components/ComRoomChartFilterSelect.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'

import { useTippy } from 'vue-tippy'




const resources = ref([])
const events = ref([])


const socket = inject("$socket");

const moment = inject('$moment')
const filter = reactive({
    peroid: 'today',
    view_type: '',
    date: moment().toDate(),
    end_date: ''
})
const selectedDate = ref()
const showAdvanceSearch = ref()

const fullCalendar = ref(null)
const gv = inject("$gv")

const toast = useToast();
const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")
const initialDate = onInitialDate()
let fullcalendarInitialDate = ref(initialDate.start)

const keyword = ref({
    guest: '',
    room_number: ''
})

const showSummary = ref(true)
const showNote = ref(false)
const totalNotes = ref(0)
let advanceFilter = ref({
    room_type: "",
    room_number: "",
    room_type_group: "",
    building: "",
    floor: ""
})
const isFilter = computed(() => {
    if (gv.dateFormat(filter.date) != gv.dateFormat(working_day.date_working_day)) {
        return true
    }
    else if (eventKeyword.value || gv.isNotEmpty(advanceFilter.value, 'property')) {
        return true
    } else {
        return false
    }
})
provide('get_count_note', {
    getTotalNote
})




if (edoorShowFrontdeskSummary) {
    showSummary.value = edoorShowFrontdeskSummary == "1";
}

let roomChartResourceFilter = reactive({
    property: property.name,
    view_type: filter.view_type // room_type = true or room = false
})

let eventKeyword = ref()

 
socket.on("test_socket", (arg) => {
    console.log(arg)
    
    alert(111)
})

socket.on("RefresheDoorDashboard", (arg) => {

    if (arg == property.name) {
        onRefresh()
        toast.add({ severity: 'info', summary: 'Info', detail: "Reservation updated", life: 3000 })

    }
})


watch(() => filter.date, (newValue, oldValue) => {

    selectedDate.value = new Date(newValue)
})


const calendarEvents = computed(() => {
    if (keyword.value.keyword) {

        return events.value.filter(r => (r.title || "").toLowerCase().includes((keyword.value.keyword || "").toLowerCase()))
    } else {
        return events.value
    }

})

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
    loading: function (loading) {
        gv.loading = loading
    },
    visibleRange: function (currentDate) {
        const startDate = initialDate.start
        const endDate = initialDate.end
        return { start: startDate, end: endDate };
    },
    resourceAreaColumns: resourceColumn(),

    resources: resources,
    events: events,
    eventAllow: function (dropInfo, draggedEvent) {
        
        return draggedEvent._def.extendedProps.can_resize == 1
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

     eventResize: (($event) => {  
        
        const dialogRef = dialog.open(ComConfirmChangeStay, {
            data: $event.event,
            props: {
                header: 'Change Stay',
                style: {
                    width: '50vw',
                },
                modal: true,
                closeOnEscape: false,
                position: 'top'
            },
            onClose: (options) => {
              
                const data = options.data;
                if (!data) {
                    $event.revert()

                }
            }
        });

    }),
    eventClick: ((info) => {

        const data = info.event._def.extendedProps;
        if (data.type == "stay") {
            showReservationStayDetail(data.reservation_stay)
        } else {
            info.event._def.date = info.event.start;
            alert(JSON.stringify(info.event._def))
            window.postMessage(info.event._def, '*')
        }

    }),
    eventMouseEnter: (($event) => {
        const event = $event.event._def

        if (event.extendedProps.type == "stay") {

            const description = `<div class="p-2 w-full">
                                        <div class="text-center border-1 p-2 border-round-lg">Reservation</div>
                                        <table class="tip_description_stay_table m-1 pt-3">
                                            <tbody>
                                            <tr class="table-rs-de" ><td>Res. No</td><td class="px-2">:</td><td>${event.extendedProps?.reservation || ''}</td></tr>
                                            <tr class="table-rs-de"><td>Res Stay. No</td><td class="px-2">:</td><td>${event.extendedProps?.reservation_stay || ''}</td></tr>    
                                            <tr class="table-rs-de"><td>Ref. No</td><td class="px-2">:</td><td>${event.extendedProps?.reference_number || ''} </td></tr>
                                            <tr class="table-rs-de"><td>Int. No</td><td class="px-2">:</td><td>${event.extendedProps?.internal_reference_number ?? ''}</td></tr>
                                            <tr class="table-rs-de"><td>Ref. type</td><td class="px-2">:</td><td>${event.extendedProps?.reservation_type || ''} ${event.extendedProps?.group_code ? '( ' + event.extendedProps?.group_code + ' )' : ''}</td></tr>    
                                            <tr class="table-rs-de"><td>Guest</td><td class="px-2">:</td><td>${event.title}</td></tr>
                                            <tr class="table-rs-de"><td>Arrival</td><td class="px-2">:</td><td>${gv.dateFormat(event.extendedProps?.arrival_date)} - ${gv.timeFormat(event.extendedProps?.start_time)}</td></tr>
                                            <tr class="table-rs-de"><td>Departure</td><td class="px-2">:</td><td>${gv.dateFormat(event.extendedProps?.departure_date)} - ${gv.timeFormat(event.extendedProps?.end_time)}</td></tr>
                                            <tr class="table-rs-de"><td>Room</td><td class="px-2">:</td><td>${event.extendedProps?.room_number}</td></tr>
                                            <tr class="table-rs-de"><td>Pax</td><td class="px-2">:</td><td>${event.extendedProps?.adult} / ${event.extendedProps?.child}</td></tr>
                                            <tr class="table-rs-de"><td>Source</td><td class="px-2">:</td><td>${event.extendedProps?.business_source || ''}</td></tr>
                                            <tr class="table-rs-de"><td>ADR</td><td class="px-2">:</td><td>${gv.currencyFormat(event.extendedProps?.adr)}</td></tr>
                                            <tr class="table-rs-de"><td>Total Room Rate</td><td class="px-2">:</td><td>${gv.currencyFormat(event.extendedProps?.total_room_rate)}</td></tr>
                                            <tr class="table-rs-de"><td>Total Debit</td><td class="px-2">:</td><td>${gv.currencyFormat(event.extendedProps?.total_debit)}</td></tr>
                                            <tr class="table-rs-de"><td>Total Credit</td><td class="px-2">:</td><td>${gv.currencyFormat(event.extendedProps?.total_credit)}</td></tr>
                                            <tr class="table-rs-de"><td>Balance</td><td class="px-2">:</td><td>${gv.currencyFormat(event.extendedProps?.balance)}</td></tr>
                                            ${(event.extendedProps?.note != "null" && event.extendedProps?.note) ? `
                                            <tr><td><span class="mt-2">Note</span></td></tr>
                                            <tr><td colspan="3"><div class="border-round-lg p-2 reason-box-style" >${event.extendedProps?.note.length > 220 ? event.extendedProps?.note.substring(0, 220) + '...' : event.extendedProps?.note}</div></td></tr>
                                            ` : ''}
                                            </tbody>
                                        </table>
                                    </div>`


            const { tippyInstance } = useTippy($event.el, {
                content: description,
            })
        } else if (event.extendedProps.type == "room_block") {
            const description = `<div class="w-full p-2">
                                        <div class="text-center border-1 p-2 border-round-lg">${event.title}</div>
                                        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
                                            <tbody>
                                            <tr class="table-rs-de" ><td>Block Number</td><td class="px-3">:</td><td>${event?.publicId || ''}</td></tr>  
                                            <tr class="table-rs-de"><td>Start Date</td><td class="px-3">:</td><td>${gv.datetimeFormat(event?.start)}</td></tr>
                                            <tr class="table-rs-de"><td>Release Date</td><td class="px-3">:</td><td>${gv.datetimeFormat(event?.end)}</td></tr>
                                            <tr class="table-rs-de"><td>Blocked by</td><td class="px-3">:</td><td>${event.extendedProps?.block_by || ''}</td></tr>
                                            <tr><td><span class="mt-2">Reason</span></td></tr>
                                            <tr><td colspan="3"><div class="border-round-lg p-2 reason-box-style" >${event.extendedProps?.reason}</div></td></tr>
                                            </tbody>
                                        </table>
                                    </div>`
            const { tippyInstance } = useTippy($event.el, {
                content: description,
            })
        }
        else if (event.extendedProps.type == "available_room") {
            const description = `<div class="pt-1"> Available Room ${event.title} </div> `
            const { tippyInstance } = useTippy($event.el, {
                content: description,
            })
        } else if (event.extendedProps.type == "unassign_room") {
            const description = `<div class="pt-1"> Unassign Room ${event.title} </div> `
            const { tippyInstance } = useTippy($event.el, {
                content: description,
            })
        }
    }),
    eventDrop: function (info) {
        if (!confirm("Are you sure about this change?")) {
            info.revert();
        }
    },




})



function getRoomChartlocationStorage() {
    if (sessionStorage.getItem('reservation_chart')) {
        const result = JSON.parse(sessionStorage.getItem('reservation_chart'))
        filter.date = moment(result.start_date).add(1, 'days').toDate()

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

        sessionStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
        if (sessionStorage.getItem('reservation_chart')) {
            const result = JSON.parse(sessionStorage.getItem('reservation_chart'))
            filter.date = moment(result.start_date).add(1, 'days').toDate()
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



    sessionStorage.setItem('reservation_chart', JSON.stringify(dataStorage))

    filter.date = moment(dataStorage.start_date).add(1, 'days').toDate()

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
        let room_type_id = event.resource._resource.extendedProps.room_type_id ?? ""

        if (room_type_id == "") {

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
                closeOnEscape: false,
                position: 'top'
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
                        el.innerHTML = `<div id='room_status_${arg.resource._resource.id}' class="cell-status text-center room-status" data-title="${arg.fieldValue}">${item.housekeeping_icon}</div>`;
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
                        el.innerHTML = `<div  title="${item.room_type}">${arg.fieldValue}</div>`;
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
                        el.innerHTML = `<div id='room_status_${arg.resource._resource.id}' class="cell-status text-center room-status" data-title="${arg.fieldValue}">${item.housekeeping_icon}</div>`;
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
    onRefresh()
}

function onView() {
    filter.view_type = filter.view_type == 'room_type' ? 'room' : 'room_type'

    roomChartResourceFilter.view_type = filter.view_type

    setRoomChartlocationStorage('', '', filter.view_type, '')

    getResource()



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
    getEvent()
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
    getEvent()
    getTotalNote()

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
            position: "top"
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
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
        }
    });
}



/// filter rescource
function onFilterResource(f) {
    roomChartResourceFilter = {
        property: property.name,
        room_type_group: f.room_type_group,
        room_type: f.room_type,
        building: f.building,
        floor: f.floor,
        room_number: f.room_number,
        view_type: filter.view_type // room_type = true or room = false
    }
    advanceFilter.value = roomChartResourceFilter
    getResource()
}
// search event
function onSearch(key) {

    keyword.value.keyword = key
}

function getTotalNote() {
    getCount('Frontdesk Note', [["note_date", ">=", working_day.date_working_day]]).then((docs) => {
        totalNotes.value = docs
    })
}

function getResource(get_event = false) {

    getApi('frontdesk.get_room_chart_resource', roomChartResourceFilter).then((result) => {
        resources.value = result.message
        const cal = fullCalendar.value.getApi()
        cal.setOption('resourceAreaColumns', resourceColumn())
        if (get_event == true) {
            getEvent()
        }

        setTimeout(() => {

            const room_status = document.getElementsByClassName("room-status")
            for (let i = 0; i < room_status.length; i++) {
                let el = room_status[i]
                useTippy(el, {
                    content: el.getAttribute("data-title")
                })
            }
        }, 3000);

    })
}
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


const getEvent = debouncer(() => {

    const cal = fullCalendar.value.getApi()

    getApi('frontdesk.get_room_chart_calendar_event', {
        start: moment(cal.view.currentStart).format("YYYY-MM-DD"),
        end: moment(cal.view.currentEnd).format("YYYY-MM-DD"),
        property: property.name,
        keyword: eventKeyword.value,
    }).then((result) => {
        events.value = (result.message)
    })

}, 500);



onMounted(() => {


    onInitialDate()

    if (!selectedDate.value) {
        const currentViewChart = JSON.parse(sessionStorage.getItem('reservation_chart'))
        selectedDate.value = new Date(moment(currentViewChart.start_date).add(1, 'days'))
    }
    getResource(true)

    getTotalNote()
})

onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
})

const onOpenAdvanceSearch = (event) => {
    if (event == false) {
        showAdvanceSearch.value.hide()
    }
    else {
        showAdvanceSearch.value.toggle(event);
    }
}

const onClearFilter = () => {
    keyword.value.guest = ''
    keyword.value.room_number = ''
    onSearch('')
    onFilterResource({})
    onFilterToday()
    onOpenAdvanceSearch(false)
}
function onSearchRoom(key) {
    advanceFilter.value.room_number = key
    onFilterResource(advanceFilter.value)

}
provide('advance_filter', {
    onOpenAdvanceSearch,
    advanceFilter,
    onFilterResource,
    onClearFilter
})

</script>
<style>
.fc .fc-timeline-header-row-chrono .fc-timeline-slot-frame {
    justify-content: center !important
}

.fc.fc-theme-standard>.room-status {
    display: none;
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