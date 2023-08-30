<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
    <div class="grid">
      <div class="col-12">
      <label>
      Business Source Type
      </label>
      <InputText class="w-full" type="text" v-model="businesssourceType.business_source_type" />
      </div>
      <div class="col-12">
        <label>
        Note
        </label>
        <Textarea class="w-full" v-model="businesssourceType.note" rows="5" cols="50" />
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup> 
import { onMounted,ref,inject,createUpdateDoc } from '@/plugin';
const dialogRef = inject('dialogRef') 
const loading = ref(false)
const rename = ref(null)
const businesssourceType = ref({});

function onSave(){
  loading.value = true
  rename.value = null
  if(dialogRef.value.data){
    rename.value = {
      old_name: dialogRef.value.data.name,
      new_name: businesssourceType.value.business_source_type
    } 
  }
  createUpdateDoc('Business Source Type', {data:businesssourceType.value},null,rename.value).then((r)=>{
    dialogRef.value.close(r)
    loading.value = false
  }).catch((er)=>{
    loading.value = false
  })
}
function onClose(){
  dialogRef.value.close()
}
onMounted(() => {
  if(dialogRef.value.data){
    businesssourceType.value = JSON.parse(JSON.stringify(dialogRef.value.data)) 
  }
})

</script>