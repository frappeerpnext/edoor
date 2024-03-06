<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid">
            <div class="col-4" v-if="guests && doc">
                <label>
                    {{ $t('Stay Guest') }}
                    </label><br/>
                <ComSelect class="mb-3 w-full" v-model="doc.guest" :options="guests" optionLabel="guest_name" optionValue="name" :clear="false" />
            </div>
           
            <div class="col-8">
                <label hidden>{{$t('Note')}}</label><br/>
                <InputText placeholder="Note" class="w-full" type="text" v-model="doc.note" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted,createUpdateDoc,getDoc } from "@/plugin"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const doc = ref({})
const guests = ref([])
const gv = inject("$gv")

function onSave() {
    isSaving.value = true
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    createUpdateDoc('Reservation Folio', doc.value)
    .then((doc) => {
        dialogRef.value.close(doc)
        isSaving.value = false
        window.postMessage({action:"ReservationStayDetail"},"*")
        window.postMessage({action:"GuestLedger"},"*")
        window.postMessage({action:"GuestLedgerTransaction"},"*")
        window.postMessage({action:"ReservationDetail"},"*")
    }).catch(()=>{
        isSaving.value = false
    })
}


onMounted(() => {
    doc.value = dialogRef.value.data 
    getDoc("Reservation Stay", doc.value.reservation_stay).then((result)=>{
        guests.value.push({
            name: result.guest,
            guest_name: result.guest_name,
        })
        if(result.additional_guests && result.additional_guests.length > 0){
            result.additional_guests.forEach(r => {
                guests.value.push({
                    name: r.guest,
                    guest_name: r.guest_name
                })
            });
        }
        
    })
});


</script>