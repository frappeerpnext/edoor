<template>
    <div>
      
        <template v-if="dataUploadStatus?.extra_service?.sync_mode=='Manage in CM'">
               <p>
    Your extra services are currently managed directly in the Channel Manager (CM). Because of this configuration,
    extra service data will not be synchronized between the PMS and the Channel Manager.
</p>

<p>
    Please ensure all extra service price updates are maintained correctly in the Channel Manager to guarantee
    accurate pricing across all connected channels.
</p>
        </template>
        <template v-else>
          <div>
             <i v-if="dataUploadStatus?.extra_service.status == 'Pending'" class="pi pi-check bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else-if="dataUploadStatus?.extra_service.status == 'In Progress'"
                class="pi pi-spin pi-spinner bg-gray-500 text-white p-2 border-circle"></i>
            <i v-else class="pi pi-check bg-green-500 text-white p-2 border-circle"></i>


          </div>
            <div v-for="s in dataUploadStatus?.extra_service?.extra_services">
              {{ s }}
            </div>
        
            <!-- i agree -->
        <div>
            <Checkbox v-model="iAgree" :binary="true" inputId="iAgree" />
            <label for="iAgree" class="ml-2 cursor-pointer">
                By checking this box, you confirm that all extra service rate is accurate.
            </label>
        </div>

        
          </template>

        
      <!-- Footer -->
    <div>
  <Button 
    @click="onChangeDataUploadStep(-1)" 
    
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <!-- upload service rate to cm -->
    
    <Button @click="onUploadExtraServiceRate"
                v-if="dataUploadStatus?.extra_service.status != 'Complete' && dataUploadStatus.extra_service.sync_mode == 'Receive from PMS'"
                :loading="dataUploadStatus?.extra_service.status == 'In Progress'" severity="danger"
                icon="pi pi-cloud-upload" :label="$t('Upload Extra Service Now')" />
  <!-- Next Button -->
                <Button 
    @click="onNext()" 
    v-if="dataUploadStatus?.extra_service.status == 'Complete' || dataUploadStatus.extra_service.sync_mode == 'Manage in CM'"
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Next')"
  />
</div>

    </div>
</template>
<script setup>
import { ref } from 'vue';
import { useCMDashboard } from '../../../hooks/useCMDashboard';
const iAgree = ref(false)
const {
    dataUploadStatus,
    onChangeDataUploadStep
  } = useCMDashboard();

  async function onUploadExtraServiceRate() {
      

    if (!iAgree.value) {

        app.utils.showWarning("Upload Extra Service Rate", "Please confirm that the extra service rate is accurate by checking the agreement box.");
        return;
    }
    const result = await app.utils.onConfirm("Upload Extra Service Rate", "Are you sure you want to upload extra service rate to Channel Manager now?")
    if (result) {


        const l = await window.showLoading()
        const res = await app.postApi("extra_service.initialized_extra_service_upload", {
            property: window.property_name
        })
        if (res.data) {

            dataUploadStatus.value.extra_service.status = "In Progress"
            
        }

        l.close()
    }
  }

  async function onNext(){
    const l = await window.showLoading();
    const res = await app.postApi("extra_service.mark_as_first_upload_complete",{
      property:window.property_name
    },"",false)
    if(res.data){
      setTimeout(() => {
      onChangeDataUploadStep(1);  
      }, 500);
      
    }

    l.close();
  }
</script>