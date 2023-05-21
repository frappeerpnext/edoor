<template >
    
    <div class="d-bg-edoor wrapper-foot-deco fixed bottom-0 w-full items-center flex">
        <div class="flex justify-between  text-white px-2 w-full" v-if="data.date_cashier_shift && data.date_working_day && data.shift_name">
            <p>System date: {{ moment(data.date_working_day).format("DD, MMM YYYY") }} | {{ data.cashier_shift?.shift_name }} {{ moment(data.cashier?.creation).format("DD, MMM YYYY") }}</p>
            <p>Power by: eDoor Frontdesk</p>
        </div>
    </div>
</template>
<script setup>
import {inject, ref} from 'vue'
const frappe = inject('$frappe')
const moment = inject('$moment')
const call = frappe.call()
let data = ref({})
const property = JSON.parse(localStorage.getItem("edoor_property"))

call.get('edoor.api.frontdesk.get_working_day', {
    property: property.name
}).then((r)=>{
    data.value = r.message
    
})
</script>