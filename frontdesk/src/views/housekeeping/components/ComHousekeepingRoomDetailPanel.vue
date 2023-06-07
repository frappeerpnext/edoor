<template>
    <div>
       {{ hk.selectedRow }}
         <SplitButton :buttonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" :label="hk.selectedRow?.housekeeping_status"  :model="items" :color="hk.selectedRow?.status_color"  :menuButtonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" >
        </SplitButton>  
    </div>

    <Button label="Assign Housekeeper" severity="warning" @click="onAssignHousekeeper($event)" ></Button>
    <OverlayPanel ref="opHousekeeper">
        <ComOverlayPanelContent :loading="loading"  @onCancel="onAssignHousekeeper($event,{})" @onSave="onSaveAssignHousekeeper">
            <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper"  />
        </ComOverlayPanelContent>
    </OverlayPanel>

</template>

<script setup>
import { inject, ref, useToast} from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue';
const hk = inject("$housekeeping")
const edoor_setting = JSON.parse(localStorage.getItem('edoor_setting'))
const housekeeping_status = ref(edoor_setting.housekeeping_status)
const visible = ref(false)
const toast = useToast();
const opHousekeeper = ref()
const selected = ref({})

const  submitLoading = ref(false)
const items = ref([])
const show = ref()
const frappe = inject("$frappe")
const db = frappe.db()
const call = frappe.call()

if(housekeeping_status.value.length > 0){
    housekeeping_status.value.forEach(h => {
        items.value.push({
            label: h.status,
            command: () => {
                onSelected(h)
            }
        })
         
    });
}

/// change housekeeping status
const toggle = (event) => {
    show.value.toggle(event);
};

/// change housekeeping status
function onSelected($event){
    if (!hk.selectedRow) {
    toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select roow to change housekeeping status", life: 3000 })
} else {
    db.updateDoc('Room', hk.selectedRow.name, {
        housekeeping_status: $event.status,
        status_color : $event.status_color,
    })

    .then((doc) =>{
        visible.value = false 
        hk.selectedRow.housekeeping_status = doc.housekeeping_status
        hk.selectedRow.status_color = doc.status_color
        console.log(doc.housekeeping_status)
        toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
        hk.loadData()
        submitLoading.value = false
    })
    .catch((error) => {
        submitLoading.value = false
    });
}
}

// Housekeeper
function onAssignHousekeeper($event){
    opHousekeeper.value.toggle($event)
}

function onSaveAssignHousekeeper($event) {
    alert(selected.value.housekeeper)
    db.updateDoc('Room', hk.selectedRow.name, {
        housekeeper:selected.value.housekeeper,
    })
    loading.value = true; 
  
}

</script>