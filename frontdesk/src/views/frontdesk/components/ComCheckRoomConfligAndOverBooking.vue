<template>
    <Button @click="onView" class="border-none fixed bottom-8 right-8 " style="background-color: #ff0021;z-index:900;" v-if="show_warning">
        <ComIcon icon="iconConflictRoom" class="me-2" height="18px" />
        Room Conflict</Button>
</template>

<script setup>
import {getApi,ref,useDialog,onMounted, inject} from "@/plugin"
import ComIFrameModal from '@/components/ComIFrameModal.vue';
import Message from 'primevue/message';
const gv = inject("$gv")
const loading = ref(false)
const show_warning = ref(false)
const dialog = useDialog();



onMounted(()=>{
loading.value = true;
    getApi("frontdesk.check_room_config_and_over_booking",{property:window.property_name}).then(r=>{
    show_warning.value = r.message>1
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