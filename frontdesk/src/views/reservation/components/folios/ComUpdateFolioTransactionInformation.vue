<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save" :hideIcon="false" :loading="loading">
        <Stack>
            <div>
                <label for="ref">{{ $t('Reference Number') }}</label>
                <InputText id="ref" class="w-full" type="text" v-model="doc.reference_number" />
    </div>
    
    <div>
        
        <label for="reason-text" class="mb-1 font-medium block">Note</label>
        <Textarea v-model="doc.note" id="reason-text" rows="3" cols="50" placeholder="Note" class="w-full"/>
    
    </div>  
    </Stack>
        
    </ComDialogContent>

</template>
<script setup>
import { onMounted,inject, ref,getDoc,updateDoc } from "@/plugin"

const dialogRef = inject("dialogRef");
const loading = ref(false)

const doc = ref({})
function onOk(){
   loading.value = true;
   updateDoc("Folio Transaction", dialogRef.value.data.folio_transaction_number, doc.value).then(result=>{
    dialogRef.value.close(true);
    loading.value = false;
   }).catch(err=>{
    loading.value = false;
   })
            
        
    
}
onMounted(()=>{
   
    loading.value = true
    getDoc("Folio Transaction",dialogRef.value.data.folio_transaction_number).then(d=>{
        doc.value = d
        loading.value = false
    }).catch(err=>{
        loading.value = false

    })
})
</script>