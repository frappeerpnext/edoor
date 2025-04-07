<template>
   
    <ComDataView apiUrl="frontdesk.get_ledger_balance" :options="options"  >
        <template v-slot:default="{ data }">
            <ComSummaryofBalance :summary="data" :start_date="startDate" :end_date="endDate" />

        </template>
    </ComDataView>
</template>
<script setup>
import { ref } from "@/plugin"
import ComSummaryofBalance from "@/views/city_ledger/components/ComSummaryofBalance.vue"
const props = defineProps({
    ledgerType:String,
    startDate:String,
    endDate:String
})
const options = {
    property:window.property_name,
    start_date:props.startDate,
    end_date:props.endDate,
    ledger_type: props.ledgerType
}
 
</script>