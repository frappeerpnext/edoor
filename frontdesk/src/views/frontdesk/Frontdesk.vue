<template lang="">
    <div>
        <div style="max-width: 100%; height: 1000px" class="p-6">
            <div class="pb-16">
                <NewFITReservationButton/>
                <div class="relative" aria-haspopup="true" aria-controls="overlay_menu">
                    <FullCalendar :options="calendarOptions" class="h-full">
                        <template v-slot:eventContent="{event}">
                                <div class="group relative h-full p-1" v-tooltip.bottom="{ value: `
                                <div class='tooltip-reservation text-sm -mt-6' style='width:350px; line-height: auto'>
                                    <table>
                                        <tbody>
                                            <tr><td><div>ID: ${event.reservation || ''}</div></td></tr>
                                            <tr><td><div>Reference #: ${event.reference_number || ''}</div></td></tr>
                                        <tr><td><div>Guest: ${event.title}</div></td></tr>
                                        <tr><td><div>Start Date: ${dateFormat(event.start)}</div></td></tr>
                                        <tr><td><div>End Date: ${dateFormat(event.end)}</div></td></tr>
                                        <tr><td><div>Room: ${event.extendedProps?.adult}</div></td></tr>
                                        <tr><td><div>Adult: ${event.extendedProps?.adult} Child: ${event.extendedProps?.child} Pax: ${event.extendedProps?.pax}</div></td></tr>
                                        </tbody>
                                    </table>
                                </div>`, escape: true, class: 'event-tooltip' }">
                                    {{ event.title }}
                                    
                                </div>
                        </template>
                    </FullCalendar> 
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
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import { useDialog } from 'primevue/usedialog';
const frappe = inject('$frappe')
const call = frappe.call();
const moment = inject('$moment')

const dialog = useDialog();

let showTooltip = ref(false)
const reservation = ref({})
let eventInfo = reactive({
    isShow: false,
    left: 0,
    top: 0,
    data: null
})
function dateFormat(date){
    return moment(date).format("MMM DD, YYYY")
}
const calendarOptions = reactive({
    plugins: [interactionPlugin, resourceTimelinePlugin],
    schedulerLicenseKey: 'GPL-My-Project-Is-Open-Source',
    timeZone: 'UTC',
    initialView: 'resourceTimeline',
    initialDate: '2023-05-17',
    dateIncrement: { days: 5 },
    dayHeaderContent: (args) => {
        return moment(args.date).format('MMM YYYY');
    },
    visibleRange: function (currentDate) {
        // Generate a new date for manipulating in the next step
        var startDate = new Date(currentDate.valueOf());
        var endDate = new Date(currentDate.valueOf());

        // Adjust the start & end dates, respectively
        startDate.setDate(startDate.getDate() - 1); // One day in the past

        endDate.setDate(endDate.getDate() + 31); // Two days into the future

        // Remove times from start/end
        startDate = startDate.toISOString().substr(0, 10);
        endDate = endDate.toISOString().substr(0, 10);

        return { start: startDate, end: endDate };
    },
    resourceAreaColumns: [
        {
            labelText: 'xxx',
            headerContent: 'Room'
        },
   
        {
            field: 'housekeeping_status',
            width: 80,
            cellDidMount: function (arg) {
                if (arg.fieldValue)
                    arg.el.innerHTML = `<div class="pt-2 pl-1">${arg.fieldValue}</div>`;

            },
            cellClassNames: 'area-column-hide-value'
        }
    ],
    resources: function (info, successCallback, failureCallback) {

        call.get('edoor.api.frontdesk.get_room_chart_resource', {
            property: "propety_1",
            room_type: "room_type",
            building: "building"
        }).then((result) => {
            console.log(result.message)
            successCallback(result.message)
        }).catch((error) => {
            alert("load data fiale")
        });
    },
    events: function (info, successCallback, failureCallback) {

        call.get('edoor.api.frontdesk.get_room_chart_calendar_event', {
            start: info.start,
            end: info.end,
            property: "propety_1",
            room_type: "room_type",
            building: "building"
        }).then((result) => {
                successCallback(result.message)
            })
            .catch((error) => {
                alert("load data fiale")
            });
    },

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
        const data = info.event._def.extendedProps  ;
        showReservationDetail(data.reservation)
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
function onSelected($event) {
    console.log($event)
}


function showReservationDetail(name) {
    
    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
            style: {
                width: '50vw',
            },
            maximizable: true,
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            console.log(options)
        }
    });
}



</script>
<style>
.fc-h-event {
    padding: 0;
}
.fc-event { height: 40px !important; }
.fc-event-main,
.fc-event-main > span {
    display: block;
    height: 100%;
}
</style>