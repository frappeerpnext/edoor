<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Save" :hideIcon="false" :loading="loading">
        <Stack>
            <div v-if="invoice_description">
                <label for="ref">{{ $t('Invoice Description') }}</label>
                <Textarea  id="ref" class="w-full" type="text" v-model="doc.invoice_description" />
            </div>
            <div v-else>
   <div>
                <label for="ref">{{ $t('Reference Number') }}</label>
                <InputText id="ref" class="w-full" type="text" v-model="doc.reference_number" />
    </div>
    
    <div>
        
        <label for="reason-text" class="mb-1 font-medium block">Note</label>
        <Textarea v-model="doc.note" id="reason-text" rows="3" cols="50" placeholder="Note" class="w-full"/>
    
    </div>                 
            </div>
          
    </Stack>
        
    </ComDialogContent>

</template>
<script setup>
import { onMounted,inject, ref,getDoc,updateDoc } from "@/plugin"

const dialogRef = inject("dialogRef");
const loading = ref(false)
const invoice_description = ref(dialogRef.value.data.invoice_description)
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