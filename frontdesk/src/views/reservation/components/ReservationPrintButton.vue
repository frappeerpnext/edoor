<template>
    <SplitButton label="Print" icon="pi pi-print" @click="save" :model="items" />
</template>
<script setup>
import ComIFrameModal from "@/components/ComIFrameModal.vue";

import { useToast } from "primevue/usetoast";
import { ref, inject,useDialog,onMounted} from "@/plugin";
const toast = useToast();
const dialog = useDialog();
const props = defineProps({
    reservation: String,
})
const gv = inject("$gv")
const frappe = inject("$frappe")
const db = frappe.db();
const items = ref([])

//reservation detail
items.value.push({
    label: "Reservation Detail",
    icon: 'pi pi-check-circle',
    acceptClass: 'border-none crfm-dialog',
    rejectClass: 'hidden',
    acceptIcon: 'pi pi-check-circle',
    acceptLabel: 'Ok',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation",
                name: props.reservation ?? "",
                report_name:  gv.getCustomPrintFormat("Reservation Detail"),
            },
            props: {
                header: "Reservation Detail",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
            },
        });
    }
})
onMounted(() => {
db.getDocList('Print Format', {
    fields: [
        'name',
        'title'
    ],
    filters: [["show_in_reservation_stay_detail", "=", "1"]]

})
    .then((doc) => {

        doc.forEach(d => {
            items.value.push({
                label: d.title,
                name:"Pheakdey",
                icon: 'pi pi-refresh',
                command: (r) => {
               
                    toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                }
            })
        });
    })
    .catch((error) => console.error(error));

})


const save = () => {
    toast.add({ severity: 'success', summary: 'Success', detail: 'Data Saved', life: 3000 });
};
</script>