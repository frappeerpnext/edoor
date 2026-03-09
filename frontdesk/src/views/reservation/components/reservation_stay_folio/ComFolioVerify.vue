<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>  
        <div class="grid">
            <div class="col-12">
                <div class="flex gap-2">
                    <label for="mark_as_verify">{{$t('Mark as Verified')}}</label><br/>
                    <Checkbox inputId="mark_as_verify" v-model="doc.mark_as_verified" :binary="true" :trueValue="1" :falseValue="0" /> 
                </div>
            </div>
            <div class="col-6"> 
                <label>{{$t('Verified Date')}}</label><br/>
                <Calendar :disabled="!doc.mark_as_verified" class="w-full" :showButtonBar="true" v-model="doc.verified_date" placeholder="Verified Date"
                        dateFormat="dd-mm-yy" showIcon panelClass="no-btn-clear"/>
            </div>
            <div class="col-6">
                <label>{{$t('Verified Amount')}}</label><br/>
                <ComInputCurrency :disabled="!doc.mark_as_verified" classCss="w-full" v-model="doc.verified_amount" />
            </div>
            <div class="col-12">
                <label>{{$t('Verified Note')}}</label><br/>
                <Textarea :disabled="!doc.mark_as_verified" v-model="doc.verified_note" rows="3" 
                class="w-full" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted , updateDoc , getDoc } from "@/plugin";
const dialogRef = inject("dialogRef");
const moment = inject("$moment")
const doc = ref({});
const loading = ref(false);
const isSaving = ref(false); 


function onSave(){ 
    
    if (doc.value.mark_as_verified == 0) {
        doc.value.verified_amount = 0
        doc.value.verified_note = ""
        doc.value.verified_date = undefined
    }else{
        doc.value.verified_date = moment(doc.value.verified_date).format("yyyy-MM-DD")
    }
    isSaving.value = true;
    updateDoc("Reservation Folio", dialogRef.value.data.name, doc.value).then(result=>{
    dialogRef.value.close(true);
    isSaving.value = false;
   }).catch(err=>{
    isSaving.value = false;
    window.postMessage({action:"load_reservation_folio_list"},"*")
    window.postMessage({action:"load_reservation_stay_folio_list"},"*")
    window.postMessage({action:"ReservationDetail"},"*")
   })
}
onMounted(() => {  
    getDoc("Reservation Folio",dialogRef.value.data.name).then(d=>{
        doc.value = d
        if (doc.value.mark_as_verified == 0) {
            doc.value.verified_amount = doc.value.balance
        } 
        console.log(doc.value.verified_date)
        if (doc.value.verified_date != undefined) {
            doc.value.verified_date = moment(d.verified_date).toDate()
        }
        isSaving.value = false
    }).catch(err=>{
        isSaving.value = false
    })
});
</script>