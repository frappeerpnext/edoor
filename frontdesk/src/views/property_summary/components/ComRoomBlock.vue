<template>
<DataTable :value="data" paginator  :rows="20" tableStyle="min-width: 50rem">
    <Column :header="$t('No')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column field="name" :header="$t('Block') + ' #' ">
        <template  #body="slotProps">
            <Button class="p-0 link_line_action1" @click="onViewDetail('view_room_block_detail',slotProps.data.name)" link>
            {{ slotProps?.data.name }}
            </Button>
        </template>
    </Column>
    <Column  :header="$t('Block Date') ">
        <template  #body="slotProps">
            
            {{ moment(slotProps?.data.block_date).format("DD-MM-YYYY") }}
        </template>
       
    </Column>
    
    <Column  :header="$t('Start Date')">
        <template  #body="slotProps">
            {{ moment(slotProps?.data.start_date).format("DD-MM-YYYY") }}
        </template>
    </Column>
    
    <Column  :header="$t('Release Date')">
        <template  #body="slotProps">
            {{ moment(slotProps?.data.end_date).format("DD-MM-YYYY") }}
        </template>
    </Column>
    <Column  field="total_night_count" :header="$t('Nights')" headerClass="text-center" bodyClass="text-center"/>
    <Column  field="room_type" :header="$t('Room Type')"/>
    <Column  field="room_number" :header="$t('Room Number')" headerClass="text-center" bodyClass="text-center"/>
    <Column  :header="$t('Status')">
        <template  #body="slotProps">
            <span v-if="slotProps.data.is_unblock==0">Blocked</span>
            <span v-else>Unblocked</span>
        </template>
    </Column>
    <Column  :header="$t('Block By')">
        <template  #body="slotProps">
            {{ slotProps.data.owner.split("@")[0] }}
        </template>
    </Column>
    <Column  field="reason" :header="$t('Reason')"/>
</DataTable>

</template>
<script setup>
import { inject } from '@/plugin';
const moment = inject("$moment")
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    data:Object
})
function onViewDetail(action,name){
    
    window.postMessage(action + "|" + name,"*")
}    
</script>