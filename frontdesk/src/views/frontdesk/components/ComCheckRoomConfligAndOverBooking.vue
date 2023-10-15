<template>
    <Button @click="onView" v-if="show_warning">Show Warning Over booking and config room </Button>
</template>

<script setup>
import {getApi,ref,useDialog,onMounted, inject} from "@/plugin"
import ComIFrameModal from '@/components/ComIFrameModal.vue';
const gv = inject("$gv")
const loading = ref(false)
const show_warning = ref(false)
const dialog = useDialog();



onMounted(()=>{
loading.value = true;
    getApi("frontdesk.check_room_config_and_over_booking",{property:window.property_name}).then(r=>{
    show_warning.value = r.message
    loading.value = false
}).catch(ex=>{
    loading.value = false
})


})
function onView(){

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name:window.property_name,
            report_name: gv.getCustomPrintFormat("eDoor Conflict Room Assignment and Over Booking Reservation"),
            view:"ui",
        },
        props: {
            header:"Conflict Room and Over booking Reservation",
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
    });

}

</script>