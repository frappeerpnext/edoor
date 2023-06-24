<template>
    room rate 
<!--    
    <DataTable :value="data" tableStyle="min-width: 50rem">
            <Column field="name" header="Room Number"></Column>
            
        </DataTable> -->
</template>
<script setup>
import {ref,inject} from "@/plugin"
 
const frappe = inject("$frappe")
const db = frappe.db()
const data = ref([])

 


</script>