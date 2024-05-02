<template>
    <div class="w-full text-white bg-kpi-owner-db p-5 border-round-xl">
        <div class="grid gap-2">
            <ComOwnerKPICard label="Today Revenue" :value="data.room_revenue" bgColor="bg-blue-500" icon="pi pi-chart-line"/>
            <ComOwnerKPICard label="Today ADR" :value="data?.adr" bgColor="bg-blue-500"/>
            <ComOwnerKPICard label="Today Payment" :value="data?.today_payment" bgColor="bg-red-400"/>
            <ComOwnerKPICard label="MTD Revenue" :value="data?.mtd_room_revenue" bgColor="bg-cyan-500"/>
            <ComOwnerKPICard label="MTD ADR" :value="data?.mtd_adr" bgColor="bg-cyan-500"/>
            <ComOwnerKPICard label="MTD Payment" :value="data?.mtd_payment" bgColor="bg-red-400"/> 
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
            console.log(JSON.parse(localStorage.getItem("edoor_working_day")).date_working_day)
        })
</script>
