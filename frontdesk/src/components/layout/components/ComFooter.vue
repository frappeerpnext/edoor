<template >
    <div class="d-bg-edoor wrapper-foot-deco fixed bottom-0 w-full items-center flex" style="z-index: 9899;">
        <div class="flex justify-between  text-white px-2 w-full"
            v-if="data.date_working_day && data.cashier_shift">
            <p>System date: {{ moment(data.date_working_day).format("DD, MMM YYYY") }} | {{ data.cashier_shift?.shift_name
            }} {{ moment(data.cashier?.creation).format("DD, MMM YYYY") }}</p>
            <p>Power by: eDoor Frontdesk</p>
        </div>
    </div>
</template>
<script setup>
import { inject } from 'vue'
const moment = inject('$moment')

const data = JSON.parse(localStorage.getItem("edoor_working_day"))


</script>