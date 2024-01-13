<template lang="">
    <div class="pt-2 pb-1 border-b border-color-edoor g_-todies" @click="onOpenDetail">
        <div class="flex justify-between align-items-center mb-1">
            <div class="flex align-items-center h-full font-medium">{{title}}</div>
            <div class="flex-grow px-1">  </div>
            <div class="px-2 py-1 font-medium border-round-lg text-white badge-td-guest"><slot></slot></div>
        </div>
        <ProgressBar v-if="progress != null" :value="progress" class="progress-perentage" :showValue="false"></ProgressBar>
    </div>
 
</template>
<script setup>
import { computed,inject,useDialog } from "@/plugin"
import ComReservationStayList from "./ComReservationStayList.vue";
import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ProgressBar from 'primevue/progressbar';

const property = JSON.parse(localStorage.getItem("edoor_property"))
const moment = inject('$moment')
const dialog = useDialog()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const gv = inject("$gv")

const props = defineProps({
    title: String,
    value: {
        type: Number,
        default: null
    },
    totalValue: {
        type: Number,
        default: null
    },
    dialogKey:{
        type: String
    },
    disabled: {
        type:Boolean,
        default:false
    },
    isHousekeeping: {
        type:Boolean,
        default:false
    }
})

const progress = computed(() => {
    if (props.totalValue != null && props.value != null) {
        return (props.value / props.totalValue) * 100
    } else {
        return null
    }

})

function onViewData(doctype, report_name, title ,extra_params,filter_options ){
   const dialogRef = dialog.open(ComIFrameModal, {
       data: {
           "doctype": doctype,
           name: JSON.parse(localStorage.getItem("edoor_property")).name,
           report_name: report_name,
           view:"ui",
           extra_params:extra_params,
           filter_options:filter_options,
           fullheight: true
       },
       props: {
           header:title,
           style: {
               width: '90vw',
           },
           position:"top",
           modal: true,
           maximizable: true,
           closeOnEscape: false
       }
   });
}

const onOpenDetail = () => { 
const filters = [
     ['property','=',property.name]
]
    if(props.dialogKey == "all_rooms"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Room%20List",
            gv.getCustomPrintFormat("eDoor Room List"),
            'Room List',
            [{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','building','floor','room_type_group','room_type','housekeeping_status']
        )
    }else if(props.dialogKey  == "arrival"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Arrival Guest"),
            'Arrival Guest',
            [{key:'action', value:"view_arrival"},{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','building','floor','room_type','reservation_status']
        )
    }
    else if(props.dialogKey == "departure"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Departure%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Departure Guest"),
            'Departure',
            [{key:'action', value:"view_departure"},{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','building','floor','room_type','reservation_status','business_source']
        )
    } else if(props.dialogKey == "unassign_room"){

        onViewData(
            'Business%20Branch',
            // "eDoor%20Unassign%20Room%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Unassign Room Reservation List"),
            'Unassign Room Reservation List',
            [{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','room_type','business_source']
        )
    }
    else if(props.dialogKey == "pickup_drop_off"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Pickup%20and%20Drop%20Off%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Pickup and Drop Off Reservation List"),
            'Pickup & Drop Off',
            [{key:'action', value:"view_departure_remaining"},{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','room_type','reservation_status','business_source',"transportation_mode",'transportation_company']
        )
        
    }
    else if(props.dialogKey == "git_arrival"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20GIT%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor GIT Arrival Guest"),
            'GIT Arrival',
            [{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','room_type','reservation_status','business_source']
        )
    }
    else if(props.dialogKey == "fit_arrival"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20GIT%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor FIT Arrival Guest"),
            'FIT Arrival',
            [{key:"date", value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','room_type','reservation_status','business_source']
        )
    }
    else if(props.dialogKey  == "stay_over"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Stay%20Over%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Stay Over Guest"),
            'Stay Over',
            [{key:"date",value:working_day.date_working_day},{key:"is_housekeeping", value:props.isHousekeeping}],
            ['keyword','room_type','reservation_status','business_source']
        )
    }
    else if(props.dialogKey  == "no_show"){
    
        onViewData(
            'Business%20Branch',
            // "eDoor%20No%20Show%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor No Show Reservation List"),
            'No Show',
            [{key:"date",value:working_day.date_working_day}],
            []
        )
    }
    
    else if(props.dialogKey  == "cancelled"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Cancel%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Cancel Reservation List"),
            'Cancelled Reservation',
            [{key:"date",value:working_day.date_working_day}],
            []
        )
    }

    else if(props.dialogKey  == "void"){
        onViewData(
            'Business%20Branch',
            // "eDoor%20Void%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Void Reservation List"),
            'Void Reservation',
            [{key:"date",value:working_day.date_working_day}],
            []
        )
    }
  
}


function onOpenDetailx() {
    const reservation_chart = JSON.parse(sessionStorage.getItem('reservation_chart'))
    if (!props.disabled){
        const filters = [
            ['property','=',property.name]
        ]
        if(props.dialogKey == "arrival"){
            filters.push(['arrival_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")])
        }
        else if(props.dialogKey == "departure"){
            filters.push(['departure_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")])
        }
        else if(props.dialogKey == "unassign_room"){
            filters.push(['arrival_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")])
            filters.push(['rooms', '=', ''])
        }
        else if(props.dialogKey == "pickup"){
            filters.push(['arrival_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")])
            filters.push(['require_pickup', '=', 1])
        }
        else if(props.dialogKey == "drop_off"){
            filters.push(['arrival_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")])
            filters.push(['require_drop_off', '=', 1])
        }
        dialog.open(ComReservationStayList, {
            props: {
                header: props.title,
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
            data:{
                filters: filters
            },
            onClose: (options) => {
                if(options.data){
                    //
                }   
            }
        });
    }
}
</script>
<style>
.progress-perentage{
    height: 3px !important;
    border-radius: 2px !important;
}
.g_-todies:hover{
    background-color: #e9ecef;
}
</style>