<template lang="">
    <div>
        <ComHeader>
            <template #start>
                <Button @click="onShowSummary">Show Summary</Button>
                <div @click="onRefresh()">Frontdesk</div>
            </template>
            <template #end>
                <div class="flex  gap-2 justify-content-end">
                    <NewFITReservationButton/>
                    <Button label="New group booking" class="btn-date__tt btn-inner-set-icon">
                        <img class="mr-2" :src="iconEdoorAddGroupBooking">New group booking
                    </Button>
                </div>
            </template>
        </ComHeader>
        <div style="max-width: 100%; height: 1000px">
            <div>
                <div class="relative" aria-haspopup="true" aria-controls="overlay_menu">
                    <div class="flex justify-between mb-2">
                        <div>
                            <Calendar panelClass="room-chart-celendar" v-model="filter.date" dateFormat="dd-mm-yy" @date-select="onFilterDate" showButtonBar />
                        </div>
                        <div>
                            <ComRoomChartFilter :viewType="filter.view_type" @onView="onView" @onFilter="onFilter($event)" @onPrevNext="onPrevNext($event)" @onToday="onFilterToday()"/>
                        </div>
                    </div>
                    <div v-if="showSummary">
                        <ComTodaySummary/>
                        <ComHousekeepingStatus/>
                    </div>
                    <FullCalendar ref="fullCalendar" :options="calendarOptions" class="h-full">
                        <template v-slot:eventContent="{event}">
                                <!-- <div class="group relative h-full p-1" v-tooltip.bottom="{ value: `
                                <div class='tooltip-reservation text-sm -mt-6' style='width:350px; line-height: auto'>
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
                                </div>`, escape: true, class: 'event-tooltip' }">
                                
                                    {{ event.title }}
                                    
                                </div> -->
                                {{ event.title }}
                        </template>
                    </FullCalendar>
                    <ReservationStatusLabel/>
                </div>
            </div>
        </div>
    </div>
    
  </template>
<script setup>
import { ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted, computed } from '@/plugin'

import '@fullcalendar/core/vdom' // solves problem with Vite
import FullCalendar from '@fullcalendar/vue3'
import interactionPlugin from '@fullcalendar/interaction'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import iconEdoorAddGroupBooking from '../../assets/svg/icon-add-group-booking.svg'
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComRoomChartFilter from './components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from '@/views/frontdesk/components/ComTodaySummary.vue';
const socket = inject("$socket");
const frappe = inject('$frappe')
const call = frappe.call();
const moment = inject('$moment')
const fullCalendar = ref(null)

const toast = useToast();
const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")
let fullcalendarInitialDate = ref(onInitialDate())
let showTooltip = ref(false)
const reservation = ref({})
const isLoading = ref(true)
const showSummary = ref(true)
if (edoorShowFrontdeskSummary) {
    showSummary.value = edoorShowFrontdeskSummary == "1";
}

const filter = reactive({
    peroid: 'today',
    view_type: '',
    date: ''
})
let eventInfo = reactive({
    isShow: false,
    left: 0,
    top: 0,
    data: null
})
let roomChartResourceFilter = reactive({
    property: property.name,
    room_type: "room_type",
    building: "building",
    view_type: filter.view_type // room_type = true or room = false
})

socket.on("RefresheDoorDashboard", (arg) => {
    if (arg == property.name) {
        onRefresh()
        toast.add({ severity: 'info', summary: 'Info', detail: "Reservation updated", life: 3000 })

    }
})




function dateFormat(date) {
    return moment(date).format("MMM DD, YYYY")
}

const calendarOptions = reactive({
    plugins: [interactionPlugin, resourceTimelinePlugin],
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
    visibleRange: function (currentDate) {
        const startDate = moment(onInitialDate()).format('yyyy-MM-DD')
        const endDate = moment(onInitialDate()).add(31, 'days').format('yyyy-MM-DD')
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
            room_type: "room_type",
            building: "building"
        }).then((result) => {
            successCallback(result.message)
        })
            .catch((error) => {
                alert("load data fiale")
            });
    },
    eventAllow: function(dropInfo, draggedEvent) {
        return false
    },
    selectable: true,
    editable: false,
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

        //console.log(date.date.year,date.date.month,date.date.day)
        // console.log(moment(date.date.marker).format("DD"))
        return " "
    },

    slotLabelDidMount: function (date) {
        const d = moment(date.date).format("DD")
        const day = moment(date.date).format("ddd")
        if (moment(date.date).format("yyyy-MM-DD") == working_day.date_working_day) {
            date.el.getElementsByTagName("a")[0].innerHTML = "<div class='current_day line-height-15 border-round-lg px-3 py-2'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(date.date).format("MMM") + "</span></div>"
        } else {
            if (day == "Sat" || day == "Sun") {
                date.el.getElementsByTagName("a")[0].innerHTML = "<div class='line-height-15  border-round-lg px-3 py-2' style='color:red;'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(date.date).format("MMM") + "</span></div>"
            }
            else {
                date.el.getElementsByTagName("a")[0].innerHTML = "<div class='line-height-15  border-round-lg px-3 py-2'><span class='font-light'>" + day + "</span><br/>" + d + "<br/><span class='font-light'>" + moment(date.date).format("MMM") + "</span></div>"
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
        if (data.type=="stay"){
            showReservationStayDetail(data.reservation_stay)
        }else {
            alert("Open dialog of " + data.type )
        }
        
    }),
    eventMouseEnter: (($event) => {
        eventInfo.data = $event.event;
        // showTooltip.value = true; 
    }),
    eventMouseLeave: (() => {
        showTooltip.value = !showTooltip.value;
        eventInfo.data = null;
    }),
    eventDrop: function (info) {
        if (!confirm("Are you sure about this change?")) {
            info.revert();
        }
    }

})

function getRoomChartlocationStorage() {
    if (localStorage.getItem('reservation_chart')) {
        return JSON.parse(localStorage.getItem('reservation_chart'))
    } else {
        let _date = moment(working_day.date_working_day).add(-1, 'days').format("yyyy-MM-DD")
        const dataStorage = {
            view: 'room_type',
            peroid: 'today',
            date: _date
        }
        localStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
        if (localStorage.getItem('reservation_chart'))
            return JSON.parse(localStorage.getItem('reservation_chart'))
        return ''
    }
}
function setRoomChartlocationStorage(date='',view='',peroid='') {
    // set room chart localstorage
    
    let dataStorage = getRoomChartlocationStorage()
    if(date != '')
        dataStorage.date =  date
    if(view != '')
        dataStorage.view = view
    if(peroid != '')
        dataStorage.peroid = peroid
    console.log(dataStorage)
    onUpdateFilterDate(dataStorage.date)
    localStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
    return dataStorage

}

function onInitialDate(date = '', refresh = false) {
    if (date) {
        const storage = setRoomChartlocationStorage(date, '','')
        
        return storage.date
    }
    else {
        const roomChartStorage = getRoomChartlocationStorage()
        const view_date = roomChartStorage.date
        if (refresh || !view_date) {
            const date_working_day = moment(working_day.date_working_day).add(-1, 'days').format("yyyy-MM-DD")
            setRoomChartlocationStorage(date_working_day)
            return date_working_day
        } else {
            return view_date
        }
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
 
        const dialogRef = dialog.open(NewReservation, {
            data: {
                arrival_date: event.start,
                departure_date: event.end,
                room_type_id:event.resource._resource.extendedProps.room_type_id,
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
    setRoomChartlocationStorage('',filter.view_type,'')
    const cal = fullCalendar.value.getApi()
    cal.setOption('resourceAreaColumns', resourceColumn())
    cal.refetchResources()
}
function onFilter(key, refresh = false, filter_date = '') {
    filter.peroid = key
    const cal = fullCalendar.value.getApi()
    const visibleRange = cal.currentData.options.visibleRange
    const initialDate = cal.currentData.options.initialDate
    if (visibleRange.start == undefined || refresh == true || filter_date != '') {
        if (filter_date != '') {
            visibleRange.start = moment(filter_date).format("yyyy-MM-DD")
            onInitialDate(visibleRange.start)
        }
        else {
            if(refresh){
                visibleRange.start = moment(working_day.date_working_day).add(-1, 'days').format("yyyy-MM-DD")
            }
            else{
                visibleRange.start = moment(initialDate).format("yyyy-MM-DD")
            }
            
            onInitialDate(visibleRange.start)
        }
    }

    if (key == 'today') {
        cal.changeView('resourceTimeline', { start: moment(visibleRange.start).format("yyyy-MM-DD"), end: moment(visibleRange.start).add(1, 'months').format("yyyy-MM-DD") });
    }
    else if (key == 'week') {
        cal.changeView('resourceTimeline', { start: moment(visibleRange.start).format("yyyy-MM-DD"), end: moment(visibleRange.start).add(7, 'days').format("yyyy-MM-DD") });
    }
    else if (key == '14_days') {
        cal.changeView('resourceTimeline', { start: moment(visibleRange.start).format("yyyy-MM-DD"), end: moment(visibleRange.start).add(14, 'days').format("yyyy-MM-DD") });
    }
    else if (key == 'month') {
        cal.changeView('resourceTimeline', { start: moment(visibleRange.start).format("yyyy-MM-DD"), end: moment(visibleRange.start).add(1, 'months').format("yyyy-MM-DD") });
    }
}
function onFilterToday() {
    onFilter(filter.peroid, true)
}
function onFilterDate(event) {
    
    const filter_date = moment(event).add(-1, 'days')
    onFilter(filter.peroid, false, filter_date)
}
function onPrevNext(key) {
    const cal = fullCalendar.value.getApi()
    const visibleRange = cal.currentData.options.visibleRange
    const dateIncrement = cal.currentData.options.dateIncrement
    if (visibleRange.start == undefined || visibleRange.end == undefined) {
        const initialDate = cal.currentData.options.initialDate
        visibleRange.start = moment(initialDate).format("yyyy-MM-DD")
        visibleRange.end = moment(initialDate).add(1, 'months').format("yyyy-MM-DD")
        onUpdateFilterDate(visibleRange.start)

    }
    if (key == 'prev') {
        const startDate = moment(visibleRange.start).add((dateIncrement.days * -1), 'days').format("yyyy-MM-DD")
        const endDate = moment(visibleRange.end).add((dateIncrement.days * -1), 'days').format("yyyy-MM-DD")
        onInitialDate(startDate)
        cal.changeView('resourceTimeline', { start: startDate, end: endDate });
    }
    else if (key == 'next') {
        const startDate = moment(visibleRange.start).add((dateIncrement.days), 'days').format("yyyy-MM-DD")
        const endDate = moment(visibleRange.end).add((dateIncrement.days), 'days').format("yyyy-MM-DD")
        onInitialDate(startDate)
        cal.changeView('resourceTimeline', { start: startDate, end: endDate });
    }
}

const onRefresh = () => {
    const cal = fullCalendar.value.getApi()
    cal.refetchEvents()
    // cal.setOption({now:"2023-05-18"})
}
//   function onOrder(){
//     const cal = fullCalendar.value.getApi()
//     cal.setOption('resourceOrder', '-sort_order')
//   }
function showReservationStayDetail(name) {

    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Stay Detail',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true
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
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {

            }
        }
    });
}

onMounted(() => {

    // call.get("edoor.api.frontdesk.get_working_day", {
    //       property: property.name
    //   }).then((result) => {

    //     working_day.value = result.message
    //     fullCalendar.value.getApi().gotoDate(working_day.value.date_working_day);
    //     //fullCalendar.value.getApi().setOption("now",working_day.value.date_working_day);


    //   })
    const initialDate = onInitialDate()
    onUpdateFilterDate(initialDate)
})
function onUpdateFilterDate(date) {
    filter.date = moment(date).add(1, 'days').toDate()
}
onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
    socket.disconnect()
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
</style>