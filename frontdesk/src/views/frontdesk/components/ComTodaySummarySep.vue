<template lang="">
    <div class="pt-2 pb-1 border-b border-color-edoor g_-todies" @click="onOpenDetail">
        <div class="flex justify-between align-items-center mb-1">
            <div class="flex align-items-center h-full font-medium">{{title}}</div>
            <div class="flex-grow px-1">
                
            </div>
            <div class="px-2 py-1 font-medium border-round-lg text-white badge-td-guest">
                <slot></slot>
            </div>
        </div>
        <ProgressBar v-if="progress != null" :value="progress" class="progress-perentage" :showValue="false"></ProgressBar>
    </div>
 
</template>
<script setup>
import { ref, computed,getDocList,inject,useDialog } from "@/plugin"
import ProgressBar from 'primevue/progressbar';
import ComReservationStayList from "./ComReservationStayList.vue";
const property = JSON.parse(localStorage.getItem("edoor_property"))
const moment = inject('$moment')
const dialog = useDialog()
const reservation_chart = JSON.parse(localStorage.getItem('reservation_chart'))
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
    }
})
const progress = computed(() => {
    if (props.totalValue != null && props.value != null) {
        return (props.value / props.totalValue) * 100
    } else {
        return null
    }

})

function onOpenDetail() {
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
                closeOnEscape: false
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
.progress-perentage {
    height: 3px !important;
    border-radius: 2px !important;
}
.g_-todies:hover{
    background-color: #e9ecef;
}
</style>