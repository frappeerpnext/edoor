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
        <!-- Message Box -->
<div class="mt-4 mb-4">
<!-- PENDING MESSAGE -->
<StatusMessage 
  :show="dataUploadStatus?.room_rate?.status === 'Pending'"
  status="Pending"
  title="Action Required: Verify Occupancy Mapping"
>
  Before proceeding to the next step, please verify that all <strong>Occupancy Titles</strong> 
  listed under each room type match your contract rules. Incorrect mapping may result in 
  pricing discrepancies on OTA channels.
</StatusMessage>

<!-- IN PROGRESS MESSAGE -->
<StatusMessage 
  :show="dataUploadStatus?.room_rate?.status === 'In Progress'"
  status="In Progress"
  title="Syncing Data"
>
  Your room rates and occupancy rules are currently being synchronized with the channel manager. 
  Please stay on this page until the process is finished.
</StatusMessage>

<!-- COMPLETED MESSAGE -->
<StatusMessage 
  :show="dataUploadStatus?.room_rate?.status === 'Complete'"
  status="Complete"
  title="Mapping Confirmed"
>
  All room rates and occupancy codes have been successfully validated and linked. 
  Your pricing structure is now ready for the next stage of integration.
</StatusMessage>
</div>
        <div class="flex flex-column gap-3">
 <div class="flex flex-column gap-3">
    <div v-for="rt in dataUploadStatus?.room_rate?.room_types" :key="rt.room_type_code" 
         class="flex flex-column p-3 border-round shadow-1 bg-white border-left-3"
         :class="{
            'border-gray-400': rt.status === 'Pending',
            'border-blue-500': rt.status === 'In Progress',
            'border-green-500': rt.status === 'Complete'
         }">
        
        <!-- Top Row: Main Info -->
        <div class="flex align-items-center justify-content-between">
            <div class="flex align-items-center gap-3">
                <!-- Status Icon -->
                <div class="flex align-items-center justify-content-center border-circle shadow-sm" 
                     style="width: 32px; height: 32px"
                     :class="{
                        'bg-gray-500': rt.status === 'Pending',
                        'bg-blue-500': rt.status === 'In Progress',
                        'bg-green-500': rt.status === 'Complete'
                     }">
                    <i :class="[
                        'pi text-white text-xs',
                        rt.status === 'Pending' ? 'pi-check' : 
                        rt.status === 'In Progress' ? 'pi-spin pi-spinner' : 'pi-check'
                    ]"></i>
                </div>

                <div class="flex flex-column">
                    <span class="font-bold text-900 line-height-2">{{ rt.room_type_name }}</span>
                    <span class="text-xs text-500">ID: {{ rt.room_type }} | Code: {{ rt.room_type_code }}</span>
                </div>
            </div>

            <div class="flex align-items-center gap-3">
                <div class="hidden sm:flex flex-column align-items-end mr-2">
                    <span class="text-sm font-bold text-700">{{ rt.total_room }}</span>
                    <span class="text-xs text-400 uppercase font-semibold" style="letter-spacing: 1px">Rooms</span>
                </div>
                <Tag :value="rt.status" 
                     :severity="rt.status === 'Pending' ? 'secondary' : rt.status === 'In Progress' ? 'info' : 'success'" 
                     class="px-3 border-round-xl" />
            </div>
        </div>

        <!-- Bottom Row: Occupancy Codes (New Section) -->
        <div class="mt-3 pt-2 border-top-1 border-50">
            <div class="flex flex-wrap gap-1">
                <span v-for="code in rt.occupancy_codes" :key="code" 
                      class="text-xs bg-bluegray-50 text-bluegray-600 px-2 py-1 border-round font-medium border-1 border-100">
                    {{ code }}
                </span>
            </div>
        </div>
    </div>
</div>
</div>
        <div class="my-3">
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
import StatusMessage from '@/views/channel_managers/channel_manager/components/StatusMessage.vue'
import Tag from 'primevue/tag';

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