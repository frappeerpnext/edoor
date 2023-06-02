<template>
    <div>
        <h1>housekeeping room detail</h1>
        {{ hk.selectedRow}} 
        <SplitButton label="Change House Status" :model="items" @click="onUpdateStatus"/>
        
       </div>

       
</template>
<script setup>
import { inject, ref} from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue';
const hk = inject("$housekeeping")
const edoor_setting = JSON.parse(localStorage.getItem('edoor_setting'))
const housekeeping_status = ref(edoor_setting.housekeeping_status)
const items = ref([])
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

function onSelected($event){
    alert(hk.selectedRow.name)
    alert($event.status)
    
    hk.selectedRow.housekeeping_status = "xxx"

}
function onUpdateStatus($event){ 
    alert($event)
    hk.updateRoomStatus(hk.selectedRow.name,$event.item.label)
}


</script>