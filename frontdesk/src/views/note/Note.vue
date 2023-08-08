<template>
    <h1>Note list</h1>
    <p>@Ty you can bench mark from google keep if u want</p>
    {{ notes }}
</template>
<script setup>
import { ref, inject } from '@/plugin';
const frappe = inject('$frappe');
const db = frappe.db();
const notes = ref();
const loading = ref(false);
const gv = inject('$gv');

db.getDocList('Frontdesk Note')
    .then((docs) => {
		notes.value = docs
		loading.value = false			
	}).catch((rr)=>{
		gv.toast('error', rr)
	})
</script>