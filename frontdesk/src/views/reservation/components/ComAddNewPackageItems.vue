<template>
    <ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
        <div class="grid">
        <div class="col-6">
          <label class="white-space-nowrap">{{ $t('Account Code') }}</label><br />
          <ComAutoComplete v-model="data.account_code" 
                           placeholder="Select Account Code"
                           doctype="Account Code"
                           class="auto__Com_Cus w-full" 
                           :filters="{allow_post_inclusion: 1}"
                           :pageLength="20"
            />
        </div>
        <div class="col-6">
          {{$t('Posting Rule')}}
          <ComSelect  :clear="false" v-model="data.posting_rule" :options="['Everyday','Checked In Date','Checked Out Date']" />
        </div>
        <div class="col-6">
          {{$t('Charge Rule')}}
          <ComSelect  :clear="false"  v-model="data.charge_rule" :options="['Stay','Adult','Child','Pax']" />

        </div>
        <div class="col-6">
          {{$t('Rate')}}
          <ComInputCurrency classCss="w-full"  v-model="data.rate" />
        </div>
        <div class="col-6">
          {{$t('Adult Rate')}}
          <ComInputCurrency classCss="w-full"  v-model="data.adult_rate" />
        </div>
        <div class="col-6">
          {{$t('Child Rate')}}
          <ComInputCurrency classCss="w-full"  v-model="data.child_rate" />
        </div>
      </div>
    </ComDialogContent>
  </template>
  
  <script setup>
  import { inject , ref , postApi} from "@/plugin"
  const dialogRef = inject("dialogRef");
const rs = dialogRef.value.data.rs
  // Initialize data object
  const data = ref({posting_rule:"Everyday",charge_rule:'Stay'});
  
  function onSave() {
    // alert(23)
  }
  </script>
  