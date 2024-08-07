<template> 
    <div class="w-full text-white bg-kpi-owner-db p-5 border-round-xl">
        <div class="grid gap-2" >
            <template v-if="loading">
                <div v-for="index in 6" :key="index" class="col p-0">
      <Skeleton width="100%" height="75px"></Skeleton>   
    </div>
            </template>
           <template v-else> 
            <div class="grid w-full gap-2">
            <ComOwnerKPICard label="Today Revenue" :value="data.today_revenue" bgColor="bg-blue-500" icon="pi pi-chart-line"/>
            <ComOwnerKPICard label="Today Room Sold"  bgColor="bg-blue-500" icon="pi pi-dollar">
                <template v-slot:value>
                    {{data?.today_room_sold}}
                    ( {{ data?.today_occupy_data.today_occupancy.toFixed(2) }}% )
                </template>
            </ComOwnerKPICard>
            <ComOwnerKPICard label="Today Payment" :value="data?.today_payment" bgColor="bg-red-400" icon="pi pi-dollar" />
            <ComOwnerKPICard label="MTD Revenue" :value="data?.mtd_revenue" bgColor="bg-cyan-500" icon="pi pi-dollar" />
            <ComOwnerKPICard label="MTD Room Sold" :value="data?.mtd_adr" bgColor="bg-cyan-500" icon="pi pi-dollar" >
                <template v-slot:value>
                    {{data?.mtd_occupy_data.total_room_sold}}
                    ( {{ data?.mtd_occupy_data?.mtd_occupancy.toFixed(2) }}% )
                </template>
            </ComOwnerKPICard>
            <ComOwnerKPICard label="MTD Payment" :value="data?.mtd_payment" bgColor="bg-red-400" icon="pi pi-dollar" /> 
            </div>
            </template>
        </div>
        <hr class="my-3">
        <div class="grid">
            <div class="lg:col-6 col-12 p-0">
                <ComTitleOfKeyKPI label="Today Revenue">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.room_revenue" />
                   <ComOwnerKeyValueKPI label="ADR" :value="data?.adr" />
                   <ComOwnerKeyValueKPI label="RevPAR" :value="data?.revpar" />
                   <ComOwnerKeyValueKPI label="Other Revenue" :value="data?.other_revenue" />
                   
                </ComTitleOfKeyKPI>
                <ComTitleOfKeyKPI class="mt-3" label="Today Expected">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.today_exp_revenue" />
                   <ComOwnerKeyValueKPI label="ADR" :value="data?.today_exp_adr" />
                </ComTitleOfKeyKPI>
            </div>
            <div class="lg:col-6 col-12 p-0">
                <ComTitleOfKeyKPI label="MTD Revenue">
                   <ComOwnerKeyValueKPI label="Room Revenue" :value="data?.mtd_room_revenue" />
                   <ComOwnerKeyValueKPI label="MTD ADR" :value="data?.mtd_adr" />
                   <ComOwnerKeyValueKPI label="RevPAR" :value="data?.mtd_revpar" />
                   <ComOwnerKeyValueKPI label="Other Revenue" :value="data?.mtd_other_revenue" />
                </ComTitleOfKeyKPI>
                <ComTitleOfKeyKPI class="mt-3" label="Expense">
                   <ComOwnerKeyValueKPI label="Today Expense" :value="data?.today_expense" />
                   <ComOwnerKeyValueKPI label="MTD Expense" :value="data.mtd_expense" />
                </ComTitleOfKeyKPI>
            </div>
        </div>
    </div>
</template>
<script setup>
import ComOwnerKPICard from '@/views/dashboard/components/ComOwnerKPICard.vue';
import ComTitleOfKeyKPI from '@/views/dashboard/components/ComTitleOfKeyKPI.vue';
import ComOwnerKeyValueKPI from '@/views/dashboard/components/ComOwnerKeyValueKPI.vue';
import { inject, ref, defineProps ,watch ,onMounted, computed ,onUnmounted } from '@/plugin'
const loading = ref(true)
const frappe = inject("$frappe")
const call = frappe.call()
const data = ref({})
const props = defineProps({
    date: {
      type: Date,
    },
  });

  const fetchData = () => { 
    loading.value = true 
    call.get('edoor.api.frontdesk.get_owner_dashboard_current_revenue_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        end_date: props.date
    })
        .then((result) => {
            data.value = result.message
            loading.value = false 
        }).catch((error) => {
            loading.value = false 
  });
}
watch(() => props.date, (newDate) => {
  if (newDate) {
    fetchData();
  }
});
const windowActionHandler = async function (e) {
        if (e.isTrusted) {
            if (e.data.action == "ComOwnerDashboardKPI") {
                fetchData();    
            }
        }
    }
onMounted(() => {
        window.addEventListener('message', windowActionHandler, false);
    })
   onUnmounted(() => {
     window.removeEventListener('message', windowActionHandler, false);
   })
</script>
