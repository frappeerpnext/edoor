<!-- <template>
      <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
          City Ledger Type
            <div class="card flex justify-content-left">
                <InputText type="text" v-model="accountType.city_ledger_type" />
            </div><br>
            Note
            <div class="card flex justify-left">
                 <Textarea v-model="accountType.note" rows="5" cols="50" />
            </div><br>
          </ComDialogContent>
</template>

<script setup>
import { ref,createUpdateDoc ,useDialog} from '@/plugin' 
const accountType = ref({});
const gv = inject("$gv")
const dialog = useDialog()

function onSave (){ 
  alert ()
  loading.value = true
  createUpdateDoc("City Ledger Type", {data: accountType.value}).then((r)=>{
    loading.value = false
    dialog.value.close(r)
  }).catch((err)=>{
    loading.value = false
  })
}

</script> -->

<template>
sdhfklsh
</template>

<script setup>

</script>