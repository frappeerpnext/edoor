<template>
    <SplitButton label="Print" icon="pi pi-print" :model="items" />
</template>
<script setup>
import { useToast } from "primevue/usetoast";
import { ref, inject,useDialog } from "@/plugin";
import ComPrintGuestRegistrationCard from "./ComPrintGuestRegistrationCard.vue";
const dialog = useDialog();

const toast = useToast();
const props = defineProps({
    reservation: String,
    reservation_stay: String
})
const frappe = inject("$frappe")
const db = frappe.db();
const items = ref([])

//static print button
items.value.push({
    label: "Guest Registration Card",
    icon: 'pi pi-user-edit',
    command: () => {
            const dialogRef = dialog.open(ComPrintGuestRegistrationCard, {
            data: {
                reservation:props.reservation??"",
                reservation_stay:props.reservation_stay??""
            },
            props: {
                header: "Guest Registration Card",
                style: {
                    width: '80vw',
                },
                modal: true,
                maximizable: true,
            },
        });
    }
})



if (props.reservation_stay) {
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
                    name: "Pheakdey",
                    icon: 'pi pi-refresh',
                    command: (r) => {
                        console.log(r)
                        toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                    }
                })
            });
        })
        .catch((error) => console.error(error));

} else {
    //get dynamic menu by reservation

}



// const save = () => {
//     toast.add({ severity: 'success', summary: 'Success', detail: 'Data Saved', life: 3000 });
// };

</script>