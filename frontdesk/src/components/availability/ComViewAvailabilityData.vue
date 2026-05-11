<template>
<ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
    

    <div class="card" v-if="data">
     
        <DataTable :value="tableData" scrollable tableStyle="min-width: 50rem">
             <Column field="room_type_id" header="Room type"></Column>
            <Column v-for="c in days" :field="c.toString()" :header="c.toString()"></Column>
            
        </DataTable>
    </div>
 </ComDialogContent>
</template>
<script setup>
import { computed, inject, onMounted, ref } from 'vue';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import ColumnGroup from 'primevue/columngroup';   // optional
import Row from 'primevue/row';                   // optional

const moment = inject("$moment")
const days = Array.from({ length: 31 }, (_, i) => i + 1)
const data = ref()
const tableData = ref([])
function buildTablData() {
    const result = {}

    data.value?.forEach(r => {
        const d = moment.utc(r.date)
        const day = d.date()
        const monthKey = d.format("MMM-YYYY")

        const key = `${r.room_type_id}-${monthKey}`

        if (!result[key]) {
            result[key] = {
                room_type_id: r.room_type_id,
                month: monthKey,
                stop_sale: r.stop_sale
            }

            // init 1–31 columns
            for (let i = 1; i <= 31; i++) {
                result[key][i] = null
            }
        }

        result[key][day] = r.value
    })

    tableData.value =  Object.values(result)
}

async function getData(){
    const res = await app.getApi("room_availability.get_room_availability", {
            property: window.property_name,
            start_date: '2026-05-09',
            end_date: "2027-05-09"
        })
        if (res.data) {
            data.value = res.data
            buildTablData()
        }
}
onMounted(async ()=>{
await getData()
})

</script>