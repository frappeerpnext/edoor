<template>
<div class="flex my-4 justify-end">
    <div v-for="(d, index) in data" :key="index" >
    <span class="px-4 me-2 ms-6" :style="{background:d.color}"></span>{{ d.name }}  
    </div> 
</div>
</template>
<script setup>
import { ref, inject } from '@/plugin';
const frappe= inject("$frappe")
const db =frappe.db()
const data = ref([])
    db.getDocList('Reservation Status',{
        fields: ['name', 'color'],
    })
    .then((docs) =>{
        data.value = docs
    })
</script>