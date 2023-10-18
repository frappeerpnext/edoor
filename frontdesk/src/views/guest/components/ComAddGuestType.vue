<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
    <div class="grid">
      <div class="col-12">
      <label>Guest Type</label>
      <InputText class="w-full" type="text" v-model="guestType.customer_group_en" />
      </div>
      <div class="col-12">
        <label>Note</label>
        <Textarea class="w-full" v-model="guestType.note" rows="5" cols="50" />
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup> 
import { onMounted,ref,inject,createUpdateDoc } from '@/plugin';

const dialogRef = inject('dialogRef') 
const gv = inject('$gv') 
const loading = ref(false)
const rename = ref(null)
const guestType = ref({});

function onSave(){
  if(!guestType.value.customer_group_en){
    gv.toast('warn','Please input guest type name.')
    return
  }
  loading.value = true
  rename.value = null
  if(dialogRef.value.data){
    rename.value = {
      old_name: dialogRef.value.data.name,
      new_name: guestType.value.customer_group_en
    } 
  }
  createUpdateDoc('Customer Group', {data:guestType.value},null,rename.value)
  .then((r)=>{
    // window.socket.emit("RefreshData", { property:setting.property.name , action: "refresh_guest_type" })
    window.socket.emit("GuestList", window.property_name)
    window.socket.emit("GuestType", window.property_name)

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
    guestType.value = JSON.parse(JSON.stringify(dialogRef.value.data)) 
  }
})

</script>