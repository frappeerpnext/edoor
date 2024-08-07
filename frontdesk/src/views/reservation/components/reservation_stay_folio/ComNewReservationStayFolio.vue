<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
    {{ doc }}
        <div class="grid">
       

            <div class="col-6 pb-0" v-if="guests && doc">
                <label>
                    {{ $t('Stay Guest') }}
                    </label><br/>
                <ComSelect class="mb-3 w-full" v-model="doc.guest" :options="guests" optionLabel="guest_name" optionValue="name" :clear="false" />
            </div>    
             <div class="col-6 pb-0">
                <label>
                    {{ $t('Folio Type') }}
                    </label><br/>
                    <ComAutoComplete v-model="doc.folio_type" 
                           placeholder="Select Folio Type"
                           doctype="Folio Type"
                           class="auto__Com_Cus w-full" 
                           />
            </div>
           
            <div class="col-12 pt-0">
                <label >{{$t('Note')}}</label><br/>
                <Textarea v-model="doc.note" rows="3"  class="w-full"/>
            </div>
            <div class="col-12">
                <div class="flex justify-item-center">
                  <Checkbox v-model="doc.show_in_pos_transfer" inputId="show_in_pos_transfer" :binary="true" :trueValue="1" :falseValue="0" />
                  <label class="white-space-nowrap ms-2 cursor-pointer" for="show_in_pos_transfer">Show In Pos Transfer</label>
                  
                </div>
                
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
const doc = ref({show_in_pos_transfer:1})
const guests = ref([])
const gv = inject("$gv")
function onSave() {
  
    if(!gv.cashier_shift?.name){
        gv.toast('warn', 'Please Open Cashier Shift.')
        return
    }
    isSaving.value = true
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