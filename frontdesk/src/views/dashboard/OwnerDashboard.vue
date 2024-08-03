<template>
        <div class="w-full mt-2">
            <ComOwnerDashboardKPI/>
        </div>    
        <div class="grid px-2 mt-2">
        <div class="col-12 p-1">
            <ComOwnerCurrentMonthChart/>
        </div>        
        <div class="lg:col-6 col-12 p-0">
            <div class="col-12 p-0 h-auto p-1">
                <ComOwnerPaymentChart />
            </div>
            <div class="col-12 p-0 h-auto p-1"> 
                <ComOwnerRoomTypeChart />
            </div>
        </div>
        <div class="lg:col-6 col-12 h-auto p-0">
            <div class="h-full p-1">
                <ComOwnerChargeChart />
            </div>
        </div>
        <div class="lg:col-6 col-12 h-auto p-0">
            <div class="h-full p-1">
              
            </div>
        </div>
        <div class="col-6 p-1">
            <ComOwnerBusinessSourceChart />
        </div> 
    <div class="lg:col-6 col-12 p-1">
        <ComOwnerFBList />
    </div> 
    <div class="lg:col-6 col-12 p-1">
        <ComOwnerFBPaymentList />
    </div> 
    <div class="col-12 p-1">
        <ComOwnerTodayLedgerSummaryList />
    </div> 
    <div class="col-12 p-1">
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
import ComOwnerFBPaymentList from '@/views/dashboard/components/ComOwnerFBPaymentList.vue'
import ComOwnerTodayLedgerSummaryList from '@/views/dashboard/components/ComOwnerTodayLedgerSummaryList.vue'
</script>