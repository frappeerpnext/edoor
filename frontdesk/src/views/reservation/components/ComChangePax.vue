<template>
    <ComOverlayPanelContent title="Change Pax" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="flex gap-2 my-2">
        <InputNumber v-model="stay.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
            class="child-adults-txt" />
        <InputNumber v-model="stay.child" inputId="stacked-buttons" showButtons :min="0" :max="100"
            class="child-adults-txt" />
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>

import { ref, useToast, inject } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
const emit = defineEmits(['onClose'])
const toast = useToast()
const rs = inject('$reservation_stay');
const frappe = inject('$frappe');
const db = frappe.db();
const isLoading = ref(false)
const gv = inject('$gv');

const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))

const onSave = () => {
    isLoading.value = true;

    db.updateDoc("Reservation Stay", stay.value.name, {
        adult: stay.value.adult,
        child: stay.value.child,
        update_reservation: true
    })
        .then((doc) => {
            rs.reservationStay.adult = doc.adult
            rs.reservationStay.child = doc.child

            toast.add({ severity: 'success', summary: 'Change Pax', detail: "Change pax successfully", life: 3000 })
            isLoading.value = false;
            emit("onClose")
        }).catch((ex) => {
            isLoading.value = false;
            gv.showErrorMessage(ex)
        })



}



</script>
