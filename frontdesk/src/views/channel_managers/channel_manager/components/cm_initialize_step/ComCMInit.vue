<template>
    <template v-if="hideInitButton != true">
        <div class="absolute top-50 left-50 text-center" style="transform: translate(-50%, -50%);">
            <div class="card">

                <div class="logo-container grid">
                    <div class="col-5 flex justify-content-end"> 
                        <Image :src="data.edoor_logo" :alt="data.name" :width="data.edoor_logo_width || '50'" /> 
                    </div>
                    <div class="arrow text-5xl col-2 text-center">⇄</div>
                    <div class="col-5">
                        <Image :src="data.provider_logo" :alt="data.provider" :width="data.provider_logo_width || '80'" /> 
                    </div>
                </div>

                <button class="btn" @click="startInitializeData">
                {{$t(`Initialize Data Upload to ${data.provider || ''}`)}}
                </button>

                <p class="description">
                    {{$t(`Please click the button above to initiate the data initialization process for the channel manager. This will synchronize your property data with ${data.provider || ''}.`)}}
                </p>

            </div>

        </div>
    </template>
    <template v-if="showWizardBox == true">
        <ComInitializeWizardStep />
    </template>

</template>
<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

import Image from 'primevue/image';

import ComInitializeWizardStep from "@/views/channel_managers/channel_manager/components/cm_initialize_step/ComInitializeWizardStep.vue"
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';
const data = ref({})
const {
    channelManagerData,
    getDataUploadStatus,
    dataUploadStatus
} = useCMDashboard();

const showWizardBox = ref(false)
const hideInitButton = ref(false)

const startInitializeData = async () => {
    const l = await window.showLoading()
 
        showWizardBox.value = true
        hideInitButton.value = true
        l.close()    
 

    
}

function socketEvent (arg){
    if(arg.action == "update_channel_manager_data_upload_status" && arg.property == window.property_name){
        dataUploadStatus.value = arg.upload_status;
    }
}


onMounted(async() => {
    data.value = channelManagerData.value
    if (!dataUploadStatus.value){
        const l  = await window.showLoading();
        await getDataUploadStatus()
        l.close()
    }

    window.socket.on("ChannelManagerUpdate",socketEvent)

})

onUnmounted(()=>{
    window.socket.off("ChannelManagerUpdate",socketEvent)
})

 
</script>
<style scoped>
.card {
    background: #ffffff;
    padding: 40px 30px;
    border-radius: 20px;
    width: 420px;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.08);
    transition: 0.3s ease;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.12);
}

.logo-container {
    /* display: flex;
    justify-content: center; */
    align-items: center;
    /* gap: 12px; */
    margin-bottom: 25px;
}

.logo-box {
    width: 50px;
    height: 50px;
    background: #3f51b5;
    border-radius: 12px;
    display: flex;
    justify-content: center;
    align-items: center;
    color: white;
    font-weight: bold;
    font-size: 20px;
}

.arrow {
    font-size: 20px;
    color: #6b7280;
}

.brand {
    font-weight: 600;
    color: #6b21a8;
    font-size: 18px;
}

.btn {
    margin: 20px 0;
    padding: 12px 20px;
    background: linear-gradient(135deg, #4f46e5, #3b82f6);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 14px;
    cursor: pointer;
    transition: 0.3s ease;
    box-shadow: 0 5px 15px rgba(79, 70, 229, 0.3);
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(79, 70, 229, 0.4);
}

.description {
    color: #6b7280;
    font-size: 14px;
    line-height: 1.6;
    margin-top: 10px;
}
</style>