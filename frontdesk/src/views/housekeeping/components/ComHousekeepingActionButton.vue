<template>
    <Button label=" Change Housekeeping Status" severity="warning" @click="onChangeHousekeepingStatus" />

    <Dialog v-model:visible="visibleHousekeepingStatus" modal header="Change Housekeeping Status"
        :style="{ width: '30vw' }">
        <div>
            <ComSelect isFilter v-model="selectedStatus" placeholder="Housekeeping Status" doctype="Housekeeping Status" />
        </div>
        <template #footer>
            <Button label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" />
            <Button label="Yes" icon="pi pi-check" @click="onSaveChangeHousekeepingStatus" autofocus
                :loading="submitLoading" />
        </template>
    </Dialog>

    <Button label="Assign Housekeeper" severity="waring" @click="AssingnHousekeeper" />

    <Dialog v-model:visible="visibleAssignHousekeeper" modal header="Assign Housekeeper" :style="{ width: '30vw' }">
        <div>
            <ComSelect isFilter v-model="selectedHousekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper" />

        </div>
        <template #footer>
            <Button label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" />
            <Button label="Yes" icon="pi pi-check" @click="onSaveAssignHousekeeper" autofocus :loading="submitLoading" />
        </template>
    </Dialog>
</template>
<script setup>
import { ref, inject, useToast } from '@/plugin';

const toast = useToast();
const hk = inject("$housekeeping")
const frappe = inject("$frappe")

const call = frappe.call()
const visibleHousekeepingStatus = ref(false)
const visibleAssignHousekeeper = ref(false)
const submitLoading = ref(false)
const selectedStatus = ref("")
const selectedHousekeeper = ref("")

function onChangeHousekeepingStatus() {

    if (hk.selectedRooms.length == 0) {
        toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select room to change housekeeping status", life: 3000 })
    } else {
        visibleHousekeepingStatus.value = true;
    }
}

function AssingnHousekeeper() {

    if (hk.selectedRooms.length == 0) {
        toast.add({ severity: 'warn', summary: "Assingn Housekeeper", detail: "Please select room to assign in housekeeper", life: 3000 })
    } else {
        visibleAssignHousekeeper.value = true;
    }
}

function onSaveChangeHousekeepingStatus() {
    submitLoading.value = true;
    const rooms = hk.selectedRooms.map(r => r.name).join(",");
    call.post("edoor.api.housekeeping.update_housekeeping_status", {
        rooms: rooms,
        status: selectedStatus.value
    }).then((result) => {
        visibleHousekeepingStatus.value = false
        hk.selectedRooms = []
        toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
        hk.loadData()
        submitLoading.value = false
        selectedStatus.value = ""
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