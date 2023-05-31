<template lang="">
    <div>
        <ComHeader>
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Frontdesk</div>
                        <div class="ml-8">May 30 - Jun 16, 2023</div>
                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 justify-content-end">
                    <NewFITReservationButton/>
                    <Button label="New group booking" class="btn-date__tt btn-inner-set-icon border-none">
                        <img class="mr-2" :src="iconEdoorAddGroupBooking">New group booking
                    </Button>
                </div>
            </template>
        </ComHeader>
        <div class="flex justify-between mb-3">
            <ComRoomChartFilterSelect>
                <template #date>
                    <Calendar panelClass="room-chart-celendar" v-model="filter.date" dateFormat="dd-mm-yy" @date-select="onFilterDate" showButtonBar showIcon />
                </template>
            </ComRoomChartFilterSelect>
            <div>
                <ComRoomChartFilter :viewType="filter.view_type" @onView="onView" @onPrevNext="onPrevNext($event)" @onToday="onFilterToday()" @onFilter="onFilter($event)"/>
            </div>
        </div>
        <div style="max-width: 100%;">
            <div>  
                <div :class="showSummary ? 'flex gap-2' : ''">
                    <div v-if="showSummary" class="relative" style="width:250px">
                        <div class="fixed" style="width:250px">
                            <div class="w-full">
                                <ComPanel title="Guest Today" class="mb-3 pb-3">
                                    <div>
                                        <ComDonutFrontdesk/>
                                    </div>
                                    <div class="mt-3">
                                        <ComTodaySummary/>
                                    </div>
                                </ComPanel>
                                <ComPanel title="Room Status" class="pb-3">
                                    <ComHousekeepingStatus/>
                                </ComPanel>
                            </div> 
                        </div>
                    </div>
                    <div class="relative" aria-haspopup="true" aria-controls="overlay_menu" :class="showSummary ? 'chart-show-summary':''">
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
import ComTodaySummary from './components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from './components/ComRoomChartFilterSelect.vue'
import ComDonutFrontdesk from '@/views/frontdesk/components/ComDonutFrontdesk.vue'

const socket = inject("$socket");
const frappe = inject('$frappe')
const call = frappe.call();
const moment = inject('$moment')
const filter = reactive({
    peroid: 'today',
    view_type: '',
    date: ''
})
const fullCalendar = ref(null)

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
            room_type: "room_type",
            building: "building"
        }).then((result) => {
            successCallback(result.message)
        })
            .catch((error) => {
                alert("load data fiale")
            });
    },
    eventAllow: function (dropInfo, draggedEvent) {
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
        if (data.type == "stay") {
            showReservationStayDetail(data.reservation_stay)
        } else {
            alert("Open dialog of " + data.type)
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
        const result = JSON.parse(localStorage.getItem('reservation_chart'))
        filter.date = moment(result.start_date).add(1, 'days').format("yyyy-MM-DD")
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

        const dialogRef = dialog.open(NewReservation, {
            data: {
                arrival_date: event.start,
                departure_date: event.end,
                room_type_id: event.resource._resource.extendedProps.room_type_id,
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
        visibleRange.end = moment(currentViewChart.start_date).add(7, 'days').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', '')
        cal.changeView('resourceTimeline', { start: setViewChart.start_date, end: setViewChart.end_date });
    }
    else if (key == '14_days') {
        const currentViewChart = setRoomChartlocationStorage('', '', '', key)
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(14, 'days').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', '')
        cal.changeView('resourceTimeline', { start: setViewChart.start_date, end: setViewChart.end_date });
    }
    else {
        var currentViewChart = getRoomChartlocationStorage()
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(1, 'months').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', '')
        cal.changeView('resourceTimeline', { start: setViewChart.start_date, end: setViewChart.end_date });
    }
}

function onFilterDate(event) {

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
    onInitialDate()

})
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

.chart-show-summary {
    width: calc(100% - 250px);
}
</style>