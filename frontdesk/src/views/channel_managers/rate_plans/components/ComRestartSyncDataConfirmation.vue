<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" >
        <strong>{{ $t("Sync to Channel Manager has been stopped due to the following problems:") }}</strong>
        <div>
            
            {{ data?.response_text }}
        </div>
        <div>
            {{ $t("Please review and resolve all issues. These problems may be caused by misconfiguration or incorrect data mapping between the PMS and the Channel Manager.") }}
        </div>
        <div>

            <Checkbox inputId="checked" v-model="isChecked" :binary="true"  />  <label for="checked">{{ $t("I confirm that I have reviewed and resolved all issues.") }}</label>
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
            title: data.value.title,
            
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