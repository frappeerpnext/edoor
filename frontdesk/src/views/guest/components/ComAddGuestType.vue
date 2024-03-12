<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
    <div class="grid">
      <div class="col-12">
      <label>{{ $t('Guest Type') }} </label>
      <InputText class="w-full" type="text" v-model="guestType.customer_group_en" :placeholder="$t('Guest Type')"/>
      </div>
      <div class="col-12">
        <label>{{ $t('Note') }} </label>
        <Textarea class="w-full" v-model="guestType.note" rows="5" cols="50" />
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup> 
import { onMounted,ref,inject,createUpdateDoc } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
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
  createUpdateDoc('Customer Group',guestType.value,null,rename.value)
  .then((r)=>{
    window.postMessage({action:"GuestList"},"*")
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
  if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
  if(dialogRef.value.data){
    guestType.value = JSON.parse(JSON.stringify(dialogRef.value.data)) 
  }
})

</script>