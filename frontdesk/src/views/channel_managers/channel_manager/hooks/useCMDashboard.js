import { onMounted,ref, computed } from "vue"
import ComA from "@/views/channel_managers/channel_manager/components/ComA.vue"
import ComB from "@/views/channel_managers/channel_manager/components/ComB.vue"
import ChannelManagerDashboard from "@/views/channel_managers/channel_manager/ChannelManagerDashboard.vue"
import ComCMInit from "@/views/channel_managers/channel_manager/components/cm_initialize_step/ComCMInit.vue"
import {
    getRecentReservation
}  from  "@/views/channel_managers/channel_manager/hooks/helper.js"
import { data } from "jquery"
// State list
const initialized = ref(false)
const recentReservationData = ref([])
const currentComponent = ref()
const isInitializedUpload = ref(0)
const channelManagerData = ref({})
const currentCMComponent = ref()



export function useCMDashboard() {
    const property = JSON.parse(localStorage.getItem('edoor_property'))
    
    function resetData(){

    }

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

    onMounted(async()=>{
          // prevent multiple API calls
        if (initialized.value) return
        initialized.value = true


        const l = await window.showLoading()

        await getChannelManagerData() 
        setTimeout(async() => {  
            currentCMComponent.value = isInitializedUpload.value == 1
                ? ChannelManagerDashboard
                : ComCMInit
            l.close()    
        }, 3000); 

    })

    return {
        currentComponent,
        recentReservationData,
        resetData,
        getRecentReservation,
        channelManagerData,
        currentCMComponent
    }
}