<template lang="">
    <div>
        <div style="max-width: 100%; height: 1000px" class="p-6">
            <div>
                <div class="relative" aria-haspopup="true" aria-controls="overlay_menu">
                    <FullCalendar :options="calendarOptions" class="h-full">
                        <template v-slot:eventContent="{event}">

                            <div class="group relative">
                                {{ event.title }}
                                <div class="invisible group-hover:visible absolute bg-blue-600 p-4 rounded-md z-50">
                                    This is the content that will be shown on hover.
                                </div>
                            </div>
                            
                        </template>
                    </FullCalendar> 
                    <div class="w-44 absolute pt-2 z-50" :style="{left:eventInfo.left + 'px',top:eventInfo.top+'px'}"  v-if="eventInfo.isShow">
                        <div class="bg-white border border-gray-300 rounded-sm shadow-lg text-black" v-if="eventInfo.data">
                            <div class="bg-gray-100 text-lg p-1">{{eventInfo.data.title}}</div>
                            <div class="p-1 text-sm">
                                <!-- <p>Ref No : {{eventInfo.data.extendedProps.internal_ref_no}}</p> -->
                                <p>Start date : {{ moment(eventInfo.data.start).format("MMM DD, YYYY") }}</p>
                                <p>Start end : {{ moment(eventInfo.data.end).format("MMM DD, YYYY") }}</p>
                                <!-- <p>Total night : {{eventInfo.data.extendedProps.total_night}}</p>
                                <p>Adult : {{eventInfo.data.extendedProps.adult}}</p>
                                <p>Room : {{eventInfo.data.extendedProps.room}}</p> -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
</template>
<script setup>
import { ref, reactive, inject } from '@/plugin'
import '@fullcalendar/core/vdom' // solves problem with Vite
import FullCalendar from '@fullcalendar/vue3'
import interactionPlugin from '@fullcalendar/interaction'
import resourceTimelinePlugin from '@fullcalendar/resource-timeline';
const moment = inject('$moment')
let loading = ref(false)
let showTooltip = ref(false)
const reservation = ref({})
let eventInfo = reactive({
    isShow: false,
    left: 0,
    top: 0,
    data: null
})
const calendarOptions = reactive({
    plugins: [interactionPlugin, resourceTimelinePlugin],
    schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
    timeZone: 'UTC',
    initialView: 'resourceTimelineMonth',
    resourceGroupField: 'title',
    //resourceAreaHeaderContent: 'Rooms',
    resourceAreaColumns: [
        {
            labelText: 'xxx',
            headerContent: 'Room'
        },
        {
            field: 'title',
            cellDidMount: function (arg) {
                //arg.el.innerHTML +=`<input type="text" value="${arg.fieldValue}" />`;
            }
        },
        {
            field: 'icon',
            width: 80,
            cellDidMount: function (arg) {
                if (arg.fieldValue)
                    arg.el.innerHTML = `<div class="pt-2 pl-1"><img class="inline" src="${arg.fieldValue}" width="25"/></div>`;

            },
            cellClassNames: 'area-column-hide-value'
        }
    ],
    resources: [
        { id: 'a', title: 'Room A' },
        { id: 'b', title: 'Room B' },
        { id: 'c', title: 'Room C' }
    ],
    events: [
        { id: '1', resourceId: 'a', start: '2023-05-01T12:00:00+00:00', end: '2023-05-20T07:00:00', title: 'event 1' },
        { id: '2', resourceId: 'b', start: '2023-05-06T12:00:00+00:00', end: '2023-05-20T22:00:00', title: 'event 2' },
        { id: '3', resourceId: 'c', start: '2023-05-06T12:00:00+00:00', end: '2023-05-20T18:00:00', title: 'event 3' }
    ],
    selectable: true,
    editable: true,
    resourceAreaWidth: "350px",
    height: 'auto',
    slotDuration: {
        "hours": 12
    },
    slotLabelInterval: {
        "hours": 24
    },
    slotLabelFormat: [
        {
            day: '2-digit',
        }
    ],
    dateClick: (($event) => {
        console.log($event)
    }),
    eventResizeStop: (($event) => {
        console.log($event)
    }),
    eventClick: ((info) => {
        this.reservation = info.event.extendedProps.data;
        this.onChangeModal(true);
    }),
    eventMouseEnter: (($event) => {
        eventInfo.data = $event.event;
        // showTooltip.value = true;
        showTooltip.value.toggle(event);
        alert(showTooltip.value )
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

function onMousePointer(event) {
    var eventDoc, doc, body;
    event = event || window.event; // IE-ism

    if (event.pageX == null && event.clientX != null) {
        eventDoc = (event.target && event.target.ownerDocument) || document;
        doc = eventDoc.documentElement;
        body = eventDoc.body;
        event.pageX = event.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);
        event.pageY = event.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc && doc.clientTop || body && body.clientTop || 0);
    }
    // check screen
    var screenX = window.innerWidth;
    var screenY = window.innerHeight;
    var pageX = event.pageX;
    var pageY = event.pageY;

    if ((screenX - pageX) < 200)
        pageX = pageX - 220;
    if ((screenY - pageY) < 200)
        pageY = pageY - 220;

    if (eventInfo.isShow) {
        eventInfo.left = pageX;
        eventInfo.top = pageY;
    }
}
function onSelected($event) {
    console.log($event)
}
 
</script>
<style>
    .fc-h-event {
        padding: 0;
    }
</style>