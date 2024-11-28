<template>
    <span class="rounded-pill py-1 px-2 text-white border-round-3xl" :class="class"  
    :style="{ background: status?.color ? status.color : statusName == 'Stay Over' ? 'rgb(41, 205, 66)' : statusName == 'Arrival' ? 'rgb(255, 115, 0)' : statusName == 'Departure' ? 'rgb(79, 79, 79)' : ''}">
        {{ $t(statusName) }}
         <template v-if="statusName == 'Arrival' || statusName == 'Departure'">
             -
        {{gv.timeFormat(time) }} 
         </template>
      
        <slot>
        </slot>
    </span>
</template>
<script setup>
import { inject} from '@/plugin';
import {computed} from 'vue'
import {i18n} from '@/i18n';
const gv = inject("$gv")
const { t: $t } = i18n.global;
const props = defineProps({
    statusName: String,
    class: String,
    time:String
})
const setting = JSON.parse(localStorage.getItem('edoor_setting'))

const status = computed(()=>{
    return setting.reservation_status.find((r)=>r.name == props.statusName)
})

</script>
<style lang="">
    
</style>