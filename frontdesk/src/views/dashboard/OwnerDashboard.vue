<template>
       <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
           <template #start>
               <div class="text-xl md:text-2xl"> {{ $t('Owner Dashboard') }} </div>
           </template>
           <template #center>
            <div class="w-full flex item-content-center justify-content-center">
    <div class="calendar_class" style="z-index: 200;">
        <Button :label="$t('Yesterday ')" class="w-8rem md:w-12rem btn-date__t border-noround-right border-none"
                :class="selected_date == yesterday  ? 'active' : ''" @click="onShowTommorowData()" />
        <Button :label="$t('Today')" class="w-8rem md:w-12rem btn-date__t border-noround border-x-none border-none"
                :class="selected_date == working_day.date_working_day ? 'active' : ''" @click="onShowTodayData()" />
                <Calendar v-model="date" :selectOtherMonths="true" class="w-48 das-calendar" panelClass="no-btn-clear"
                @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar />
    </div>
    </div>
           </template>
       </ComHeader>
  
   
        <div class="w-full -mt-2">
            <ComOwnerDashboardKPI :date="selected_date" />
        </div>    
        <div class="grid px-2 mt-2">
        <div class="col-12 p-1">
            <ComOwnerCurrentMonthChart/>
        </div>        
        <div class="lg:col-6 col-12 p-0">
            <div class="col-12 p-0 h-auto p-1">
                <ComOwnerPaymentChart :date="selected_date" />
            </div>
            <div class="col-12 p-0 h-auto p-1"> 
                <ComOwnerRoomTypeChart :date="selected_date"  />
            </div>
        </div>
        <div class="lg:col-6 col-12 h-auto p-0">
            <div class="h-full p-1">
                <ComOwnerChargeChart :date="selected_date"/>
            </div>
        </div>
        <div class="lg:col-6 col-12 h-auto p-0">
            <div class="h-full p-1">
              <ComOwnerNationalityChart :date="selected_date" />
            </div>
        </div>
        <div class="lg:col-6 col-12 p-1">
            <ComOwnerBusinessSourceChart :date="selected_date"/>
        </div> 
    <div class="lg:col-6 col-12 p-1">
        <ComOwnerFBList :date="selected_date"/>
    </div> 
    <div class="lg:col-6 col-12 p-1">
        <ComOwnerFBPaymentList :date="selected_date"/>
    </div> 
    <div class="col-12 p-1">
        <ComOwnerTodayLedgerSummaryList :date="selected_date"/>
    </div> 
    <div class="col-12 p-1">
        <ComRecentFolioTransaction :date="selected_date"/>
    </div> 
</div>
</template>
<script setup>
import { inject, ref, onUnmounted, onMounted, computed } from '@/plugin'
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
import ComOwnerNationalityChart from '@/views/dashboard/components/ComOwnerNationalityChart.vue'
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const selected_date = ref(null)
const yesterday  = ref('')
const date = ref(null)
const moment = inject('$moment')
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
function onShowTodayData() {
    selected_date.value = working_day.date_working_day;
    date.value = moment(working_day.date_working_day).format("DD-MM-YYYY")
  
}
function onShowTommorowData() {
    yesterday.value = moment(working_day.date_working_day, "YYYY-MM-DD").add(-1, 'days');
    yesterday.value = moment(yesterday.value).format("YYYY-MM-DD")
    selected_date.value = yesterday.value
    date.value = moment(yesterday.value).format("DD-MM-YYYY")
    
}
function onDateSelect(event) {
    const today = moment(working_day.date_working_day);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = moment(tomorrow.value).format("YYYY-MM-DD")
    selected_date.value = moment(event).format("YYYY-MM-DD")
    
}


onMounted(() => {
    if (!selected_date.value) {
        const edoor_working_day = working_day.date_working_day
        selected_date.value = moment(edoor_working_day).format("YYYY-MM-DD")
    }
    if (!date.value) {
        date.value = moment(selected_date.value).format("DD-MM-YYYY")
    }
}) 
function Refresh() {
    window.postMessage({ action: "ComOwnerDashboardKPI" }, "*");
}
    
</script>