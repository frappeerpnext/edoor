<template>
        <div class="w-full mt-1">
            <ComOwnerDashboardKPI/>
        </div>    
    <div class="grid px-2 mt-2">
        <div class="col-12 bg-green-500">
            <ComOwnerCurrentMonthChart/>
        </div>        
        <div class="col-6 p-0">
            <div class="col-12 p-0 h-auto p-1">
                <ComOwnerPaymentChart />
            </div>
            <div class="col-12 p-0 h-auto p-1"> 
                <ComOwnerRoomTypeChart />
            </div>
        </div>
        <div class="col-6 h-auto p-0">
            <div class="h-full p-1">
                <ComOwnerChargeChart />
            </div>
        </div>
        <div class="col-12 p-1">
            <ComOwnerBusinessSourceChart />
        </div> 
<div class="col-6 bg-black">
    FB
</div> 
<div class="col-6 bg-pink-500">
    FBpayment
</div> 
<div class="col-12 bg-red-500">
    city
</div> 
<div class="col-12 bg-green-500">
    <ComRecentFolioTransaction/>
</div> 
</div>
</template>
<script setup>

import ComOwnerDashboardKPI from '@/views/dashboard/components/ComOwnerDashboardKPI.vue'
import ComOwnerCurrentMonthChart from '@/views/dashboard/components/ComOwnerCurrentMonthChart.vue'
import ComOwnerPaymentChart from '@/views/dashboard/components/ComOwnerPaymentChart.vue'
import ComRecentFolioTransaction from '@/views/dashboard/components/ComRecentFolioTransaction.vue'
import ComOwnerChargeChart from '@/views/dashboard/components/ComOwnerChargeChart.vue'
import ComOwnerRoomTypeChart from '@/views/dashboard/components/ComOwnerRoomTypeChart.vue'
import ComOwnerBusinessSourceChart from '@/views/dashboard/components/ComOwnerBusinessSourceChart.vue'
import ComOwnerFBList from '@/views/dashboard/components/ComOwnerFBList.vue'
</script>