<template >
    
    <div class="d-bg-edoor wrapper-foot-deco fixed bottom-0 w-full items-center flex" style="z-index: 12;">
        <div class="flex justify-between  text-white px-2 w-full" v-if="data?.date_working_day">
            <p>Working Day # : {{ data.name }}, System date : {{ moment(data?.date_working_day).format("DD-MMM-YYYY") }}
 
                <template v-if="gv.cashier_shift?.name">
                    | {{ gv.cashier_shift?.shift_name }}, Shift # : <a @click="onViewShiftDetail">{{ gv.cashier_shift?.name }}</a>,
                    {{ moment(gv.cashier_shift?.creation).format("DD-MMM-YYYY hh:mm A") }}
                </template>
            </p>
            <p>Powered by : {{ powered_by_text }}</p>
        </div>
    </div>
</template>
<script setup>
import { inject,watch,ref } from 'vue'
const moment = inject('$moment')
const powered_by_text =  window.setting.powered_by_text 
const data = ref(JSON.parse(localStorage.getItem("edoor_working_day")))
const gv = inject("$gv")


watch(() => gv.working_day, (newValue, oldValue) => {
    if(gv.working_day?.name){
        data.value = gv.working_day
    }
})

function onViewShiftDetail(){
    window.postMessage('view_cashier_shift_detail|' +  gv.cashier_shift?.name , '*')
}
</script>