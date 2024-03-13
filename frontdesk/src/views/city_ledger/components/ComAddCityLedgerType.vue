<template>
  <ComDialogContent :loading="loading" @onClose="onClose" @onOK="onSave()">
    <div class="grid">
      <div class="col-12">
          <label>{{ $t('City Ledger Type') }}</label>
          <InputText class="w-full" type="text" v-model="accountType.city_ledger_type" />
      </div>
      <div class="col-12">
        <label> {{ $t('Note') }} </label>
        <Textarea class="w-full" v-model="accountType.note" rows="5" cols="50" />
      </div>
    </div>
</ComDialogContent> 
</template>

<script setup>
import { onMounted,ref,inject,createUpdateDoc  } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialogRef = inject('dialogRef')
const gv = inject('$gv')
const accountType = ref({})
const loading = ref(false)
const rename = ref(null)
 
function onSave(){
  if(!accountType.value.city_ledger_type){
    gv.toast('warn','City ledger type is required.')
    return
  }
  loading.value = true
  rename.value = null
  if(dialogRef.value.data){
    rename.value = {
      old_name: dialogRef.value.data.name,
      new_name: accountType.value.city_ledger_type
    } 
  }
  createUpdateDoc('City Ledger Type', accountType.value,null,rename.value).then((r)=>{
    dialogRef.value.close(r)
    loading.value = false
    window.postMessage({action:"CityLedgerType"},"*")
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
    accountType.value = JSON.parse(JSON.stringify(dialogRef.value.data))
  }
})
</script>