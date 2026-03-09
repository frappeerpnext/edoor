<template>
     <ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
    <div class="grid">
        <div class="col-6" >
        <label class="white-space-nowrap">{{ $t('Account Code') }}</label><br />
        <ComAutoComplete  v-model="data.account_code" 
                            placeholder="Select Account Code"
                            doctype="Account Code"
                            class="auto__Com_Cus w-full" 
                            @onSelected="onSelectAccountCode"
                            :pageLength="20"
                            />
        </div>
        <div class="col-6">
            {{$t('Posting Rule')}}
            <InputText type="text" class="p-inputtext-sm w-full" v-model="data.posting_rule" :maxlength="100" />
        </div>
        <div class="col-6">
            {{$t('Charge Rule')}}
            <InputText type="text" class="p-inputtext-sm w-full" v-model="data.charge_rule" :maxlength="100" />
        </div>
        <div class="col-6">
            {{$t('Charge Rule')}}
            <InputText type="text" class="p-inputtext-sm w-full" v-model="data.charge_rule" :maxlength="100" />
        </div>
        <div class="col-4">
            {{$t('Rate')}}
            <ComInputCurrency classCss="w-full"  v-model="data.rate" />
        </div>
        <div class="col-4">
            {{$t('Adult Rate')}}
            <ComInputCurrency classCss="w-full"  v-model="data.adult_rate" />
        </div>
        <div class="col-4">
            {{$t('Child Rate')}}
            <ComInputCurrency classCss="w-full"  v-model="data.child_rate" />
        </div>
      <!-- Add more properties as needed -->
    </div>
</ComDialogContent>
  </template>
  
  <script setup>
  import { inject} from "@/plugin"
const dialogRef = inject("dialogRef");
const data = dialogRef.value.data.data
function onSave() {
   
}
  </script>
  