<template>
    room rate 
    {{ data }}
    <DataTable :value="data" tableStyle="min-width: 50rem">
            <Column field="name" header="Room Number"></Column>
            
        </DataTable>
</template>
<script setup>
import {ref,inject} from "@/plugin"
const props  = defineProps({
    reservation_stay:String
})
const frappe = inject("$frappe")
const db = frappe.db()
const data = ref([])

db.getDocList('Reservation Room Rate',{
    limit:100,
    fields:["*"],
    filters:[["reservation_stay","=",props.reservation_stay]]
})
  .then((docs) => 
  
  {
    data.value = docs
  }
  
  )
  .catch((error) => console.error(error));



</script>