<template>
  <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="grid">
            <div class="col-6">
                <label>{{$t('Taken Date')}} </label>
                <Calendar disabled selectOtherMonths class="w-full" showIcon v-model="data.taken_date" :manualInput="false" :min-date="working_day" dateFormat="dd-mm-yy"/>
            </div>
           <div class="col-6">
            <label>{{ $t('Taken By') }}</label>
            <InputText type="text" class="p-inputtext-sm w-full" :placeholder=" $t('Taken By') "
            v-model="data.taken_by" :maxlength="50" />
           </div>
           <div class="col-12">
                <label>{{ $t('Note') }}</label>
                <Textarea v-model="data.taken_note" rows="5" :placeholder="$t('Note')" cols="30"
                    class="w-full border-round-xl" />
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, updateDoc, getApi, onMounted } from '@/plugin';
const dialogRef = inject('dialogRef');
const moment = inject('$moment');
const data = ref({})
function onSave(){
    data.value.is_taken = 1
    if (dialogRef.value.data.name) {
        data.value.taken_date = moment(dialogRef.value.data.posting_date).format('YYYY-MM-DD') 
    }else{
         data.value.taken_date = moment().format('YYYY-MM-DD')
    }
    updateDoc("Lost and Found",dialogRef.value.data.name , data.value).then(r=>{
        window.postMessage({"action":"LostAndFoundList"},"*")  
        dialogRef.value.close(r)
        }).catch(() => {
            
        })
}
onMounted(() => {
    if (dialogRef.value.data.name) {
    data.value.taken_date = moment(dialogRef.value.data.posting_date).format('DD-MM-YYYY') 
    data.value.taken_by = dialogRef.value.data.taken_by
    data.value.taken_note = dialogRef.value.data.taken_note
    }else{
        data.value.posting_date = moment().format('DD-MM-YYYY') 
    }
   
});
</script>