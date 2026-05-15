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

      
        <div v-else >
        <!-- PENDING -->
<StatusMessage 
  :show="dataUploadStatus?.restriction?.status === 'Pending' || !(dataUploadStatus?.restriction?.status)"
  status="Pending"
  title="Action Required: Review Booking Restrictions"
>
  Please verify that the restriction rules below (like <strong>MinLOS</strong> and <strong>Closed</strong>) 
  match your property policy. These settings will go live immediately upon confirmation.
</StatusMessage>

<!-- IN PROGRESS -->
<StatusMessage 
  :show="dataUploadStatus?.restriction?.status === 'In Progress'"
  status="In Progress"
  title="Uploading Restriction Data"
>
  Updating restriction parameters for <strong>{{ dataUploadStatus?.room_rate?.room_types?.length }}</strong> 
  room types. This may take a few moments as we sync each rule individually.
</StatusMessage>

<!-- COMPLETE -->
<StatusMessage 
  :show="dataUploadStatus?.restriction?.status === 'Complete'"
  status="Complete"
  title="Restrictions Successfully Synced"
>
  Your booking restrictions are now live and synchronized. You can proceed to the 
  <strong>Extra Services</strong> step.
</StatusMessage>
             <div v-for="rt in dataUploadStatus?.restriction?.room_types" :key="rt.room_type_code" 
     class="flex flex-column p-4 border-round shadow-1 bg-white mb-3 border-left-3"
     :class="rt.status === 'Pending' ? 'border-gray-400' : 'border-green-500'">
    
    <!-- 1. Header Section -->
    <div class="flex align-items-center justify-content-between mb-3">
        <div class="flex align-items-center gap-3">
            <div class="p-3 bg-bluegray-50 border-round">
                <i class="pi pi-lock text-bluegray-600 text-xl"></i>
            </div>
            <div class="flex flex-column">
                <span class="text-xl font-bold text-900">{{ rt.room_type_name }}</span>
                <span class="text-sm text-500">{{ rt.room_type }} | Code: {{ rt.room_type_code }}</span>
            </div>
        </div>
        <Tag :value="rt.status" :severity="rt.status === 'Pending' ? 'secondary' : 'success'" />
    </div>

    <!-- 2. Restrictions Grid Section -->
    <div class="bg-gray-50 p-3 border-round border-1 border-100">
        <div class="text-xs font-bold text-500 uppercase mb-3 letter-spacing-1">
            {{ $t('Syncing Restrictions') }} ({{ rt.restrictions.length }})
        </div>
        
        <div class="grid">
            <div v-for="res in rt.restrictions" :key="res.restriction" class="col-12 md:col-6 lg:col-4 xl:col-3">
                <div class="flex align-items-center justify-content-between p-2 bg-white border-round border-1 border-200 shadow-sm">
                    <span class="text-sm font-medium text-700 ml-1">{{ res.restriction }}</span>
                    
                    <!-- Compact Status Indicator -->
                    <div class="flex align-items-center">
                        <i v-if="res.status === 'Pending'" class="pi pi-clock text-orange-500 text-xs mr-2"></i>
                        <i v-else-if="res.status === 'In Progress'" class="pi pi-spin pi-spinner text-blue-500 text-xs mr-2"></i>
                        <i v-else class="pi pi-check-circle text-green-500 text-xs mr-2"></i>
                        
                        <span class="text-xs font-semibold uppercase" 
                              :class="res.status === 'Pending' ? 'text-orange-500' : 'text-green-500'">
                            {{ res.status }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>

        </div>

        <!-- i agree -->
        <div class="my-3" v-if="dataUploadStatus?.restriction?.restrictions?.length > 0 && dataUploadStatus?.restriction?.sync_mode == 'Receive from PMS'">
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
import StatusMessage from '@/views/channel_managers/channel_manager/components/StatusMessage.vue'
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