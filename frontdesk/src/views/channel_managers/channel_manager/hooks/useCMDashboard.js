import { onMounted,ref, computed } from "vue"
 
import ChannelManagerDashboard from "@/views/channel_managers/channel_manager/ChannelManagerDashboard.vue"
import ComCMInit from "@/views/channel_managers/channel_manager/components/cm_initialize_step/ComCMInit.vue"
import {
    getRecentReservation
}  from  "@/views/channel_managers/channel_manager/hooks/helper.js"

// State list
const initialized = ref(false)
const recentReservationData = ref([])
const currentComponent = ref()
const isInitializedUpload = ref(0)
const channelManagerData = ref({})
const currentCMComponent = ref()
const dataUploadStatus = ref(null)
const activeStepIndex = ref(1)


const dataUploadSteps = ref([
  { index: 1, title: 'WELCOME' },
  { index: 2, title: 'CREDENTIALS',is_validate:false },
  { index: 3, title: 'DATA MAPPING' },
  { index: 4, title: 'AVAILABILITY' },
  { index: 5, title: 'PRICES' },
  { index: 6, title: 'RESTRICTIONS' },
  { index: 7, title: 'EXTRA SERVICES' },
  { index: 8, title: 'COMPLETE' }
])




export function useCMDashboard() {
    const property = JSON.parse(localStorage.getItem('edoor_property'))
     
    async function getChannelManagerData() {
        const res = await app.getDoc('Channel Manager Integration', property.name)

        if (res.data) {
            channelManagerData.value = res.data 
            isInitializedUpload.value = res.data.initialized_data_upload 
        }

    }

    function getSetting(){
        // api call 
        // 1 upload already or not yet
        // how manu step already update
        // connectted source
        // last sysnch status

    }

    async function getDataUploadStatus(){
        const res =await app.getApi("edoor.channel_managers.data_upload.get_data_upload_status",{
            property:window.property_name
        })
        if (res.data){
            dataUploadStatus.value = res.data
        }
    }

    function onChangeDataUploadStep(n=1){

        activeStepIndex.value = activeStepIndex.value  + n
        

    }

    onMounted(async()=>{
          // prevent multiple API calls
        if (initialized.value) return
        initialized.value = true


        const l = await window.showLoading()

        await getChannelManagerData() 
       
            currentCMComponent.value = (isInitializedUpload.value == 1)
                ? ChannelManagerDashboard
                : ComCMInit;

            l.close()    
      

    })

     function resetData(){
        activeStepIndex.value = 1
        initialized.value = false;
        dataUploadStatus.value = null
        // change credential step is validate = false
        dataUploadSteps.value[1].is_validate = false

    }

    async function onRefresh(is_reset = false){
        const l = await window.showLoading()
        await getChannelManagerData() ;
        await getDataUploadStatus();
        if(is_reset){
            resetData();
            currentCMComponent.value = ChannelManagerDashboard;
        }
        l.close();

    }

    return {
        dataUploadStatus,
        currentComponent,
        recentReservationData,
        getRecentReservation,
        channelManagerData,
        currentCMComponent,
        dataUploadSteps,
        activeStepIndex,
        getChannelManagerData,
        getDataUploadStatus,
        resetData,
        onChangeDataUploadStep,
        onRefresh
    }
}