<template>
    <h1>Housekeeping</h1>
    {{ selectedRooms }}
   
    <ComAutoComplete v-model="data.room_type" placeholder="Room Type" doctype="Room Type"   />
    <ComAutoComplete v-model="data.housekeeping_status" placeholder="Housekeeping Status" doctype="Housekeeping Status"   />

    <DataTable v-model:selection="selectedRooms"  dataKey="name" :value="room_list" tableStyle="min-width: 50rem">
        <Column selectionMode="multiple" headerStyle="width: 3rem"></Column>
        <Column field="room_number" header="Room #"></Column>
        <Column field="room_type" header="Room Type"></Column>
        <Column field="housekeeping_status" header="Status">
            <template #body="slotProps">
            <Tag :value="slotProps.data.housekeeping_status" :style="{ background: slotProps.data.status_color }" ></Tag>
        </template>
    </Column>
        <Column field="housekeeping_status" header="Status">
            <template #body="slotProps">
                <SplitButton label="Change Status" :model="houseKeepingStatus">
                
                </SplitButton>
        </template>
    </Column>
 
    </DataTable>
</template>
<script setup>
    import {ref,inject} from "@/plugin"
    import Tag from 'primevue/tag';
    import { useToast } from "primevue/usetoast";
    const frappe = inject("$frappe")
    const db = frappe.db()

const toast = useToast();
    const data = ref({})
    const room_list = ref([])
    const selectedRooms = ref([])

    
const houseKeepingStatus =ref([])  


    db.getDocList('Room',{
        fields: ['name',"room_type_id","room_type","room_number","housekeeping_status","status_color"],
    })
    .then((docs) => 
    {
        console.log(docs)
        room_list.value = docs
    }
    )
    .catch((error) => console.error(error));

    db.getDocList('Housekeeping Status',{
        fields: ['name',"icon","status_color"],
    })
    .then((docs) => 
    {
       docs.forEach(d => {
        houseKeepingStatus.value.push(
            {
                label: d.name,
                icon: d.icon,
                command: (x) => {
                  
                  console.log(x)

                    // toast.add({ severity: 'success', summary: 'Updated', detail: 'Data Updated', life: 3000 });
                }
            }
                )
       });
         
    }
    )
    .catch((error) => console.error(error));


</script>