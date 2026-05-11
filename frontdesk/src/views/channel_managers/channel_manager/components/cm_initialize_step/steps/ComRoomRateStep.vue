<template>
    <div>
        <!-- if mode manage in cm -->
        <template v-if="dataUploadStatus?.room_rate?.sync_mode == 'Manage in CM'">
            <p>
                Your rates are currently managed directly in the Channel Manager (CM). Because of this configuration,
                rate data will not be synchronized between the PMS and the Channel Manager.
            </p>
            <p>Please make sure all rate updates and changes are maintained directly in the Channel Manager to ensure
                pricing accuracy across all connected channels.</p>

        </template>
        <!-- end manage in cm -->
        <template v-else-if="dataUploadStatus?.room_rate?.sync_mode == 'Deliver to PMS'">

            Get data from cm and update to pms

        </template>
        <div v-else v-for="rt in dataUploadStatus?.room_rate?.room_types">
            <i v-if="rt.status == 'Pending'" class="pi pi-check bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else-if="rt.status == 'In Progress'"
                class="pi pi-spin pi-spinner bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else class="pi pi-check bg-green-500 text-white p-2 border-circle"></i>

            {{ rt }}

        </div>

        <div>
        <!-- i agree -->
        <Checkbox v-model="iAgree" :binary="true" inputId="iAgree" />
        <label for="iAgree" class="ml-2 cursor-pointer">
            By checking this box, you confirm that all room rate information is accurate.
        </label>
</div>
        <!-- Footer -->
        <div class="footer flex gap-2">
            <!-- previouse button -->
            <Button @click="onChangeDataUploadStep(-1)" class="btn-back" icon="pi pi-arrow-left" :label="$t('Back')" />

           
            <!-- upload room rate to cm -->
            <Button @click="onUploadRoomRateData"
                v-if="dataUploadStatus?.room_rate.status != 'Complete' && dataUploadStatus.availability.sync_mode == 'Receive from PMS'"
                :loading="dataUploadStatus?.room_rate.status == 'In Progress'" severity="danger"
                icon="pi pi-cloud-upload" :label="$t('Upload Room Rate Now')" />
            <!-- next -->
            <Button @click="onChangeDataUploadStep(1)" class="btn-next"
                v-if="dataUploadStatus?.room_rate?.status == 'Complete'" icon="pi pi-arrow-right" iconPos="right"
                :label="$t('Next')" />
        </div>

    </div>
</template>
<script setup>
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js';
import { ref } from 'vue';

const { onChangeDataUploadStep,
    dataUploadStatus
} = useCMDashboard();

const iAgree = ref(false)

 
async function onUploadRoomRateData() {


    if (!iAgree.value) {

        app.utils.showWarning("Upload Room Rate", "Please confirm that the room rate information is accurate by checking the agreement box.");
        return;
    }
    const result = await app.utils.onConfirm("Upload Room Rate", "Are you sure you want to upload room rate to Channel Manager now?")
    if (result) {


        const l = await window.showLoading()
        const res = await app.postApi("rate_plan.initialized_room_rate_upload", {
            property: window.property_name
        })
        if (res.data) {

            dataUploadStatus.value.room_rate.status = "In Progress"
            dataUploadStatus.value.room_rate.room_types.forEach(rt => {
                rt.status = 'In Progress'
            })
        }

        l.close()
    }

}

</script>