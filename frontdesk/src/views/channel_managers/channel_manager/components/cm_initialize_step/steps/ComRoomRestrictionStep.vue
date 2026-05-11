<template>
    <div>
       
       
        <template v-if="dataUploadStatus?.restriction?.sync_mode == 'Manage in CM'">

            <p>
                Your room restrictions are currently managed directly in the Channel Manager (CM). Because of this
                configuration,
                restriction data will not be synchronized between the PMS and the Channel Manager.
            </p>

            <p>
                Please make sure all restriction updates and changes are maintained directly in the Channel Manager to
                ensure
                accurate restriction settings across all connected channels.
            </p>



        </template>
        <!-- end manage in cm -->
        <template v-else-if="dataUploadStatus?.restriction?.sync_mode == 'Deliver to PMS'">

            Get data from cm and update to pms

        </template>

      
        <div v-else v-for="rt in dataUploadStatus?.restriction?.room_types">
              <template v-if="dataUploadStatus?.restriction?.restrictions?.length == 0">
            You have not enabled any restriction configuration in the Channel Manager Integration Settings.
            Please enable at least one restriction code if you would like to use restriction features.

        </template>
            <i v-if="rt.status == 'Pending'" class="pi pi-check bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else-if="rt.status == 'In Progress'"
                class="pi pi-spin pi-spinner bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else class="pi pi-check bg-green-500 text-white p-2 border-circle"></i>

            {{ rt }}

            <div>
                <template v-for="rs in rt.restrictions">
                    <Chip :label="rs.restriction" v-if="rs.status == 'Pending'" />
                    <Chip :label="rs.restriction" v-else-if="rs.status == 'In Progress'" icon="pi pi-spinner pi-spin" />
                    <Chip :label="rs.restriction" v-else icon="pi pi-check bg-green-500 text-white rounded-full p-1" />
                </template>

            </div>

        </div>

        <!-- i agree -->
        <div v-if="dataUploadStatus?.restriction?.restrictions?.length > 0 && dataUploadStatus?.restriction?.sync_mode == 'Receive from PMS'">
            <Checkbox v-model="iAgree" :binary="true" inputId="iAgree" />
            <label for="iAgree" class="ml-2 cursor-pointer">
                By checking this box, you confirm that all room restriction information is accurate.
            </label>
        </div>


        <!-- Footer -->
        <div class="footer flex gap-2">
            <!-- previouse button -->
            <Button @click="onChangeDataUploadStep(-1)" class="btn-back" icon="pi pi-arrow-left" :label="$t('Back')" />
            <!-- upload room rate to cm -->
            <Button @click="onUploadRoomRestrictionData"
                v-if="dataUploadStatus?.restriction.status != 'Complete' && dataUploadStatus.restriction.sync_mode == 'Receive from PMS'"
                :loading="dataUploadStatus?.restriction.status == 'In Progress'" severity="danger"
                icon="pi pi-cloud-upload" :label="$t('Upload Room Restriction Now')" />
       <!-- next -->
            <Button @click="onChangeDataUploadStep(1)" class="btn-next"
                v-if="dataUploadStatus?.restriction?.status == 'Complete' || dataUploadStatus.restriction.sync_mode == 'Manage in CM' "  icon="pi pi-arrow-right" iconPos="right"
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

function onViewRoomRestriction() {
    alert("view resteiction type data")
}
async function onUploadRoomRestrictionData() {


    if (!iAgree.value) {

        app.utils.showWarning("Upload Room Restriction", "Please confirm that the room restriction information is accurate by checking the agreement box.");
        return;
    }
    const result = await app.utils.onConfirm("Upload Room Restriction", "Are you sure you want to upload room restriction to Channel Manager now?")
    if (result) {


        const l = await window.showLoading()
        const res = await app.postApi("room_restriction.initialized_room_restriction_upload", {
            property: window.property_name
        })
        if (res.data) {

            dataUploadStatus.value.restriction.status = "In Progress"
            dataUploadStatus.value.restriction.room_types.forEach(rt => {
                rt.status = 'In Progress';
                rt.restrictions.forEach((rs) => {
                    rs.status = 'In Progress';
                })
            })
        }

        l.close()
    }

}

</script>