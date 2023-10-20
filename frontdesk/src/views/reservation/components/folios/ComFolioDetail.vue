<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" :loading="loading">
 
        {{ doc }}

        <hr/>
        <div v-if="doc"> 
            <ComFolioAction :folio="doc" />
            <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="doc" />
            <ComFolioTransactionSimpleStyle v-else :folio="doc" />
        </div>

    </ComDialogContent>
</template>
<script setup>
 
import { ref, onMounted, inject, getDoc } from '@/plugin'
import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"
const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)

const name = ref()
const doc = ref()

const dialogRef = inject("dialogRef");
 
 
const loading = ref(false)



function onOk() {
   
  
    dialogRef.value.close(note.value)
            
}

function getData(){
    loading.value = true
    getDoc("Reservation Folio",name.value).then(r=>{
        doc.value = r
        loading.value = false
    }).catch(err=>{
        loading.value = false
    })
}

onMounted(() => {
    name.value = dialogRef.value.data.name;
    getData()
})




</script>
<style lang="">
    
</style>