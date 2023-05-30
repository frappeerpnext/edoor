<template>
    <h1>Housekeeping</h1>
    {{ selectedRooms }}
    {{ filter }}
    
    <ComSelect v-model="filter.selected_building" @onSelected="onSearch"
                placeholder="Building" doctype="Building" />
    <ComSelect :isMultipleSelect="true" isFilter v-model="filter.selected_room_type" optionLabel="room_type"
        optionValue="name" @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"></ComSelect>
    <ComSelect :isMultipleSelect="true" isFilter v-model="filter.selected_housekeeping_status"
        placeholder="Housekeeping Status" doctype="Housekeeping Status" @onSelected="onSearch" />
        <ComSelect isFilter v-model="filter.selected_housekeeping_status" placeholder="Housekeeper"
                doctype="Housekeeper" @onSelected="onSearch" />
    
    
    <Button label=" Change Housekeeping Status" severity="warning" @click="onChangeHousekeepingStatus" />

    <Dialog v-model:visible="visibleHousekeepingStatus" modal header="Change Housekeeping Status"
        :style="{ width: '50vw' }">
        <div>
            <ComSelect isFilter v-model="filter.housekeeping_status_to_change" placeholder="Housekeeping Status"
                doctype="Housekeeping Status" @onSelected="onSearch" />

        </div>
        <template #footer>
            <Button label="No" icon="pi pi-times" @click="visibleHousekeepingStatus = false" text />
            <Button label="Yes" icon="pi pi-check" @click="visibleHousekeepingStatus = false" autofocus />
        </template>
    </Dialog>

    <Button label="Assign Housekeeper" severity="waring" @click="AssingnHousekeeper" />

    <Dialog v-model:visible="visibleAssignHousekeeper" modal header="Assign Housekeeper" :style="{ width: '50vw' }">
        <p>
            <ComSelect isFilter v-model="filter.selected_housekeeping_status" placeholder="Housekeeper"
                doctype="Housekeeper" @onSelected="onSearch" />
        </p>
        <template #footer>
            <Button label="No" icon="pi pi-times" @click="visible = false" text />
            <Button label="Yes" icon="pi pi-check" @click="visible = false" autofocus />
        </template>
    </Dialog>
    <DataTable v-model:selection="selectedRooms" dataKey="name" :value="room_list" tableStyle="min-width: 50rem">
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="room_number" header="Room #"></Column>
        <Column field="room_type" header="Room Type"></Column>
        <Column field="room_type" header="Room Type"></Column>

        <Column field="housekeeper" header="Housekeeper"></Column>
        <Column field="housekeeping_status" header="Status">
            <template #body="slotProps">
                <Tag :value="slotProps.data.housekeeping_status" :style="{ background: slotProps.data.status_color }"></Tag>
            </template>
        </Column>
        <Column field="housekeeping_status" header="Status">
            <template #body="slotProps">
                <SplitButton label="Change Status" :model="houseKeepingStatus" @onItemClick="onItemClick('xx')">
                   
                </SplitButton>
                
            </template>
        </Column>
    </DataTable>
</template>

<script setup>

import { ref, inject, useToast, onMounted } from "@/plugin"
import Tag from 'primevue/tag';

const frappe = inject("$frappe")
const db = frappe.db()

const toast = useToast();

const filter = ref({})
const room_list = ref([])
const selectedRooms = ref([])


const houseKeepingStatus = ref([])
const onSearch = debouncer(() => {
    loadData();
}, 500);
const visibleHousekeepingStatus = ref(false);
const visibleAssignHousekeeper = ref(false);

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

loadData()

const onItemClick = ($event) => {
      alert(1)
      console.log($event);
    };
    
function loadData() {
    let filters = []
    if (filter.value.selected_room_type && filter.value.selected_room_type.length > 0) {
        filters.push(["room_type_id", 'in', filter.value.selected_room_type])

    }
    if (filter.value.selected_housekeeping_status && filter.value.selected_housekeeping_status.length > 0) {
        filters.push(["housekeeping_status", 'in', filter.value.selected_housekeeping_status])
    }


    db.getDocList('Room', {
        fields: ['name', "room_type_id", "room_type", "room_number", "housekeeping_status", "status_color", "housekeeper",],
        filters: filters,
        limit: 1000,
    })
        .then((docs) => {
            console.log(docs)
            room_list.value = docs
        }
        )
        .catch((error) => console.error(error));


}
function onChangeHousekeepingStatus() {

    if (selectedRooms.value.length == 0) {
        toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select room to change housekeeping status", life: 3000 })
    } else {
        visibleHousekeepingStatus.value = true;
    }

}
function AssingnHousekeeper() {

    if (selectedRooms.value.length == 0) {
        toast.add({ severity: 'warn', summary: "AssingnHousekeeper", detail: "Please select room to assign in housekeeper", life: 3000 })
    } else {
        visibleAssignHousekeeper.value = true;
    }
}

onMounted(() => {
    db.getDocList('Housekeeping Status', {
        fields: ['name', "icon", "status_color"],
    })
        .then((x) => {
            x.forEach(d => {
                houseKeepingStatus.value.push(
                    {
                        labelx: d.name,
                        icon: d.icon,
                        command: (x) => {

 

                            // db.updateDoc('Room', 'RM-0001', {
                            //     housekeeping_status: 'Occ Dirty',
                            // })
                            //     .then((doc) => console.log(doc))
                            //     .catch((error) => console.error(error));


                            // toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                        }
                    }
                )
            }
            );
        }
        )
        .catch((error) => console.error(error));
}
)
</script>