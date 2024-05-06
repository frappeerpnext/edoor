<template>
    <div class="w-full text-white bg-kpi-owner-db p-5 border-round-xl">
        <div class="grid gap-2" style="height:80px">
            <template v-if="loading">
                <div v-for="index in 6" :key="index" class="col p-0">
      <Skeleton width="100%" height="100%"></Skeleton>   
    </div>
            </template>
           <template v-else> 
            <ComOwnerKPICard label="Today Revenue" :value="data.room_revenue" bgColor="bg-blue-500" icon="pi pi-chart-line"/>
            <ComOwnerKPICard label="Today ADR" :value="data?.adr" bgColor="bg-blue-500" icon="pi pi-dollar" />
            <ComOwnerKPICard label="Today Payment" :value="data?.today_payment" bgColor="bg-red-400" icon="pi pi-dollar" />
            <ComOwnerKPICard label="MTD Revenue" :value="data?.mtd_room_revenue" bgColor="bg-cyan-500" icon="pi pi-dollar" />
            <ComOwnerKPICard label="MTD ADR" :value="data?.mtd_adr" bgColor="bg-cyan-500" icon="pi pi-dollar" />
            <ComOwnerKPICard label="MTD Payment" :value="data?.mtd_payment" bgColor="bg-red-400" icon="pi pi-dollar" /> 
            </template>
        </div>
        <hr class="my-3">
        <div class="grid">
            <div class="col-6 p-0">
                <ComTitleOfKeyKPI label="Today Revenue">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.room_revenue" />
                   <ComOwnerKeyValueKPI label="Other Revenue" :value="data?.other_revenue" />
                   <ComOwnerKeyValueKPI label="RevPAR" :value="data?.revpar" />
                </ComTitleOfKeyKPI>
                <ComTitleOfKeyKPI class="mt-3" label="Today Expected">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.today_exp_revenue" />
                   <ComOwnerKeyValueKPI label="ADR" :value="data?.today_exp_adr" />
                </ComTitleOfKeyKPI>
            </div>
            <div class="col-6 p-0">
                <ComTitleOfKeyKPI label="MTD Revenue">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.mtd_room_revenue" />
                   <ComOwnerKeyValueKPI label="Other Revenue" :value="data?.mtd_other_revenue" />
                   <ComOwnerKeyValueKPI label="RevPAR" :value="data?.mtd_revpar" />
                </ComTitleOfKeyKPI>
                <ComTitleOfKeyKPI class="mt-3" label="Expense">
                   <ComOwnerKeyValueKPI label="Today Expense" :value="data?.today_expense" />
                   <ComOwnerKeyValueKPI label="MTD Expense" :value="data.mtd_expense" />
                </ComTitleOfKeyKPI>
            </div>
        </div>
    </div>
    {{selected_date}}
</template>
<script setup>
import ComOwnerKPICard from '@/views/dashboard/components/ComOwnerKPICard.vue';
import ComTitleOfKeyKPI from '@/views/dashboard/components/ComTitleOfKeyKPI.vue';
import ComOwnerKeyValueKPI from '@/views/dashboard/components/ComOwnerKeyValueKPI.vue';
import { inject, ref, onUnmounted, onMounted, computed } from '@/plugin'
const loading = ref(true)
const frappe = inject("$frappe")
const selected_date = JSON.parse(localStorage.getItem("edoor_working_day")).edoor_working_day
const call = frappe.call()
const data = ref({})
const doc = call.get('edoor.api.frontdesk.get_owner_dashboard_current_revenue_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day
    })
        .then((result) => {
            data.value = result.message
            loading.value = false 
        }).catch((error) => {
            loading.value = false 
  });
</script>
