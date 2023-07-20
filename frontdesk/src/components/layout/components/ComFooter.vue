<template >
    <div class="d-bg-edoor wrapper-foot-deco fixed bottom-0 w-full items-center flex" style="z-index: 12;">
        <div class="flex justify-between  text-white px-2 w-full" v-if="data.date_working_day">
            <p>Working Day #: {{ data.name }}, System date: {{ moment(data?.date_working_day).format("DD-MMM-YYYY") }}

                <template v-if="gv.cashier_shift">
                    | {{ gv.cashier_shift?.shift_name }}, Shift #: <a @click="onViewShiftDetail">{{ gv.cashier_shift?.name }}</a>,
                    {{ moment(gv.cashier_shift?.creation).format("DD-MMM-YYYY hh:mm A") }}
                </template>
            </p>
            <p>Power by: eDoor Frontdesk</p>
        </div>
    </div>
</template>
<script setup>
import { inject } from 'vue'
const moment = inject('$moment')

const data = JSON.parse(localStorage.getItem("edoor_working_day"))
const gv = inject("$gv")
function onViewShiftDetail(){
    window.postMessage('view_cashier_shift_detail|' +  gv.cashier_shift?.name , '*')
}
</script>