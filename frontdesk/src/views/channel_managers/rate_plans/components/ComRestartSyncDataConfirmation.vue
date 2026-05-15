<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" >
        <div class="sync-error-container p-4 border-round shadow-1">
    <!-- Header with Icon -->
    <div class="flex align-items-center mb-3 text-red-600">
      <i class="pi pi-exclamation-triangle mr-2 text-2xl"></i>
      <h3 class="m-0 font-bold">
        {{ $t("Sync to Channel Manager has been stopped") }}
      </h3>
    </div>

    <!-- Error Detail Box -->
    <div class="error-details p-3 mb-3 bg-red-50 border-left-3 border-red-500">
      <p class="m-0 font-medium text-red-700">
        {{ data?.response_text || $t("Unknown error occurred.") }}
      </p>
    </div>

    <!-- Instructions -->
    <div class="instructions mb-4 text-secondary line-height-3">
      <p>
        {{ $t("Please review and resolve all issues. These problems may be caused by misconfiguration or incorrect data mapping between the PMS and the Channel Manager.") }}
      </p>
    </div>

    <!-- Confirmation Action -->
    <div class="confirmation-footer p-3 bg-gray-50 border-round flex align-items-center">
      <Checkbox 
        inputId="checked" 
        v-model="isChecked" 
        :binary="true" 
        class="mr-2"
      />
      <label for="checked" class="cursor-pointer font-semibold selection-none">
        {{ $t("I confirm that I have reviewed and resolved all issues.") }}
      </label>
    </div>
  </div>
        
    </ComDialogContent>
</template>
<script setup>

import { useRatePlan } from "@/views/channel_managers/rate_plans/hooks/useRatePlan.js";
 import { i18n } from '@/i18n';
import { inject, onMounted, ref } from "vue";
const { t: $t } = i18n.global;
const isChecked = ref(false)
const data = ref()
const dialogRef = inject("dialogRef");
 


async function onOk(){

    if (!isChecked.value){
        app.utils.showWarning("Please checked checkbok","I confirm that I have reviewed and resolved all issues.", 3000,"confirm_checkbox_resync")
        return
    }
   
   

    const l = await window.showLoading()
    // export function postApi(api, params = Object, message,show_message=true,base_url="edoor.api."){
    
    const resp = await app.postApi(
        "resync_data.restart_sync_data_to_channel_manager",
        {
            property: data.value.property,
            request_type: data.value.request_type,
            
        },
        "",//message
        false,//hide message
        "edoor.channel_managers."//base url
    )
    l.close();
    if (resp.data){
        

        app.utils.onConfirm("Confirmation","Data sync to the channel manager is running in the background.<br/> You will be notified when it is complete, or you can check the status by clicking the  <strong>View Sync Status</strong> button.")
        dialogRef.value.close();
    }

    

    
}
onMounted(()=>{
    data.value =   dialogRef.value.data.data
})
</script>