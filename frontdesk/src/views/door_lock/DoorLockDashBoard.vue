<template>
   <ComHeader :isRefresh="true" @onRefresh="onRefresh" :isSetting="true" >
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center gap-2 w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">
                          Door Lock Managemewnt
                        </div>
                        
                    </div>
                </div>
            </template>
            
        </ComHeader>
  <div class="surface-ground p-4 font-sans min-h-screen">
    <section class="mb-4">
      <div class="text-xs font-bold text-500 uppercase tracking-wider mb-2">Live System Health & Capacity</div>
      <div class="grid">
        <div class="col-12 sm:col-6 md:col-3 lg:col">
  <StatCard
    title="Total Rooms"
    :value="data.total_room"
    subtitle="100% Active Property"
    icon="pi pi-home"
    borderClass="border-blue-500"
    iconClass="text-blue-500"
  />
</div>

<div class="col-12 sm:col-6 md:col-3 lg:col">
  <StatCard
    title="Occupied"
    :value="data.total_room_occupy"
    subtitle="50% Occupancy Rate"
    icon="pi pi-bookmark"
    borderClass="border-green-500"
    iconClass="text-green-500"
    subtitleClass="text-green-500 font-medium"
  />
</div>

<div class="col-12 sm:col-6 md:col-3 lg:col">
  <StatCard
    title="Vacant Rooms"
    :value="data.total_room_vacant"
    subtitle="Ready for Check-In"
    icon="pi pi-check-circle"
    borderClass="border-teal-500"
    iconClass="text-teal-500"
    subtitleClass="text-teal-500 font-medium"
  />
</div>

<div class="col-12 sm:col-6 md:col-3 lg:col">
  <StatCard
    title="Cards Issued"
    :value="3"
    subtitle="Active Encoding Runs"
    icon="pi pi-credit-card"
    borderClass="border-purple-500"
    iconClass="text-purple-500"
    subtitleClass="text-purple-500 font-medium"
  />
</div>

<div class="col-12 sm:col-6 md:col-3 lg:col">
  <StatCard
    title="Failed Ops"
    :value="2"
    subtitle="Requires Verification"
    icon="pi pi-exclamation-circle"
    borderClass="border-red-500"
    iconClass="text-red-500"
    titleClass="text-red-500"
    valueClass="text-red-600"
    subtitleClass="text-red-400"
  />
</div>
      </div>
    </section>

    <section class="mb-4">
      <div class="text-xs font-bold text-500 uppercase tracking-wider mb-2">Quick Operations Dashboard Desk</div>
      <div class="grid">
       <div v-for="op in operations" :key="op.label" class="col-6 sm:col-4 md:col-3 lg:col">
  <div 
    @click="handleCardClick(op)"
    class="surface-card p-3 border-round shadow-1 text-center cursor-pointer hover:surface-100 transition-duration-150 border-1 border-100 h-full flex flex-column justify-content-center align-items-center"
  >
    <i :class="[op.icon, op.color, 'text-xl mb-2']"></i>
    <div class="text-sm font-bold text-800 mb-1">{{ op.label }}</div>
    <div class="text-xs text-500">{{ op.subtext }}</div>
  </div>
</div>
      </div>
    </section>

    <ComRecentLog ref="recentLogRef" />
  </div>
</template>

<script setup>
import { inject, ref, onUnmounted, onMounted, computed } from '@/plugin'
import { useToast } from "primevue/usetoast";
import StatCard from '@/views/door_lock/components/StatCard.vue'
import ComCheckCard from "@/views/door_lock/components/ComCheckCard.vue"
import ComRecentLog from "@/views/door_lock/components/ComRecentLog.vue"
import ComResetCard from "@/views/door_lock/components/ComResetCard.vue"


const selected_date = ref(null)
const toast = useToast();
const data = ref({})
const recentLogRef = ref(null)
const api = inject('$frappe')
function getData(loading = true) {
    const call = api.call();
    const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))?.date_working_day
    selected_date.value = moment(edoor_working_day).format("YYYY-MM-DD")
    call.get('edoor.api.frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: selected_date.value
    })
        .then((result) => {
            data.value = result.message
        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Waring', detail: error.exception ? error.exception.split(":")[1] : '', life: 3000 })
            gv.loading = false;

        });
}
onMounted(() => {
    getData()
})

// Filters State
const filters = ref({
  search: '',
  action: null,
  status: null,
  date: null
});

const actionOptions = ref(['Card Verification', 'Renew Guest Card', 'Write Guest Card']);
const statusOptions = ref(['Success', 'Failed']);

// Define your specific action functions
function onWriteGuestCard() {
  console.log('Writing Guest Card...');
}



// Your updated operations array
const operations = ref([
  { label: 'Write Guest Card', subtext: 'New Room Keys', icon: 'pi pi-key', color: 'text-blue-500', action: viewComWriteGuestCard },
  { label: 'Check Out Card', subtext: 'Change key card type to Check Out', icon: 'pi pi-sign-out', color: 'text-gray-500', action: onCheckOutCard },
  { label: 'Check Card', subtext: 'Verify RFID Sector', icon: 'pi pi-check-square', color: 'text-green-500', action: onVerifyCard },
  { label: 'Reset Card', subtext: 'Clear Access Sectors', icon: 'pi pi-refresh', color: 'text-red-500', action: onResetCard },
  { label: 'Master Card', subtext: 'Hotel-wide Privilege', icon: 'pi pi-shield', color: 'text-purple-500', action: null },
  { label: 'Staff Card', subtext: 'Housekeeping Pass', icon: 'pi pi-users', color: 'text-orange-500', action: null },
]);

// The master click handler
function handleCardClick(op) {
  if (op.action && typeof op.action === 'function') {
    op.action();
  } else {
    console.warn(`No action defined for: ${op.label}`);
  }
}

// Your existing log function
function viewComWriteGuestCard() {
  app.dialog.viewComWriteGuestCard("Write Guest Card");
}
function onCheckOutCard() {
  app.dialog.viewComCheckoutCard("Check Out Card");
}


async function onVerifyCard() {
   const result = await app.utils.openDialog(ComCheckCard,"Check Card");

}
async function onResetCard() {
   const result = await app.utils.openDialog(ComResetCard,"Reset Card");

}
 

async function onRefresh(){
  const l = await window.showLoading();

  await getData()
  await recentLogRef.value?.getData()
  
  l.close();
}



</script>

<style scoped>
/* Optional layout tuning to get exact design match */
.tracking-wider {
  letter-spacing: 0.05em;
}
.custom-table :deep(.p-datatable-thead > tr > th) {
  background-color: #f8f9fa;
  color: #6c757d;
  font-size: 11px;
  letter-spacing: 0.03em;
}
</style>
