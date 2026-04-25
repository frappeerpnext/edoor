<template>
        <ComRestrictionToolBar/>
        <ComRoomRestrictionGridByRoomType :year="selectedYear"/>
   
        <ComBottomAction 
        updateRestrictionText="Update Restriction"
        :selectionCount="selectedDates.size" 
        @update-restriction="onUpdateRestriction"
        :hideUpdateRate="true"  @clear-selection="onClearSelection()" 
        :selectedRestrictionTypes="restrictionTypeList"
        />
    </template>
<script setup>
import { onMounted,useRoute,ref,inject } from '@/plugin';
import ComRestrictionToolBar from "@/views/channel_managers/rate_plans/components/ComRestrictionToolBar.vue"
import ComRoomRestrictionGridByRoomType from "@/views/channel_managers/rate_plans/components/ComRoomRestrictionGridByRoomType.vue"
import ComBottomAction from "@/views/channel_managers/rate_plans/components/ComBottomAction.vue"
import {useRatePlan} from "@/views/channel_managers/rate_plans/hooks/useRatePlan.js"
import {useRestriction} from "@/views/channel_managers/rate_plans/hooks/useRestriction.js"
import ComBulkUpdateRestriction from "@/views/channel_managers/rate_plans/components/ComBulkUpdateRestriction.vue"
const frappe = inject('$frappe')
const db = frappe.db();
const property = JSON.parse(localStorage.getItem('edoor_property'))
const route = useRoute();
const {
    selectedYear,
    selectedDates,
    reloadRestrictionData

} = useRatePlan()
const {   
    restrictionTypeList
} = useRestriction();

async function onUpdateRestriction(restrictionType){
    const result = await app.utils.openDialog(ComBulkUpdateRestriction,"Update Restriction - " + restrictionType,
        {
            data:{
                rate_type: route.params.name,
                restriction_type: restrictionType
            }
        }
    );
    
    if (result){
        await reloadRestrictionData(restrictionType)
    }


}
function onClearSelection() {
    selectedDates.value = new Set();
}


onMounted(async()=>{
    await reloadRestrictionData()
})

</script>