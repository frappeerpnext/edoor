<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
     Guest Type
   <div class="card flex justify-content-left">
      <InputText type="text" v-model="guestType.customer_group_en" />
    </div><br>
      Note
    <div class="card flex justify-left">
      <Textarea v-model="guestType.note" rows="5" cols="50" />
    </div><br>
  </ComDialogContent>
</template>

<script setup> 
import { onMounted,ref,inject,createUpdateDoc,getDoc  } from '@/plugin';
const dialogRef = inject('dialogRef')
const accountType = ref({})
const loading = ref(false)

function onSave(){
  loading.value = true
  createUpdateDoc("Customer Group", {data: guestType.value}).then((r)=>{
    dialogRef.value.close(r)
    
  }).catch((err)=>{
    loading.value = false
  })
}

function onClose(){
  dialogRef.value.close()
}

onMounted(() => {
  if(dialogRef.value.data?.name){
    loading.value = true
    getDoc("City Ledger Type",dialogRef.value.data?.name).then((doc)=>{
      accountType.value = doc
      loading.value = false
    }).catch((err)=>{
      loading.value = false    
    })
  }
})

</script>