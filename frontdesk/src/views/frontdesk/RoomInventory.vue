<template lang="">
    <div>
        <ComHeader isRefresh @onRefresh="onRefresh()">
        
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Room Inventory</div>
                        <div class="ml-8 header-title text-2xl" v-if="moment(filter.date).format('yyyy') != moment(filter.end_date).format('yyyy')">{{moment(filter.date).format('MMM DD, yyyy')}} - {{moment(filter.end_date).format('MMM DD, yyyy')}}</div>
                        <div class="ml-8 header-title text-2xl" v-else>{{moment(filter.date).format('MMM DD')}} - {{moment(filter.end_date).format('MMM DD, yyyy')}}</div>
                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 justify-content-end">
                    <Button label='Uncomming Note' :badge="totalNotes" badgeClass="bg-white text-600 badge-rs" class="bg-yellow-500 border-none" @click="showNote=!showNote"/>
                    <NewFITReservationButton/>
                    <NewGITReservationButton/>
                </div>
            </template>
        </ComHeader>
        <div class="flex justify-end mb-3 filter-calen-fro sticky_search_bar_room" id="room_search_sticky" >
            <div>
                <ComRoomChartFilter :viewType="filter.view_type"   @onPrevNext="onPrevNext($event)" @onToday="onFilterToday()" @onFilter="onFilter($event)"/>
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
                    </div>
                    <div class="relative" aria-haspopup="true" aria-controls="overlay_menu" :class="showSummary ? 'chart-show-summary':''">
                       
                        <Sidebar v-model:visible="showNote" class="top-20 -mt-1 w-3" style="padding-bottom: 82px;" position="right">
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
                        <tippy :content="'sdf'">
                      
                        </tippy>
                        
                        <FullCalendar ref="fullCalendar" :options="calendarOptions" class="h-full">
                            <template v-slot:eventContent="{event}"> 
                                    <div class="group relative h-full p-1 event-room-type-class" :class="event.extendedProps.type" style="height: 36px">
                                        <div class="flex justify-content-center">
                                            <div :style="{color:event.extendedProps.textcolor}" class="">
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
  </template>
<script setup>
import { ref, reactive, inject, onUnmounted, useToast, onMounted, watch, getApi, getCount, provide } from '@/plugin'
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
import ComRoomChartFilter from './components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from './components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from './components/ComRoomChartFilterSelect.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'

// import { useTippy } from 'vue-tippy'

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

const fullCalendar = ref(null)
const gv = inject("$gv")

const toast = useToast();
// const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")
const initialDate = onInitialDate()
let fullcalendarInitialDate = ref(initialDate.start)
const resources = ref([])
const events = ref([])


const showSummary = ref(true)
const showNote = ref(false)
const totalNotes = ref(0)
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




window.socket.on("RefresheDoorDashboard", (arg) => {

    if (arg == property.name) {
        onRefresh()
        toast.add({ severity: 'info', summary: 'Info', detail: "Reservation updated", life: 3000 })

    }
})


watch(() => filter.date, (newValue, oldValue) => {
    selectedDate.value = new Date(newValue)
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

    resourceLabelDidMount: function (info) {

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

 

    eventClick: ((info) => {

        const data = info.event._def.extendedProps;
        if (data.type == "stay") {
            showReservationStayDetail(data.reservation_stay)
        } else {
            info.event._def.date = info.event.start;
            alert("open list of " +   info.event.extendedProps.type )
            window.postMessage(info.event._def, '*')
        }

    }),
    eventMouseEnter: (($event) => {
        const event = $event.event._def


    }),


})

function getRoomChartlocationStorage() {
    if (sessionStorage.getItem('reservation_chart')) {
        const result = JSON.parse(sessionStorage.getItem('reservation_chart'))
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

        sessionStorage.setItem('reservation_chart', JSON.stringify(dataStorage))
        if (sessionStorage.getItem('reservation_chart')) {
            const result = JSON.parse(sessionStorage.getItem('reservation_chart'))
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



    sessionStorage.setItem('reservation_chart', JSON.stringify(dataStorage))

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

function resourceColumn() {

    return [
        {
            labelText: 'xxx',
            headerContent: 'Room Type'
        },
        {
            field: 'total_room',
            headerContent: 'Rooms',
            width: 60,
            cellContent: function (arg) {
                const el = arg.resource._context.calendarApi.el
                const item = arg.resource.extendedProps

                if (arg.fieldValue) {
                    el.innerHTML = "<div style='text-align:center;display:none'>" + arg.fieldValue + "</div>"
                }
                else {
                    el.innerHTML = ''
                }

                let dom = [el.innerHTML]
                return { html: dom }
            }
        },
        {
            field: 'total_room_night',
            headerContent: 'Total Room Night',
            width: 60,
            cellContent: function (arg) {
                const el = arg.resource._context.calendarApi.el
                const item = arg.resource.extendedProps

                if (arg.fieldValue) {
                    el.innerHTML = "<div style='text-align:center;display:none'>" + arg.fieldValue + "</div>"
                }
                else {
                    el.innerHTML = ''
                }

                let dom = [el.innerHTML]
                return { html: dom }
            }
        }
    ]

}


function onShowSummary() {
    onRefresh()
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_show_frontdesk_summary", showSummary.value ? "1" : "0")
 
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
        
    }
    else {
        
        var currentViewChart = getRoomChartlocationStorage()
        visibleRange.start = moment(currentViewChart.start_date).format("yyyy-MM-DD")
        visibleRange.end = moment(currentViewChart.start_date).add(1, 'months').subtract(1, 'days').format("yyyy-MM-DD")
        const setViewChart = setRoomChartlocationStorage(visibleRange.start, visibleRange.end, '', key)
        cal.changeView('resourceTimeline', { start: moment(setViewChart.start_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss'), end: moment(setViewChart.end_date).add(12, 'hours').format('YYYY-MM-DD hh:mm:ss') });
        
    }
    getEvents()

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
   getEvents()
    getTotalNote()

}
  



function getTotalNote() {
    getCount('Frontdesk Note', [["note_date", ">=", working_day.date_working_day]]).then((docs) => {
        totalNotes.value = docs
    })
}
function getResources() {
    getApi('frontdesk.get_room_inventory_resource', { property: property.name }).then((result) => {
        resources.value = result.message
        getEvents()
    })
}
function getEvents() {
    const cal = fullCalendar.value.getApi()
    
    call.get('edoor.api.frontdesk.get_room_inventory_calendar_event', {
        start: moment(cal.view.currentStart).format("YYYY-MM-DD"),
        end: moment(cal.view.currentEnd).format("YYYY-MM-DD"),
        property: property.name
    }).then((result) => {
        //1 create room type event
       events.value = []

        resources.value.forEach(r => {
            let current_date = cal.view.currentStart;
            const days = moment( cal.view.currentEnd).diff(moment( cal.view.currentStart), 'days');
            const total_rooms = resources.value.reduce((n, d) => n + (d.total_room || 0), 0)
            if (r.id == "vacant_room"){
                r.total_room_night = (days * total_rooms) -  result.message.room_occupy.reduce((n, d) => n + (d.total || 0), 0)
            }else if (r.id == "occupany"){
                r.total_room_night = parseInt(result.message.room_occupy.reduce((n, d) => n + (d.total || 0), 0) / (total_rooms*days) * 100 )   + "%"
            } else if (r.id == "out_of_order"){
                r.total_room_night = result.message.room_occupy.reduce((n, d) => n + (d.block || 0), 0)
            }else if (r.id == "arrival_departure"){
                r.total_room_night = result.message.room_occupy.reduce((n, d) => n + (d.arrival || 0), 0) 
                r.total_room_night = r.total_room_night + "/" +  result.message.room_occupy.reduce((n, d) => n + (d.departure || 0), 0) 
            }else if (r.id == "pax"){
                r.total_room_night = result.message.room_occupy.reduce((n, d) => n + (d.adult || 0), 0) 
                r.total_room_night = r.total_room_night + "/" +  result.message.room_occupy.reduce((n, d) => n + (d.child || 0), 0) 
            }else {
                r.total_room_night = (days * r.total_room) -  result.message.room_occupy.filter(x=>x.room_type_id==r.id).reduce((n, d) => n + (d.total || 0), 0)
            }
            

            while (current_date <= cal.view.currentEnd) {
                let title = ""
                
                let color="#f7f7f7"
                let textcolor="black"
                let borderColor=""
                if (r.id == "vacant_room") {
                    title = total_rooms -  result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.total || 0), 0)
                    color="#fd952c"
                    textcolor="white"
                } 
                else if (r.id == "out_of_order") {
                    title = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.block || 0), 0)
                    color="black"
                    textcolor="white"
                } else if (r.id == "occupany") {
                    title = parseInt( result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.total || 0), 0)/ total_rooms  * 100) + "%"
                    color="green"
                    textcolor="white"
                } else if (r.id == "arrival_departure") {
                    title = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.arrival || 0), 0)
                    title = title + " | " +  result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.departure || 0), 0)
                    color="#F2CB38"
                    textcolor="white"
                } else if (r.id == "pax") {
                    title = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.adult || 0), 0)
                    title = title + " | " +  result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.child || 0), 0)
                    color="#76E2E8"
                    textcolor="white"
                } else {

                    title =  r.total_room - (result.message.room_occupy.find(x => x.room_type_id == r.id && x.date == moment(current_date).format("YYYY-MM-DD"))?.total || 0)
borderColor="rgb(0 185 26 / 30%)"
                }
                if (title < 0) {
                    color="red";
                    textcolor="white"
                    
                }
               
                events.value.push(
                        {
                            resourceId: r.id,
                            start: moment(current_date).format("YYYY-MM-DD") + "T00:00:00.000000",
                            end: moment(current_date).format("YYYY-MM-DD") + "T23:59:00.000000",
                            title: title,
                            color: color,
                            textcolor:textcolor ?? 'white' ,
                            type: r.id ,
                            borderColor:borderColor
                        }
                    )
                current_date.setDate(current_date.getDate() + 1);
            }
        });





    })
        .catch((error) => {
            console.log(error)
            toast.add({ severity: 'warn', summary: 'Info', detail: "Loading data fail. Please try again", life: 3000 })
            gv.loading = false
        });
}
const handleScroll = (event) => {
    const sticky = document.getElementById("room_search_sticky");
 
    if(document.body.scrollTop > 50){
        sticky.classList.add("front_desk_sicky_bar");
    }else{
        sticky.classList.remove("front_desk_sicky_bar");
    }
};
onMounted(() => {

    onInitialDate()

    getResources()

    if (!selectedDate.value) {
        const currentViewChart = JSON.parse(sessionStorage.getItem('reservation_chart'))
        selectedDate.value = new Date(moment(currentViewChart.start_date).add(1, 'days'))
    }
    getTotalNote()
    document.body.addEventListener('scroll', handleScroll);
})

onUnmounted(() => {
    window.socket.off("RefresheDoorDashboard");
    document.body.removeEventListener('scroll', handleScroll);
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