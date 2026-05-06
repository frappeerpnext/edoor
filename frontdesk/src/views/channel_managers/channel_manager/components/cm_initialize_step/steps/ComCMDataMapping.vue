<template>
    <div>
        data mapping info
        {{ channelManagerData }}

        
      <!-- Footer -->
    <div class="footer flex gap-2">
  <Button 
    @click="onChangeDataUploadStep(-1)" 
    class="btn-back" 
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <Button 
    @click="onChangeDataUploadStep(1)" 
    class="btn-next" 
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Next')"
  />
</div>

    </div>
</template>
<script setup>
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';

const {channelManagerData,onChangeDataUploadStep} = useCMDashboard()
</script>