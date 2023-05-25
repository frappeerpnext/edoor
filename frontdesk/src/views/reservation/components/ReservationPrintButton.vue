<template>
    <SplitButton label="Print" icon="pi pi-print" @click="save" :model="items" />
</template>
<script setup>
import { useToast } from "primevue/usetoast";
import { ref, inject } from "@/plugin";
const toast = useToast();
const props = defineProps({
    name: String
})
const frappe = inject("$frappe")
const db = frappe.db();
const items = ref([])

db.getDocList('Print Format', {
    fields: [
        'name',
        'title'
    ],
    filters: [["show_in_reservation_stay_detail", "=", "1"]]

})
    .then((doc) => {
        console.log(doc)
        doc.forEach(d => {
            items.value.push({
                label: d.title,
                name:"Pheakdey",
                icon: 'pi pi-refresh',
                command: (r) => {
                    console.log(r)
                    toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                }
            })
        });
    })
    .catch((error) => console.error(error));




const save = () => {
    toast.add({ severity: 'success', summary: 'Success', detail: 'Data Saved', life: 3000 });
};
</script>