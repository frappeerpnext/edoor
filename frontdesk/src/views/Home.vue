<template>
  <div>
    <h1>Home Page</h1>
    <span class="material-symbols-outlined">settings</span>
    <Button label="Primary" size="small"/>
    <Button @click="Update">Update </Button>
    <Button @click="AddNote">Add Note </Button>
    <a href="http://192.168.10.114:1216/app/sale">Misc Sale</a>
 
  </div>
</template>

<script setup>
import { inject, ref } from '@/plugin'
const frappe = inject('$frappe')
const db = frappe.db()
const call = frappe.call();
const data = ref()



 

db.getDoc('Sale', 'SO2023-0007')
  .then((doc) => {
    data.value = doc
  })
  .catch((error) => console.error(error));
 


</script>
