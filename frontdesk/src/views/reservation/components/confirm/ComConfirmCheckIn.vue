<template>
    <ComDialogContent :hideButtonClose="true" :hideButtonOK="true">
 
        <div v-if="rs.room_rates?.length > 0 && reservationStays?.length==0">
            <Message severity="info"> Room rate on {{ moment(rs.room_rates[0].date).format('DD-MM-YYYY') }} is
                <CurrencyFormat :value="rs.room_rates[0].total_rate" />
                <br />
                Please make sure your room rate is correct.
            </Message>
        </div>
        <div v-else>
            <Message severity="info">
                Your are about to check in {{ reservationStays.length }} room(s).
                <br />
                Please make sure that you assign room, guest and set room rate correctly.
            </Message>

        </div>

        <div class="relative">
            <span class="absolute w-full"><Checkbox class="w-full" v-model="isConfirm" :binary="true" /></span>
            <span class="pl-5">I am verify that all information is correct</span>
        </div>
        <template #footer-right>

            <Button :disabled="!isConfirm" @click="onOk" class="bg-green-500 border-none">
                <ComIcon icon="checkin" style="height: 18px;" class="me-2" /> Check In
            </Button>

        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted } from '@/plugin';
const dialogRef = inject("dialogRef");
const rs = inject("$reservation_stay")
const isConfirm = ref(false)
const moment = inject("$moment")

const reservationStays = ref([])

function onOk() {
    dialogRef.value.close("Ok");
}

onMounted(() => {
    if (dialogRef.value.data?.stays){
        reservationStays.value = dialogRef.value.data.stays;
    }
    
    if (reservationStays.value.length==0) {
        rs.getRoomRate(rs.reservationStay.name);
    }
});
</script>