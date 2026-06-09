<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Re Sync Room Rate Now" :hideIcon="false">
 
    <template v-if="cmInfo?.provider == 'Exely'">
<div
  class="surface-card  border-round-xl p-4  flex gap-4 align-items-start"
>
  
  <!-- Icon -->
  <div
    class="bg-blue-500 text-white flex align-items-center justify-content-center border-round-xl w-4rem h-4rem flex-shrink-0"
  >
    <i class="pi pi-sync"></i>
  </div>

  <!-- Content -->
  <div class="flex-1">
    
    <div class="text-900 text-xl font-bold ">
      Before Resyncing Room Rates
    </div>

    <p class="text-600 line-height-3 mt-0">
      To resync room rates from the Channel Manager, please make sure
      the selected rate plans are enabled for PMS sync in the Exely backend first.
    </p>

    <!-- Path -->
    <div
      class="inline-flex align-items-center gap-2 bg-white  border-round-lg flex-wrap"
    >
      <span class="font-semibold text-blue-600">
        Integration
      </span>

      <i class="pi pi-angle-right text-500"></i>

      <span class="font-semibold text-blue-600">
        Sync of rate plans with PMS
      </span>
    </div>

    <p class="text-600 line-height-3 mt-0 mb-0">
      Then select the rate plans you want to send to PMS before starting
      the resync process.
    </p>

  </div>
</div>

 </template>

    </ComDialogContent>
    </template>
    <script setup>
import { useApp } from '@/hooks/useApp.js';
import { inject } from 'vue';

    const {cmInfo} = useApp();
    
    const dialogRef = inject("dialogRef");

    async function onOk(){
        const l = await window.showLoading()
        const res = await app.postApi("rate_plan.get_room_rate_from_channel_manager",{
            property:window.property_name
        },"",false)
        if (res.data){
            // 
            alert("show confirm for waiting to finish data from cm manager")
            dialogRef.value.close()
        }
        l.close()
        
    }
    </script>
