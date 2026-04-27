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
import { ref ,onMounted } from 'vue';
import ComViewPendingSyncData from '@/views/channel_managers/channel_manager/components/ComViewPendingSyncData.vue';
const props = defineProps({
    types:Object
})
const hasPendingData = ref(true);
function onViewPendingData() {
    app.utils.openDialog(ComViewPendingSyncData, "Pending Sync Data")
    op.value.hide()

}
async function checkPendingSyncData(){
    const res = await app.getDocList("Channel Manager Sync Data Log")
    if (res.data){
        hasPendingData.value = res.data.length>0
    }

}

onMounted(async ()=>{
    await checkPendingSyncData()
})

</script>