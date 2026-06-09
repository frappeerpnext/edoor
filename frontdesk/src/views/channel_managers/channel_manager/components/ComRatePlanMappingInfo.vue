<template> 
    <div class="card">
        <DataTable :value="channelManagerData?.rate_plans" stripedRows tableStyle="min-width: 50rem">
            <Column field="rate_plan_code" :header="$t('Rate Plan Code')"></Column>
            <Column field="rate_plan_name" :header="$t('Rate Plan Name')"></Column>
            <Column field="edoor_rate_plan" :header="$t('eDoor Rate Plan')"></Column> 
            <Column field="availability_block" :header="$t('Availability Block')"></Column> 
            <Column field="availabilty_block_name" :header="$t('Availabilty Block Name')"></Column> 
        </DataTable>
    </div> 

 
</template>
<script setup>
import { useCMDashboard } from '@/views/channel_managers/channel_manager/hooks/useCMDashboard.js'

const { channelManagerData } = useCMDashboard()

</script>