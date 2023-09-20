<template lang=""> 
    <div>
        <ComHeader isRefresh @onRefresh="onRefresh()">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center">
                        <i @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer"></i>
                        <div @click="onRefresh()" class="text-2xl ml-4">Frontdesk</div> 
                        
                        <div class="ml-8 header-title text-2xl" v-if="moment.utc(filter.date).format('yyyy') != moment.utc(filter.end_date).format('yyyy')">{{moment.utc(filter.date).format('MMM DD, yyyy')}} - {{moment.utc(filter.end_date).format('MMM DD, yyyy')}}</div>
                        <div class="ml-8 header-title text-2xl" v-else>{{moment.utc(filter.date).format('MMM DD')}} - {{moment.utc(filter.end_date).format('MMM DD, yyyy')}}</div>
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
                <div>
                    <span class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText class="btn-set__h w-full" v-model="keyword.room_number" placeholder="Search Rooms" v-debounce="onSearchRoom"/>
                    </span>
                </div>
                <div>
                    <span class="p-input-icon-left w-full">
                        <i class="pi pi-search" />
                        <InputText class="btn-set__h w-full"  v-model="keyword.keyword" placeholder="Search" v-debounce="onSearch"/>
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
                     
                        <FullCalendar ref="fullCalendar" :options="calendarOptions" class="h-full">
                            <template v-slot:eventContent="{event}"> 
                                    <div class="group relative h-full p-1" :class="event.extendedProps.type" style="height: 36px">
                                        <div :class="event.extendedProps.type=='room_type_event' ? 'flex justify-content-center XXX' : 'flex'">
                                            <span class="ml-1 display-block stay-identify-position" :style="{backgroundColor:event.extendedProps.reservation_color}" v-if="event.extendedProps.reservation_color">
                                                <!-- GIT/FIT Color -->
                                            </span>                                        
                                            <span class="wrp-statu-icon">
                                                <span v-if="event.extendedProps.is_master" class="stay-bar-status mr-1">
                                                    <ComIcon style="height: 12px;" icon="iconCrown"/>
                                                </span>
                                                <span v-if="event.extendedProps.reservation_type=='GIT'" class="stay-bar-status mr-1">
                                                    <ComIcon style="height: 12px;" icon="iconUserGroup"/>
                                                </span>
                                            </span>
                                           
                                            <div class="guest-title">
                                                <template v-if="event.extendedProps.type=='room_type_event'">
                                                    <span :style="event.extendedProps.room_available < 0 ? 'color:#FFF' : 'color:#000'">{{event.extendedProps.room_available}}</span>
                                                    <span :style="event.extendedProps.room_available < 0 ? 'color:#ffb0b0' : 'color:#dee2e6'"> | </span>
                                                    <span :style="event.extendedProps.room_available < 0 ? 'color:#FFF' : 'color:#000'">{{event.extendedProps.unassign_room}}</span>
                                                </template>
                                                <template v-else>
                                                    {{event.title}}
                                                </template>
                                                
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
import {h, ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted, watch, getApi, getCount, provide, computed, getDocList } from '@/plugin'
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
import ComCalendarEventTooltip from '@/views/frontdesk/components/ComCalendarEventTooltip.vue'

import { useTippy } from 'vue-tippy'


const resources = ref([])
const events = ref([])
 

const socket = inject("$socket");

const disable_refresh_calendar_event = ref(false)
const moment = inject('$moment')
const filter = ref({
     
    view_type: 'room',
    date: moment().toDate(),
    end_date: '',
    period:"15_days"
})
const selectedDate = ref()
const showAdvanceSearch = ref()
 

const fullCalendar = ref(null)
const gv = inject("$gv")

const toast = useToast();
const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")
 
 
const keyword = ref({
    keyword:'',
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
const isFilter = computed(() => {
 
      if (keyword.value.keyword || gv.isNotEmpty(advanceFilter.value, 'property,view_type')) {
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
    view_type: filter.value.view_type // room_type = true or room = false
})

 



socket.on("RefresheDoorDashboard", (arg) => {
     if(!disable_refresh_calendar_event.value){
        if (arg == property.name) {
            onRefresh(false)
        }
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
    nowIndicator: false,
    stickyHeaderDates: true,
    headerToolbar: false,
    nowIndicator: true,
    resourceAreaColumns: resourceColumn(),
    now:working_day.date_working_day + " 12:00:00",
    resources: resources,
    events: events,
    eventAllow: function (dropInfo, draggedEvent) {
        if(draggedEvent._def.extendedProps.reservation_status=="In-house"){
            if(!moment(draggedEvent._def.extendedProps.arrival_date).isSame(moment(dropInfo.start).format("YYYY-MM-DD"))){
                return false
            }
        }
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

        info.el.addEventListener('click', function() {
           window.postMessage({"action":"view_product_data_sumary_by_date",date:moment(info.date).format("YYYY-MM-DD")})
           
        })
       
        

    },

    select: (($event) => {

        onSelectedDate($event)
    }),
    eventResize: (($event) => {
        disable_refresh_calendar_event.value = true
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
                //prevent reload calendar when we working on current window
                setTimeout(() => {
                    disable_refresh_calendar_event.value = false
                }, 3000);
            }
        });
    }),
    eventClick: ((info) => {
        // alert(info.event._def)
        
        const data = info.event._def.extendedProps;
        if (data.type == "stay") {
            showReservationStayDetail(data.reservation_stay)
        } else {
            info.event._def.date = info.event.start;
            
            // window.postMessage(info.event._def, '*')
            openRoomBlock(info.event._def)
        }

    }),
    eventMouseEnter: (($event) => {
        if(loading.value){
            return
        }
        const event = $event.event._def
        if (!$event.el.getAttribute("has_tippy")) {
            $event.el.setAttribute("has_tippy", "yes");
            const { tippyInstance } = useTippy($event.el, {
                content:  h(ComCalendarEventTooltip, { event: event }),
            })
        }

    }),
    eventDrop: function (info) {
        if (!confirm("Are you sure about this change?")) {
            info.revert();
        }
    },
   
})



const getEventDebounce = debouncer(() => {
   getEvent()

}, 500);

const openRoomBlock = debouncer((_data) => {
    window.postMessage(_data, '*')
}, 200);
 
function setRoomChartlocationStorage() {

    sessionStorage.setItem('reservation_chart', JSON.stringify({
        "period":filter.value.period || "15_days",
        "start_date":moment.utc(filter.value.date).format("YYYY-MM-DD"),
        "view": filter.value.view_type || "room" 
    }))
}

function onFilterToday() {
    if (gv.loading){
        return
    }
    const date =moment.utc(working_day.date_working_day)
   calendarOptions.visibleRange = {start:date.toDate(),end:getEndDate(date, filter.value.period)}
   
    getEvent() 
    removeDOM()
}

function onChangePeriod(period) {
    
    if (gv.loading){
        return
    }
    
    const cal = fullCalendar.value.getApi()
    filter.value.period = period
   calendarOptions.visibleRange = {start:cal.view.currentStart,end:getEndDate(cal.view.currentStart, filter.value.period)}
    
    getEvent()
}


function onFilterDate(event) {
 
 if (gv.loading){
     return
 }

const date = moment.utc( moment(event).format("YYYY-MM-DD")).toDate()
filter.value.date = date
 calendarOptions.visibleRange ={start:date,end:getEndDate(date, filter.value.period)};
 getEvent()
}


function onPrevNext(key) {
    if (gv.loading){
        return
    }
    const cal = fullCalendar.value.getApi()
    let visible_date = {}
    if (key == 'prev') {
        visible_date = { start: moment(cal.view.currentStart).add(calendarOptions.dateIncrement.days*-1,"days").toDate(), end:  moment(cal.view.currentEnd).add(calendarOptions.dateIncrement.days*-1,"days").toDate() }
    } else {
        visible_date =   { start: moment(cal.view.currentStart).add(calendarOptions.dateIncrement.days,"days").toDate(), end:  moment(cal.view.currentEnd).add(calendarOptions.dateIncrement.days,"days").toDate() };
    }
    
    removeDOM()
    calendarOptions.visibleRange = visible_date;
    filter.value.date = visible_date.start
    filter.value.end_date = visible_date.end

    getEvent()
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
function resourceColumn(view_type) {
    if (!view_type){
        const state =  JSON.parse(sessionStorage.getItem("reservation_chart"))
        view_type = (state?.view || "room") 
    }
    
    
    if (view_type== 'room_type') {
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
    // socket.emit("RefresheDoorDashboard", doc.message.property)
    alert(property.reservation.property)
}

function onView() {
    filter.value.view_type = filter.value.view_type == 'room_type' ? 'room' : 'room_type'
    roomChartResourceFilter.view_type = filter.value.view_type    
    calendarOptions.resourceAreaColumns = resourceColumn(filter.value.view_type)
    getResourceAndEvent()
}

function generateEventForRoomType(data){
 
    const cal = fullCalendar.value.getApi()
    let current_date = cal.view.currentStart;
    
    const room_type_event = []
    let occupy_data ={}
    
    if (filter.value.view_type=="room_type"){

     
        resources.value.forEach(r=>{
        
                while (current_date <= cal.view.currentEnd) {
                    if (r.id=="property_summary"){
                        occupy_data = data.filter(c=>c.date==moment(current_date).format("YYYY-MM-DD") )
                    
                            room_type_event.push(
                                {

                                    color:"green",
                                    resourceId: r.id,
                                    start: moment(current_date).format("YYYY-MM-DD") + "T00:00:00.000000",
                                    end: moment(current_date).format("YYYY-MM-DD") + "T23:59:00.000000",
                                    title: r.total_room - (occupy_data.reduce((n, d) => n + (d.total || 0), 0) || 0)  + ' / ' + (occupy_data.reduce((n, d) => n + (d.unassign_room || 0), 0) || 0),
                                    type: "property_summary",
                                    arrival: occupy_data?.arrival || 0,
                                    departure: occupy_data?.departure || 0,
                                    adult: occupy_data?.adult || 0,
                                    child: occupy_data?.child || 0,
                                    room_available: r.total_room - occupy_data.reduce((n, d) => n + (d.total || 0), 0) ,
                                    unassign_room:occupy_data.reduce((n, d) => n + (d.unassign_room || 0), 0)  
                                }
                            )
                    }else { 
                        occupy_data = data.find(c=>c.room_type_id== r.id && c.date==moment(current_date).format("YYYY-MM-DD") )
                    
                        room_type_event.push(
                            {

                                color:(r.total_room - (occupy_data?.total || 0)) < 0 ? "red" : "#F7F7F7",
                                resourceId: r.id,
                                start: moment(current_date).format("YYYY-MM-DD") + "T00:00:00.000000",
                                end: moment(current_date).format("YYYY-MM-DD") + "T23:59:00.000000",
                                title: r.total_room - (occupy_data?.total || 0)  + ' / ' + (occupy_data?.unassign_room || 0),
                                type: "room_type_event",
                                arrival: occupy_data?.arrival || 0,
                                departure: occupy_data?.departure || 0,
                                adult: occupy_data?.adult || 0,
                                child: occupy_data?.child || 0,
                                room_available: r.total_room - (occupy_data?.total || 0),
                                unassign_room:(occupy_data?.unassign_room || 0)
                            }
                        )
                    }
                    current_date.setDate(current_date.getDate() + 1);
                }
            
                current_date = cal.view.currentStart;
                
            })
    }else {
        //when calender view by room 
        //code below is generate event for current propert event display in first row of calendar
        resources.value.filter(r=>r.id=="property_summary").forEach(r=>{
        while (current_date <= cal.view.currentEnd) {
               occupy_data = data.find(c=>c.date==moment(current_date).format("YYYY-MM-DD") )
                   room_type_event.push(
                       {

                           color:"green",
                           resourceId: r.id,
                           start: moment(current_date).format("YYYY-MM-DD") + "T00:00:00.000000",
                           end: moment(current_date).format("YYYY-MM-DD") + "T23:59:00.000000",
                           title: r.total_room - (occupy_data?.total || 0)  + ' / ' + (occupy_data?.unassign_room || 0),
                           type: "property_summary",
                           arrival: occupy_data?.arrival || 0,
                           departure: occupy_data?.departure || 0,
                           adult: occupy_data?.adult || 0,
                           child: occupy_data?.child || 0,
                           room_available: r.total_room - (occupy_data?.total || 0),
                            unassign_room:(occupy_data?.unassign_room || 0)
                       }
                   )
           
           current_date.setDate(current_date.getDate() + 1);
       }
   
    
       
   })
}
    events.value = [...events.value, ...room_type_event]
 
}
 
const onRefresh = debouncer((show_loading = true) => {
    //clear tippy
    
    [...document.querySelectorAll('*')].forEach(node => {
        if (node._tippy) {
            node._tippy.destroy();
        }
    });
    //end clear tip 

    getResourceAndEvent()

    getTotalNote()

}, 500);



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
        business_source: f.business_source,
        view_type:filter.value.view_type
    }
    advanceFilter.value = roomChartResourceFilter

    getResourceAndEvent()

}


// search event
function onSearch(key) {
    getEvent();
}

function getTotalNote() {
    getCount('Frontdesk Note', [["note_date", ">=", working_day.date_working_day],['property','=', property.name]]).then((docs) => {
        totalNotes.value = docs
    })
}

function getResource() {
    gv.loading = true
        getApi('frontdesk.get_room_chart_resource', roomChartResourceFilter)
        .then((result) => {
            
            resources.value = result.message
  
            removeDOM()
            
            setTimeout(() => {

                const room_status = document.getElementsByClassName("room-status")
                for (let i = 0; i < room_status.length; i++) {
                    let el = room_status[i]
                    useTippy(el, {
                        content: el.getAttribute("data-title")
                    })
                }
            }, 3000);
             
            gv.loading = false
        }).catch((error)=>{
            gv.loading = false
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


function  getEvent(){ 
    gv.loading = true 
    filter.value.date =  moment.utc(calendarOptions.visibleRange.start).toDate()
        
    getApi('frontdesk.get_room_chart_calendar_event', {
        start: moment.utc(calendarOptions.visibleRange.start).format("YYYY-MM-DD"),
        end: moment.utc(calendarOptions.visibleRange.end).format("YYYY-MM-DD"),
        property: property.name,
        keyword: keyword.value.keyword,
        business_source: advanceFilter.value.business_source,
        room_type:advanceFilter.value.room_type,
        view_type:filter.value.view_type,
        room_number: keyword.value.room_number,
        room_type_group:advanceFilter.value.room_type_group,
        floor:advanceFilter.value.floor
    }).then((result) => {
        events.value = (result.message.events)
        
        
        generateEventForRoomType( result.message.occupy_data)
       
        setRoomChartlocationStorage()
        showConflictRoom(result.message.conflig_rooms)
        removeDOM()

        gv.loading = false
            
    }).catch((error) => {
        gv.loading = false
    })
}

 

function getResourceAndEvent(){
    gv.loading = true
    getApi("frontdesk.get_room_chart_resource_and_event",
    {
        start: moment.utc(calendarOptions.visibleRange.start).format("YYYY-MM-DD"),
        end: moment.utc(calendarOptions.visibleRange.end).format("YYYY-MM-DD"),
        property: property.name,
        keyword: keyword.value.keyword,
        business_source: advanceFilter.value.business_source,
        room_type:advanceFilter.value.room_type,
        view_type:filter.value.view_type,
        room_number: keyword.value.room_number,
        room_type_group:advanceFilter.value.room_type_group,
        floor:advanceFilter.value.floor
    }).then((result)=>{
        resources.value = result.message.resources
        events.value = result.message.events.events
 
        removeDOM()

        
            generateEventForRoomType(result.message.events.occupy_data)
        
        gv.loading = false
        setRoomChartlocationStorage()
        showConflictRoom(result.message.events.conflig_rooms)
    })
}

const handleScroll = (event) => {
    const sticky = document.getElementById("front_desk_search_sticky");
 
    if(document.body.scrollTop > 50){
        sticky.classList.add("front_desk_sicky_bar");
    }else{
        sticky.classList.remove("front_desk_sicky_bar");
    }
};

onMounted(() => {
    gv.loading = true
    const state = JSON.parse(sessionStorage.getItem("reservation_chart"))
    
    if (state){
        
        filter.value.view_type = state.view || "room"
        filter.value.date  = moment.utc(state.start_date).toDate()
        filter.value.end_date = moment.utc(state.end_date).toDate()

        filter.value.period = state.period || "15_days"
    }else {
        filter.value.date = moment.utc( working_day.date_working_day).add(-1,"days").toDate()
    }

    roomChartResourceFilter.view_type = filter.value.view_type


 
    calendarOptions.visibleRange =  { start:filter.value.date, end: getEndDate(filter.value.date,filter.value.period) }

   getResourceAndEvent()

    getTotalNote()
    document.body.addEventListener('scroll', handleScroll);

})

function getEndDate(start, period){
    let date = moment()
    if (period=="week"){
        date = moment(start).add(7, "days").toDate()
    }else if(period=="15_days"){
        date =  moment(start).add(15, "days").toDate()
    }else {
        date = moment(start).add(1, "months").toDate()
    }
    filter.value.end_date = date
    return date

}

onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
    document.body.removeEventListener('scroll', handleScroll);
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
    keyword.value.room_number = ''
    keyword.value.keyword = ''
    onFilterResource({})
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
function showConflictRoom(conflig_rooms){
    setTimeout(() => {
            if(conflig_rooms){
                resources.value.forEach((r)=>{
                    if (filter.value.view_type=="room_type"){
                        let room_type_el  = document.querySelector('td[data-resource-id="' + r.id + '"]')
                        let el = document.querySelector('table.fc-scrollgrid-sync-table td.fc-timeline-lane[data-resource-id="' + r.id + '"]')
                        room_type_el.parentNode.style.backgroundColor = "#EDEDED";
                        el.style.backgroundColor ="#EDEDED";
                    }

                    r.children?.forEach((c)=>{
                        let room_type_el  = document.querySelector('td[data-resource-id="' + c.id + '"]')
                        let el = document.querySelector('table.fc-scrollgrid-sync-table td.fc-timeline-lane[data-resource-id="' + c.id + '"]')
                        if (conflig_rooms.includes(c.id)){
                            room_type_el.parentNode.style.backgroundColor = setting.room_conflict_background_color;
                            el.style.backgroundColor =setting.room_conflict_background_color;

                        }else {
                            room_type_el.parentNode.style.backgroundColor = '';
                            el.style.backgroundColor = '';
                        }
                    })
                    
                    
                })
            }
            

        }, 500);
}
//Remove tippy tooltips when room chart DOM removed
const removeDOM = () => {
    document.querySelectorAll('[id^="tippy-"]').forEach(function(element) {
        element.remove();
    });
}



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
div.sticky_search_bar{
  position: -webkit-sticky;
  position: sticky;
  top: 62px;
  background-color: #eff2f7;
  z-index: 4;
}
div.front_desk_sicky_bar{
    padding:10px 0;
}
.fc-timeline-lane .fc-resource{
    background: red !important;
}
</style>