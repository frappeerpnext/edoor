<template>
    <span class="text-xl">
        <b>Today payment Received</b>
        </span>   
    <div>
        <DataTable :value="doc?.today_payment"    >
      <template #empty>
        <div class="flex items-center justify-center h-full  p-16">
  There is no city ledger transaction
</div>

        </template> 
    <Column field="account_name" header="Account Name"></Column>
    <Column  header="Total Amount">
        <template #body="slotProps">
            <CurrencyFormat :value="slotProps.data.total_amount" />
        </template>
    </Column>
</DataTable>
    </div>
    <div class="mt-3">
        <span class="text-xl">
            <b>MTD payment Received</b>
            </span>   
    <div>
        <DataTable :value="doc?.mtd_payment"    >
      <template #empty>
        <div class="flex items-center justify-center h-full  p-16">
  There is no city ledger transaction
</div>

        </template> 
    <Column field="account_name" header="Account Name"></Column>
    <Column  header="Total Amount">
        <template #body="slotProps">
            <CurrencyFormat :value="slotProps.data.total_amount" />
        </template>
    </Column>
    
</DataTable>
    </div>
    </div>
</template>
<script setup>
import { ref, getDoc, onMounted,getApi} from '@/plugin'
const doc = ref({})
const props = defineProps({
    name: String,

})
function loadData(){
    getApi("city_ledger.get_city_Ledger_payment_received", {
        filters: {
            date: working_day.date_working_day,
            city_ledger: props?.name,
            property:window.property.name
        }
    }).then((result) => {
        console.log(window.property)
        doc.value = result.message
    })
}
onMounted(() => {
    loadData()
})
</script>