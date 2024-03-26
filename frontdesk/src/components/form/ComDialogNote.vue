<template>
    <ComDialogContent @onOK="onOk" hideButtonClose :titleButtonOK="Ok" :hideIcon="false" :loading="loading">
        <Message v-if="data?.confirm_message">
            <div v-html="$t(data?.confirm_message)" />
        </Message>

        <label for="reason-text" class="mb-1 font-medium block"> {{ $t('Reason') }} </label>
        <Textarea autofocus v-model="note" id="reason-text" rows="3" cols="50" :placeholder=" $t('Please Enter Reason') " class="w-full" />
        <div v-if="data?.data.show_reserved_room" class="py-2">
            <Checkbox inputId="no_show_sell_room" v-model="data.data.reserved_room" :binary="true" />
            <label for="no_show_sell_room" class="ml-1 cursor-pointer">{{ $t('Reserved room for this reservation.') }} </label>
        </div>

    </ComDialogContent>
</template>
<script setup>
import Message from 'primevue/message';
import { ref, onMounted, inject, postApi, deleteApi,updateDoc } from '@/plugin'
import { useToast } from "primevue/usetoast";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const toast = useToast();
const dialogRef = inject("dialogRef");
const rs = inject("$reservation_stay")
const emit = defineEmits(['onOk', 'onClose'])
const data = ref()
const note = ref("")
const loading = ref(false)

function onOk() {
    if (!note.value) {
        toast.add({ severity: 'warn', summary: 'Enter Note', detail: "Please Enter Note", life: 3000 })
        return
    }
    loading.value = true

    data.value.data.note = note.value

    if(data.value.note_field){
        data.value.data[data.value.note_field] = note.value  
    }
   

    if (data.value.method == "POST") {
        postApi(data.value.api_url, data.value.data).then((r) => {
            loading.value = false
            dialogRef.value.close({note:note.value,data:r})
            onLoadSocket()            
        }).catch(() => {
            loading.value = false
        })
    } else if(data.value.method=="PUT") {
        updateDoc(data.value.api_url,data.value.name , data.value.data).then(r=>{
            loading.value = false
            dialogRef.value.close({note:note.value,data:r})
            onLoadSocket()

        }).catch(() => {
            loading.value = false
          
        })

    } else if(data.value.method=="DELETE") {
        
        deleteApi(data.value.api_url, data.value.data)
        .then((r) => {
            loading.value = false
            dialogRef.value.close({note:note.value,data:r})
            onLoadSocket()

        }).catch(() => {
            loading.value = false
        })
    }
}
function onLoadSocket(){ 
    window.postMessage({action:"Dashboard"},"*")
    window.postMessage({action:"ReservationList"},"*")
    window.postMessage({action:"ReservationStayList"},"*")
    if (!dialogRef.value.data.disable_reload_frontdesk){
        window.postMessage({action:"Frontdesk"},"*")
    }

    window.postMessage({action:"TodaySummary"},"*")
    window.postMessage({action:"GuestLedger"},"*")
    window.postMessage({action:"GuestLedgerTransaction"},"*")
    window.postMessage({action:"Reports"},"*")
    window.postMessage({action:"ReservationDetail"},"*")
    window.postMessage({action:"FolioTransactionList"},"*")
    window.postMessage({action:"PayableLedger"},"*")

    if(data.value.data.stays && data.value.data.stays.length > 0){
        data.value.data.stays.forEach(r => { 
            window.postMessage({action:"ReservationStayDetail"},"*")
        });
    }
}

onMounted(() => {
    data.value = dialogRef.value.data;
})

</script>
<style lang="">
    
</style>