<template lang=""> 
    <div>
        <ComHeader isRefresh @onRefresh="onRefresh()">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Room Inventory</div> 
                        <div class="ml-8 header-title text-2xl" v-if="moment.utc(filter.date).format('yyyy') != moment.utc(filter.end_date).format('yyyy')">{{moment.utc(filter.date).format('DD MMM, yyyy')}} - {{moment.utc(filter.end_date).add(-1,"days").format('DD MMM, yyyy')}}</div>
                        <div class="ml-8 header-title text-2xl" v-else>{{moment.utc(filter.date).format('DD MMM')}} - {{moment.utc(filter.end_date).add(-1,"days").format('DD MMM, yyyy')}}</div>
                    </div>
                </div>
            </template>
            <template #end> 
                <div class="flex gap-2 justify-content-end">
                    <Button label='Uncomming Note' :badge="totalNotes" badgeClass="bg-white text-600 badge-rs" class="bg-yellow-500 border-none" @click="showNote=!showNote">
                      <ComIcon icon="iconNoteWhite" class="me-2" height="18px" /> Uncomming Note <Badge
                      style="font-weight: 600 !important;" class="badge-rs bg-white text-500" :value="totalNotes"
                      severity="warning">
                    </Badge>
                    </Button>
                    <NewFITReservationButton/>
                    <NewGITReservationButton/>
                
                </div>
            </template>
        </ComHeader>
        <div class="flex justify-between mb-3 filter-calen-fro sticky_search_bar" id="front_desk_search_sticky"> 
            <div class="flex gap-2">
                <div>
                    <Calendar :selectOtherMonths="true" class="w-full" :modelValue="filter.date" @date-select="onFilterDate" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
                </div>
                
               
             
            </div>
            <div>
                <ComRoomChartFilter :viewType="filter.view_type" @onView="onView" @onPrevNext="onPrevNext($event)" @onToday="onFilterToday()" @onChangePeriod="onChangePeriod($event)"/>
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

                        <RoomInventoryChart :data="events"/>

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
import { h, ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted, watch, getApi, getCount, provide, computed, getDocList } from '@/plugin'
import '@fullcalendar/core/vdom' // solves problem with Vite
import { useTippy } from 'vue-tippy'
import interactionPlugin from '@fullcalendar/interaction'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';
import ComCalendarEventTooltip from '@/views/frontdesk/components/ComCalendarEventTooltip.vue'
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComConfirmChangeStay from "@/views/frontdesk/components/ComConfirmChangeStay.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import ComRoomChartFilter from './components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from './components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from './components/ComRoomChartFilterSelect.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'
import ComCalendarEvent from '@/views/frontdesk/components/ComCalendarEvent.vue'
import ComCheckRoomConfligAndOverBooking from '@/views/frontdesk/components/ComCheckRoomConfligAndOverBooking.vue'
import RoomInventoryChart from '@/views/frontdesk/components/RoomInventoryChart.vue'
import FullCalendar from '@fullcalendar/vue3'


const resources = ref([])
const events = ref([])
const moment = inject('$moment')
const filter = ref({
    view_type: 'room',
    date: moment().toDate(),
    end_date: '',
    period: "15_days"
})

const showAdvanceSearch = ref()

const fullCalendar = ref(null)
const gv = inject("$gv")
const toast = useToast();
const dialog = useDialog();
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")

const keyword = ref({
    keyword: '',
    room_number: ''
})
const showSummary = ref(true)
const showNote = ref(false)
const loading = ref(false)
const totalNotes = ref(0)

let advanceFilter = ref({
    room_type: "",
    room_number: "",
    room_type_group: "",
    building: "",
    floor: ""
})

 

provide('get_count_note', {
    getTotalNote
})



if (edoorShowFrontdeskSummary) {
    showSummary.value = edoorShowFrontdeskSummary == "1";
}

let roomChartResourceFilter = reactive({
    property: window.property_name,
    view_type: filter.value.view_type // room_type = true or room = false
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
    nowIndicator: false,
    stickyHeaderDates: false,
    headerToolbar: false,
    nowIndicator: true,
    resourceAreaColumns: resourceColumn(),
    now: working_day.date_working_day + " 12:00:00",
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
        info.el.addEventListener('click', function () {
            window.postMessage({ "action": "view_product_data_sumary_by_date", date: moment(info.date).format("YYYY-MM-DD") })
        })
        info.el.style.cursor="pointer"

    },
 
 
    eventClick: ((info) => {
 

        const data = info.event._def.extendedProps;
        info.event._def.date = info.event.start;
        window.postMessage(info.event._def, '*')
    }),

    eventMouseEnter: (($event)=>{
       
        if (loading.value) {
            return
        }
        const event = $event.event._def
 
        const elements    = document.querySelectorAll('.' + $event.event._def.extendedProps.reservation_stay);
        elements.forEach(e=>{
            e.parentNode.parentNode.parentNode.style.boxShadow = '2px 2px 5px 1px rgba(0, 0, 0, 0.8)';
        })
        if (!$event.el.getAttribute("has_tippy") && $event.event._def.extendedProps.type=="room_inventory_room_type_summary") {
            $event.el.setAttribute("has_tippy", "yes");
            const { tippyInstance } = useTippy($event.el, {
                content: h(ComCalendarEventTooltip, { event: event }),
            })
        }
    }),

    eventMouseLeave:(($event) => {
        const elements    = document.querySelectorAll('.' + $event.event._def.extendedProps.reservation_stay);
        elements.forEach(e=>{
            e.parentNode.parentNode.parentNode.style.boxShadow='';
        })
    }),
    
  
})

 

function setRoomChartlocationStorage() {
    sessionStorage.setItem('reservation_chart', JSON.stringify({
        "period": filter.value.period || "15_days",
        "start_date": moment.utc(filter.value.date).format("YYYY-MM-DD"),
        "view": filter.value.view_type || "room"
    }))
}

function onFilterToday() {
    if (gv.loading) {
        return
    }
    const date = moment.utc(working_day.date_working_day)
    calendarOptions.visibleRange = { start: date.toDate(), end: getEndDate(date, filter.value.period) }
    getEvents()
    removeDOM()
}

function onChangePeriod(period) {
    if (gv.loading) {
        return
    }
    const cal = fullCalendar.value.getApi()
    filter.value.period = period
    calendarOptions.visibleRange = { start: cal.view.currentStart, end: getEndDate(cal.view.currentStart, filter.value.period) }
    getEvents()
}

function onFilterDate(event) {
    if (gv.loading) {
        return
    }
    const date = moment.utc(moment(event).format("YYYY-MM-DD")).toDate()
    filter.value.date = date
    calendarOptions.visibleRange = { start: date, end: getEndDate(date, filter.value.period) };
    getEvents()
}

function onPrevNext(key) {
    if (gv.loading) {
        return
    }
    const cal = fullCalendar.value.getApi()
    let visible_date = {}
    if (key == 'prev') {
        visible_date = { start: moment(cal.view.currentStart).add(calendarOptions.dateIncrement.days * -1, "days").toDate(), end: moment(cal.view.currentEnd).add(calendarOptions.dateIncrement.days * -1, "days").toDate() }
    } else {
        visible_date = { start: moment(cal.view.currentStart).add(calendarOptions.dateIncrement.days, "days").toDate(), end: moment(cal.view.currentEnd).add(calendarOptions.dateIncrement.days, "days").toDate() };
    }
    removeDOM()
    calendarOptions.visibleRange = visible_date;
    filter.value.date = visible_date.start
    filter.value.end_date = visible_date.end


    getEvents()

 
}

 
function resourceColumn() {
    return [
            {
                labelText: 'xxx',
                headerContent: 'Room Type'
            },
            {
                width: 60,
                cellContent: function (arg) {
                    const el = arg.resource._context.calendarApi.el
                         el.innerHTML = `<div id='resource_total_${arg.resource._resource.id}' class="cell-status text-center">${ arg.resource.extendedProps.total_room || ""}</div>`;
                    
                     
                   
               
                    
                    let dom = [el.innerHTML]
                    return { html: dom }
                }
            }
        ]
    
}


function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_show_frontdesk_summary", showSummary.value ? "1" : "0")
    onRefresh()
 
}

function onView() {
    filter.value.view_type = filter.value.view_type == 'room_type' ? 'room' : 'room_type'
    roomChartResourceFilter.view_type = filter.value.view_type
    getEvents()
}

 
const onRefresh = debouncer((show_loading = true) => {
    
    getResources()
    getTotalNote()
}, 500);

  
 

function getTotalNote() {
    getCount('Frontdesk Note', [["note_date", ">=", working_day.date_working_day], ['property', '=', window.property_name]]).then((docs) => {
        totalNotes.value = docs
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

 
function getResources() {
    getApi('frontdesk.get_room_inventory_resource', { property: window.property_name }).then((result) => {
        resources.value = result.message
        getEvents()
    })
}

function getEvents() {
   
    gv.loading = true
    const cal = fullCalendar.value.getApi()
    
    getApi('frontdesk.get_room_inventory_calendar_event', {
        start: moment(cal.view.currentStart).format("YYYY-MM-DD"),
        end: moment(cal.view.currentEnd).add(-1,"days").format("YYYY-MM-DD"),
        property: window.property_name
    }).then((result) => {
        removeDOM()
        //1 create room type event
       events.value = []
       const total_rooms = resources.value.reduce((n, d) => n + (d.total_room || 0), 0)
        resources.value.filter(x=>x.id !="dummy").forEach(r => {
            
            let current_date = cal.view.currentStart;
            const days = moment( cal.view.currentEnd).diff(moment( cal.view.currentStart), 'days');
           
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
            

            while (current_date < cal.view.currentEnd) {
                let title = ""
                
                let event = {
                    color:"rgb(255 255 255)",
                    borderColor:"rgb(233 233 233 / 30%)",
                    textcolor:"black",
                    resourceId: r.id,
                    start: moment(current_date).format("YYYY-MM-DD") + "T00:00:00.000000",
                    end: moment(current_date).format("YYYY-MM-DD") + "T23:59:00.000000",
                    type:"property_summary"
                }
                if (r.id == "vacant_room") {
                    event.vacant_room = total_rooms -  result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.total || 0), 0)
                    event.title = event.vacant_room 
                    if ((event.vacant_room || 0)<0){
                        event.color="red"
                    }else {
                        event.color="#fd952c"
                    }
                    
                    event.textcolor="white"
                    
                } 
                else if (r.id == "out_of_order") {
                    event.title = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.block || 0), 0)
                    event.color="black"
                    event.textcolor="white"
                    
                } else if (r.id == "occupany") {
                    if (window.setting.calculate_room_occupancy_include_room_block=0){
                        const room_block = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.block || 0), 0)
                        event.occupancy = ( result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.total || 0), 0)/ (total_rooms - room_block)    * 100).toFixed(2)   
                    }else {
                        event.occupancy = ( result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.total || 0), 0)/ total_rooms  * 100).toFixed(2) 
                    }

                    event.title = event.occupancy + "%"
                    
                    event.color="green"
                    event.textcolor="white"
                    
                } else if (r.id == "arrival") {

                    event.arrival = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.arrival || 0), 0) || 0
                    event.title = event.arrival

                    event.color="#F2CB38"
                    event.textcolor="white"
                    
                } else if (r.id == "stay_over") {
                    event.stay_over = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.stay_over || 0), 0) || 0
                    event.title = event.stay_over
                    event.color="#F2CB38"
                    event.textcolor="white"
                    
                } else if (r.id == "departure") {
                    event.departure = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.departure || 0), 0) || 0
                    event.title = event.departure

                    event.color="#F2CB38"
                    event.textcolor="red"
                    
                } else if (r.id == "pax") {
                    event.title = result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.adult || 0), 0)
                    event.title = event.title + " | " +  result.message.room_occupy.filter(x => x.date == moment(current_date).format("YYYY-MM-DD")).reduce((n, d) => n + (d.child || 0), 0)
                    event.color="#76E2E8"
                    event.textcolor="white"
                    
                } else {
                    const current_date_occupy = result.message.room_occupy.find(x => x.room_type_id == r.id && x.date == moment(current_date).format("YYYY-MM-DD"))
                    event.title = r.total_room - (current_date_occupy?.total || 0)  
                    if((current_date_occupy?.unassign_room || 0)!=0){
                        event.title = event.title + " | "  +  (current_date_occupy?.unassign_room || 0)
                    }
                  
                  
                    event.type="room_inventory_room_type_summary"
                    event.current_date=current_date
                    event.room_available=r.total_room - (current_date_occupy?.total || 0)  
                    event.unassign_room=(current_date_occupy?.unassign_room || 0)
                    event.room_type = r.title //room type from resource
                    if(r.total_room - (current_date_occupy?.total || 0)  <0){
                        event.color="red"
                        event.textcolor ="white"
                    }
                  
                }
                

                events.value.push(event)
                current_date.setDate(current_date.getDate() + 1);
            }
        });

        //show summary to resource
        setTimeout(() => {
            document.querySelector("#resource_total_vacant_room").textContent =events.value.reduce((n, d) => n + (d.room_available || 0), 0)
            document.querySelector("#resource_total_arrival").textContent = result.message.room_occupy.reduce((n, d) => n + (d.arrival || 0), 0)
            document.querySelector("#resource_total_stay_over").textContent = result.message.room_occupy.reduce((n, d) => n + (d.stay_over || 0), 0)
            document.querySelector("#resource_total_departure").textContent = result.message.room_occupy.reduce((n, d) => n + (d.departure || 0), 0)
            document.querySelector("#resource_total_out_of_order").textContent = result.message.room_occupy.reduce((n, d) => n + (d.block || 0), 0)
            document.querySelector("#resource_total_pax").textContent = result.message.room_occupy.reduce((n, d) => n + (d.adult || 0), 0) + "/" +  result.message.room_occupy.reduce((n, d) => n + (d.child || 0), 0)
            
            const toatlRoomNight = moment(cal.view.currentEnd).diff(moment(cal.view.currentStart), "days") * total_rooms
            if (window.setting.calculate_room_occupancy_include_room_block=0){
                    const room_block = result.message.room_occupy.reduce((n, d) => n + (d.block || 0), 0)
                    document.querySelector("#resource_total_occupany").textContent =  (result.message.room_occupy.reduce((n, d) => n + (d.total || 0), 0)/ (toatlRoomNight - room_block)    * 100).toFixed(2) + "%"

                }else {
                    document.querySelector("#resource_total_occupany").textContent =  (result.message.room_occupy.reduce((n, d) => n + (d.total || 0), 0)/ (toatlRoomNight)    * 100).toFixed(2) + "%"
           
                }
            

           
            
           
        }, 100);

    



        gv.loading = false

    })
        .catch((error) => {
            console.log(error)
            toast.add({ severity: 'warn', summary: 'Info', detail: "Loading data fail. Please try again", life: 3000 })
            gv.loading = false
        });
}



 
const handleScroll = (event) => {
    const sticky = document.getElementById("front_desk_search_sticky");
    if (document.body.scrollTop > 50) {
        sticky.classList.add("front_desk_sicky_bar");
    } else {
        sticky.classList.remove("front_desk_sicky_bar");
    }
};

onMounted(() => {

    window.socket.on("RoomInventory", (arg) => {
        if (arg == window.property_name) {
            getResources(false)
        }
    })
    const state = JSON.parse(sessionStorage.getItem("reservation_chart"))
    if (state) {
        filter.value.view_type = state.view || "room"
        filter.value.date = moment.utc(state.start_date).toDate()
        filter.value.end_date = moment.utc(state.end_date).toDate()
        filter.value.period = state.period || "15_days"
    } else {
        filter.value.date = moment.utc(working_day.date_working_day).add(-1, "days").toDate()
    }
    roomChartResourceFilter.view_type = filter.value.view_type
    calendarOptions.visibleRange = { start: filter.value.date, end: getEndDate(filter.value.date, filter.value.period) }

    getResources()

    document.body.addEventListener('scroll', handleScroll);

})
 

function getEndDate(start, period) {
    let date = moment()
    if (period == "week") {
        date = moment(start).add(7, "days").toDate()
    } else if (period == "15_days") {
        date = moment(start).add(15, "days").toDate()
    } else {
        date = moment(start).add(1, "months").toDate()
    }
    filter.value.end_date = date
    return date
}

onUnmounted(() => {
    window.socket.off("RoomInventory");
    document.body.removeEventListener('scroll', handleScroll);
})
 

//Remove tippy tooltips when room chart DOM removed
const removeDOM = () => {
    document.querySelectorAll('[id^="tippy-"]').forEach(function (element) {
        element.remove();
    });
}
</script>
<style>
.fc-content td:hover{
        background: #DBDBDB; 
        opacity: 0.4;
    }
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

div.sticky_search_bar {
    position: -webkit-sticky;
    position: sticky;
    top: 62px;
    background-color: #eff2f7;
    z-index: 4;
}

div.front_desk_sicky_bar {
    padding: 10px 0;
}

.fc-timeline-lane .fc-resource {
    background: red !important;
}</style>