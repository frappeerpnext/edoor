<template>
    <ComDialogContent  :loading="isLoading" hideButtonClose>
    {{ doc }}
    </ComDialogContent>

</template>
<script setup>
import {ref,getDoc,inject,onMounted } from "@/plugin"
const dialogRef = inject("dialogRef");
 
    const doc = ref({})
    const isLoading = ref(false) 


  onMounted(() => {
   
  if(dialogRef.value.data.folio_transaction_number){
     
    isLoading.value = true
    getDoc("Folio Transaction", dialogRef.value.data.folio_transaction_number)
    .then((result)=>{
        doc.value =result
        isLoading.value = false
    }).catch((err)=>{
        isLoading.value = false
    })
  }
  })
</script>