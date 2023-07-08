<template lang="">
    <div class="pt-2 pb-1 border-b border-color-edoor g_-todies" @click="onClick">
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
    <Dialog v-model:visible="visible" modal header="View Reservations" :style="{ width: '50vw' }">
        <div>{{data}}</div>
    </Dialog>
</template>
<script setup>
import { ref, computed,getDocList,inject } from "@/plugin"
import ProgressBar from 'primevue/progressbar';
const visible = ref(false) 
const data = ref([])
const moment = inject('$moment')
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
    }
})
const progress = computed(() => {
    if (props.totalValue != null && props.value != null) {
        return (props.value / props.totalValue) * 100
    } else {
        return null
    }

})
function onClick(){
    const reservation_field = ['*']
    if(props.dialogKey){
        if(props.dialogKey == 'arrival'){
   
            getReservationStay({
                fields: reservation_field,
                filters: [['arrival_date', '=', moment(reservation_chart.start_date).add(1,'days').format("yyyy-MM-DD")]]
            })
        }
    }
    
    visible.value = true
}
function getReservationStay(filter){
    getDocList('Reservation Stay',filter).then((r)=>{
        data.value = r 
    })
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