<template>
    <div>
        
             <com-confirm-message label="Verify Availability"
            text="Please review and verify the availability details below before proceeding." />
 
<Message v-if="dataUploadStatus?.availability?.status == 'In Progress'">
   We are currently processing your room availability data in the background. Please wait until the upload to the channel manager is completed.
</Message>

        <div class="availability-wrapper" v-if="dataUploadStatus"> 
            <div class="availability-title">{{ $t('AVAILABILITY') }}</div>
            <com-availability 
            @onClick="onViewAvailabilityData(rt.room_type)"
            v-for="(rt, index) in dataUploadStatus.availability.room_types" :key="index"
                :room-type-name="rt.room_type_name" :room-type-code="rt.room_type_code"
                :total-room="rt.total_room" :day-cover="365"
                 >
                <template #status>
 
                    <i v-if="rt.status=='Pending'" class="pi pi-check bg-gray-500 text-white p-2 border-circle"></i>
                    <i v-else-if="rt.status=='In Progress'" class="pi pi-spin pi-spinner bg-gray-500 text-white p-2 border-circle"></i>
                    <i v-else class="pi pi-check bg-green-500 text-white p-2 border-circle"></i>
                                        
                    
                </template>
                </com-availability>
        </div>
        <Checkbox 
  v-model="iAgree" 
  :binary="true" 
  inputId="iAgree"
  
/>
<label for="iAgree" class="ml-2 cursor-pointer">
  By checking this box, you confirm that all room availability information is accurate.
</label>
        <div class="footer flex gap-2">
            <Button @click="onChangeDataUploadStep(-1)" 
             :disabled="dataUploadStatus?.availability.status == 'In Progress'"
            class="btn-back" icon="pi pi-arrow-left" :label="$t('Back')" />
            <Button  @click="onViewAvailabilityData('')"   icon="pi pi-eye" :label="$t('View Availability')" />
            
            <Button @click="onUploadRestrictionData"  
            v-if="dataUploadStatus?.availability.status != 'Complete' && dataUploadStatus.availability.sync_mode == 'Receive from PMS'"
            :loading="dataUploadStatus?.availability.status == 'In Progress'"
             severity="danger" 
            icon="pi pi-cloud-upload" 
            :label="$t('Upload Availability Now')" />
            
            
            <Button @click="onChangeDataUploadStep(1)"
            v-if="dataUploadStatus?.availability.status == 'Complete'"
             class="btn-next" icon="pi pi-arrow-right" 
             iconPos="right"
                :label="$t('Next')" />
                
        </div>

    </div>

</template>
<script setup>
import ComAvailability from '@/views/channel_managers/channel_manager/components/ComAvailability.vue';

import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';
import { ref } from 'vue';
const {
    onChangeDataUploadStep,
    dataUploadStatus
} = useCMDashboard();
 const iAgree = ref(false)


async function onUploadRestrictionData(){
    
     
    if (!iAgree.value) {
      
    app.utils.showWarning("Upload Room Availability","Please confirm that the room availability information is accurate by checking the agreement box.");
    return;
}
    const result = await app.utils.onConfirm("Upload Room Availability", "Are you sure you want to upload room availability to Channel Manager now?")
    if (result){
        

        const l = await window.showLoading()
        const res = await app.postApi("room_availability.initialized_availability_upload",{
            property:window.property_name
        }) 
        if (res.data){
           
            dataUploadStatus.value.availability.status = "In Progress"
        dataUploadStatus.value.availability.room_types.forEach(rt=>{
            rt.status ='In Progress'
        })
        }

        l.close()
    }
    
}

function onViewAvailabilityData(room_type = ""){
    app.dialog.viewAvailabilityData("View Room Availability Data",{"room_type":room_type})
}




</script>
<style scoped>
.availability-wrapper {
    margin-top: 20px;
    /* padding: 20px; */
    border-radius: 16px;
    /* background: #ffffff; */
    /* box-shadow: 0 10px 30px rgba(0,0,0,0.05); */
    font-family: 'Segoe UI', sans-serif;
}

.availability-title {
    font-size: 14px;
    font-weight: 600;
    color: #7b8190;
    margin-bottom: 15px;
    letter-spacing: 0.5px;
}
</style>