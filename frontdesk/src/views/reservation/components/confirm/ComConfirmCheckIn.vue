<template>
    <ComDialogContent :hideButtonClose="true" :hideButtonOK="true">
        <template v-if="rs.reservationStay.reservation_status=='No Show'">
            <Message severity="info">
                This reservation is a No Show reservation. If there is a No Show charge, please adjust it in the folio after check-in. Room revenue will only be included from today onward.
            </Message>
        </template>
        <template v-else>
            <div v-if="rs.room_rates?.length > 0 && reservationStays?.length==0">
                <Message :severity="rs.room_rates[0].total_rate==0?'warn':'info'"> Room rate on {{ moment(rs.room_rates[0].date).format('DD-MM-YYYY') }} is
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
    
        </template>

        <label for="reason-text" class="mb-1 font-medium block">Note</label>
        <Textarea autofocus v-model="note" id="reason-text" rows="3" cols="50" placeholder="Please enter check in note" class="w-full" />


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
import { onUnmounted } from 'vue';
import { useConfirm } from "primevue/useconfirm";
const dialogRef = inject("dialogRef");
const rs = inject("$reservation_stay")
const isConfirm = ref(false)
const note = ref()
const moment = inject("$moment")
const confirm = useConfirm();
const reservationStays = ref([])

function onOk() {
    if(reservationStays?.length==0 && rs.room_rates[0].total_rate==0){
        confirm.require({
        message: 'Are you sure you want to proceed Check In with rate 0?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {
            dialogRef.value.close({"note":note.value});
        },
         
    });
    }else {
        dialogRef.value.close({"note":note.value});
    }
    
}

onMounted(() => {
    if (dialogRef.value.data?.stays){
        reservationStays.value = dialogRef.value.data.stays;
    }
    
    if (reservationStays.value.length==0) {
        rs.getRoomRate(rs.reservationStay.name);
    }
});
onUnmounted(()=>{
    window
})
</script>