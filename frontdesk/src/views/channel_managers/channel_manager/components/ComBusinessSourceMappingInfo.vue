<template> 
    <div class="card">
        <DataTable :value="channelManagerData?.business_source" stripedRows tableStyle="min-width: 50rem">
            <Column field="cm_business_source" :header="$t('CM Business Source')"></Column>
            <Column field="edoor_business_source" :header="$t('eDoor Business Source')"></Column> 
        </DataTable>
    </div> 

 
</template>
<script setup>
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()

</script>