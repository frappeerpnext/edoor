<template>
   
    <Message :closable="false" v-if="hasPendingData" severity="warn">
        
        <p>You have pending data to sync to the channel manager. If it is not synced within 5 minutes, please contact your
        system administrator.
        </p>
        <div>
            <Button @click="onViewPendingData" label="View pending sync data" severity="secondary"></Button>
        </div>
    </Message>

</template>
<script setup>
import { ref ,onMounted, onUnmounted } from 'vue';
import ComViewPendingSyncData from '@/views/channel_managers/channel_manager/components/ComViewPendingSyncData.vue';
const props = defineProps({
    types:Object
})
const hasPendingData = ref(false);
const intervalId = ref(null)
function onViewPendingData() {
    app.utils.openDialog(ComViewPendingSyncData, "Pending Sync Data")
    op.value.hide()

}
async function checkPendingSyncData(){
 
    const {data,error} = await app.getApi("edoor.channel_managers.utils.get_pending_sync_data_status",{
        property:window.property_name
    })
    
 
hasPendingData.value = (data.has_pending_data == 1);
         
        
   

}


onMounted(async ()=>{
    
    await checkPendingSyncData()
     intervalId.value = setInterval(checkPendingSyncData, 1000*60)

})

onUnmounted(()=>{
    clearInterval(intervalId.value)
})


</script>