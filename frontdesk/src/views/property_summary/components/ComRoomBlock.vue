<template>
<DataTable :value="data" paginator  :rows="20" tableStyle="min-width: 50rem">
    <Column header="No" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column field="name" header="Block #">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_room_block_detail',slotProps.data.name)" link>
            {{ slotProps?.data.name }}
            </Button>
        </template>
    </Column>
    <Column  header="Block Date">
        <template  #body="slotProps">
            
            {{ moment(slotProps?.data.block_date).format("DD-MM-YYYY") }}
        </template>
       
    </Column>
    
    <Column  header="Start Date">
        <template  #body="slotProps">
            {{ moment(slotProps?.data.start_date).format("DD-MM-YYYY") }}
        </template>
    </Column>
    
    <Column  header="Release Date">
        <template  #body="slotProps">
            {{ moment(slotProps?.data.end_date).format("DD-MM-YYYY") }}
        </template>
    </Column>
    <Column  field="total_night_count" header="Nights" headerClass="text-center" bodyClass="text-center"/>
    <Column  field="room_type" header="Room Type"/>
    <Column  field="room_number" header="Room Number" headerClass="text-center" bodyClass="text-center"/>
    <Column  header="Status">
        <template  #body="slotProps">
            <span v-if="slotProps.data.is_unblock==0">Blocked</span>
            <span v-else>Unblocked</span>
        </template>
    </Column>
    <Column  header="Block By">
        <template  #body="slotProps">
            {{ slotProps.data.owner.split("@")[0] }}
        </template>
    </Column>
    <Column  field="reason" header="Reason"/>
</DataTable>

</template>
<script setup>
import { inject } from '@/plugin';
const moment = inject("$moment")
const props = defineProps({
    data:Object
})
function onViewDetail(action,name){
    
    window.postMessage(action + "|" + name,"*")
}    
</script>