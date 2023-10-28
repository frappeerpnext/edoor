<template>
    <div class="flex gap-2">
        <div>
            <Button label=" Change Housekeeping Status" class="p-button h-full p-component conten-btn white-space-nowrap" severity="warning" @click="onChangeHousekeepingStatus" >
                Change Housekeeping Status 
                <Badge style="font-weight: 600 !important;" class="badge-rs bg-white text-500" :value="hk?.selectedRooms?.length" severity="warning"></Badge>
            </Button>
        </div>
        <div>
            <Button label="Assign Housekeeper" class="p-button h-full p-component conten-btn border-r-orange-300 white-space-nowrap" @click="AssingnHousekeeper" >
                Assign Housekeeper
                <Badge style="font-weight: 600 !important;color:#4338ca;border-color:#4338ca;" class="border-1 bg-transparent flex justify-center items-center" :value="hk?.selectedRooms?.length"
                severity="warning">
                </Badge>
            </Button>
        </div>
    </div> 
    <Dialog v-model:visible="visibleHousekeepingStatus" modal header="Change Housekeeping Status"
        :style="{ width: '30vw' }" position="top">
        <div>
            <ComSelect isFilter v-model="selectedStatus" placeholder="Housekeeping Status" doctype="Housekeeping Status" :filters="{is_block_room:0}" />
        </div>
        <template #footer>
            <!-- <Button class="border-none" label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" /> -->
            <Button class="border-none" label="Ok" icon="pi pi-check-circle" @click="onSaveChangeHousekeepingStatus" autofocus
                :loading="submitLoading" />
        </template>
    </Dialog>
    <Dialog v-model:visible="visibleAssignHousekeeper" modal header="Assign Housekeeper" :style="{ width: '30vw' }" position="top">
        <div>
            <ComSelect isFilter v-model="selectedHousekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper" />
        </div>
        <template #footer>
            <!-- <Button class="border-none" label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text v-if="!submitLoading" /> -->
            <Button class="border-none" label="Ok" icon="pi pi-check-circle" @click="onSaveAssignHousekeeper" autofocus :loading="submitLoading" />
        </template>
    </Dialog>
</template>
<script setup>
import { ref, inject, useToast,postApi } from '@/plugin';

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
    postApi("housekeeping.update_housekeeping_status", {
        rooms: rooms,
        status: selectedStatus.value
    }).then((result) => {
        visibleHousekeepingStatus.value = false
        hk.loadData().then((r)=>{
            hk.selectedRooms = []
        })
        window.socket.emit("ComHousekeepingStatus", window.property_name)
        submitLoading.value = false
        selectedStatus.value = ""
    })
    .catch((err) => {
        submitLoading.value = false
    })
}
function onSaveAssignHousekeeper(){
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