<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
    <div class="grid">
      <div class="col-12">
        <label>{{ $t('Business Source Type') }} </label>
        <InputText class="w-full" type="text" v-model="businesssourceType.business_source_type" />
      </div>
      <div class="col-12">
        <label> {{ $t('Note') }} </label>
        <Textarea class="w-full" v-model="businesssourceType.note" rows="5" cols="50" />
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup> 
import { onMounted,ref,inject,createUpdateDoc } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
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
  createUpdateDoc('Business Source Type', businesssourceType.value,null,rename.value).then((r)=>{
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
    businesssourceType.value = JSON.parse(JSON.stringify(dialogRef.value.data)) 
  }
})

</script>