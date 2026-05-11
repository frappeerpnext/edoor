<template>
    <div>
       Congratulations, you have successfully uploaded all data to the Channel Manager. From now on, any changes to reservations, rates, restrictions, or extra service prices will be automatically synchronized between the PMS and the Channel Manager in both directions.

      <!-- Footer -->
    <div>
  <Button 
    @click="onChangeDataUploadStep(-1)" 
    
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <Button 
    @click="onClose" 
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Go to Channel Manager Dashboard')"
  />
</div>

    </div>
</template>
<script setup>
import { onMounted } from 'vue';
import { useCMDashboard } from '../../../hooks/useCMDashboard';

const {onChangeDataUploadStep,onRefresh} = useCMDashboard();

async function onClose(){
    await onRefresh(true);
    
}

onMounted(async ()=>{
  const l = await window.showLoading();
  const res = await app.postApi("edoor.channel_managers.utils.mark_channel_data_upload_as_complete",{
    property:window.property_name
  },"",false)  
  
  l.close()
})
</script>