<template>
    <div v-if="!isMobile" class="flex gap-2">
        <div>
            <Button :label="$t('Change Housekeeping Status') " class="p-button h-full p-component conten-btn white-space-nowrap"
                severity="warning" @click="onChangeHousekeepingStatus">
                {{ $t('Change Housekeeping Status') }}
                
                <Badge style="font-weight: 600 !important;" class="badge-rs bg-white text-500"
                    :value="hk?.selectedRooms?.length" severity="warning"></Badge>
            </Button>
        </div>
        <div>
            <Button label="Assign Housekeeper"
                class="p-button h-full p-component conten-btn border-r-orange-300 white-space-nowrap"
                @click="AssingnHousekeeper">
                {{ $t('Assign Housekeeper') }}
                
                <Badge style="font-weight: 600 !important;color:#4338ca;border-color:#4338ca;"
                    class="border-1 bg-transparent flex justify-center items-center" :value="hk?.selectedRooms?.length"
                    severity="warning">
                </Badge>
            </Button>
        </div>
    </div>
    <SplitButton v-else class="border-split-none w-full flex  justify-content-end " :model="items_action" >
   <div class="bg-blue-500 ps-4 text-white border-round-left  flex align-items-center pe-5">
    <Badge style="font-weight: 600 !important;" class="badge-rs bg-white text-500 me-4"
                    :value="hk?.selectedRooms?.length" severity="warning"></Badge>
                    {{ $t('Action') }}
    
   </div>
    </SplitButton>
    <Dialog v-model:visible="visibleHousekeepingStatus" modal header="Change Housekeeping Status" :style="{ width: isMobile ? '100vw' : '30vw' }"
        position="top">
        <div> 
            <ComSelect isFilter placeholder="Housekeeping Status" class="w-full" optionLabel="label" optionValue="status"
                v-model="selectedHouseKeepingStatusCode" :options="housekeeping_status_code"
                :filters="{ is_block_room: 0 }" />
        </div>
        <template #footer>
            <!-- <Button class="border-none" label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" /> -->
            <Button class="border-none" :label="$t('Ok')" icon="pi pi-check-circle" @click="onSaveChangeHousekeepingStatus"
                autofocus :loading="submitLoading" />
        </template>
    </Dialog>
    <Dialog v-model:visible="visibleAssignHousekeeper" modal :header="$t('Assign Housekeeper')" :style="{ width: isMobile ? '100vw' : '30vw' }"
        position="top">
        <div>
            <ComSelect isFilter v-model="selectedHousekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper" />
        </div>
        <template #footer>
            <!-- <Button class="border-none" label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" /> -->
            <Button class="border-none" :label="$t('Ok')" icon="pi pi-check-circle" @click="onSaveAssignHousekeeper" autofocus
                :loading="submitLoading" />
        </template>
    </Dialog>
</template>
<script setup>
import { ref, inject, useToast, postApi } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const toast = useToast();
const hk = inject("$housekeeping")

const frappe = inject("$frappe")
const call = frappe.call()
const visibleHousekeepingStatus = ref(false)
const visibleAssignHousekeeper = ref(false)
const submitLoading = ref(false)
const isMobile = ref(window.isMobile) 
const selectedHouseKeepingStatusCode = ref("")
const selectedHousekeeper = ref("")
const gv = inject("$gv")
const items_action = ref([])
items_action.value.push({
    label: "Change Housekeeping Status",
    command: () => {
        onChangeHousekeepingStatus()
    }
})
items_action.value.push({
    label: "Assign Housekeeper",
    command: () => {
        AssingnHousekeeper()
    }
})
const housekeeping_status_code = ref(window.setting.housekeeping_status_code);
housekeeping_status_code.value.forEach(item => {
  item.label = $t(item.status);
});
function onChangeHousekeepingStatus() {
    selectedHouseKeepingStatusCode.value = housekeeping_status_code.value[0].status
    if (!gv.cashier_shift?.name) {
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    if (hk.selectedRooms.length == 0) {
        toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select room to change housekeeping status", life: 3000 })
    } else {
        visibleHousekeepingStatus.value = true;
    }
}

function AssingnHousekeeper() {
    if (!gv.cashier_shift?.name) {
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    if (hk.selectedRooms.length == 0) {
        toast.add({ severity: 'warn', summary: "Assingn Housekeeper", detail: "Please select room to assign in housekeeper", life: 3000 })
    } else {
        visibleAssignHousekeeper.value = true;
    }
}

function onSaveChangeHousekeepingStatus() {
    submitLoading.value = true;
    const rooms = hk.selectedRooms.map(r => r.name).join(",");
    postApi("housekeeping.update_housekeeping_status", {
        rooms: rooms,
        property: window.property_name,
        status: selectedHouseKeepingStatusCode.value
    }).then((result) => {
        visibleHousekeepingStatus.value = false
        hk.loadData().then((r) => {
            hk.selectedRooms = []
        })
        window.postMessage({"action":"ComHousekeepingStatus"},"*")
        submitLoading.value = false
        selectedHouseKeepingStatusCode.value = ""
    })
        .catch((err) => {
            submitLoading.value = false
        })
}
function onSaveAssignHousekeeper() {
    submitLoading.value = true;
    const rooms = hk.selectedRooms.map(r => r.name).join(",");
    call.post("edoor.api.housekeeping.update_housekeeper", {
        rooms: rooms,
        housekeeper: selectedHousekeeper.value
    }).then((result) => {
        visibleAssignHousekeeper.value = false
        hk.selectedRooms = []
        toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping successfully", life: 3000 })
        hk.loadData()
        submitLoading.value = false
        selectedHousekeeper.value = ""
    })
        .catch((err) => {
            submitLoading.value = false
        })
}


</script>