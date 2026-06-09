<template>
        <ComRestrictionToolBar/>
        <ComRoomRestrictionGridByRoomType :year="selectedYear"/> 
   
        <ComBottomAction 
        updateRestrictionText="Update Restriction"
        :selectionCount="selectedDates.size" 
        @update-restriction="onUpdateRestriction"
        :hideUpdateRate="true"  @clear-selection="onClearSelection()" 
        :selectedRestrictionTypes="restrictionManageByCM" 
        v-if="cm_info?.restrictions == 'Receive from PMS'"
        />
    </template>
<script setup>
import { onMounted,useRoute,ref,inject , computed } from '@/plugin';
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
    reloadRestrictionData,
    restrictionTypes,
    cm_info

} = useRatePlan()

const restrictionManageByCM = computed(()=>{
  const _data = []
  if (cm_info.value.closed==1){
    _data.push("Closed")
  }
  if (cm_info.value.cta==1){
    _data.push("Cta")
  }
  if (cm_info.value.ctd==1){
    _data.push("Ctd")
  }
  if (cm_info.value.minlos==1){
    _data.push("MinLos")
  }
  
  if (cm_info.value.maxlos==1){
    _data.push("MaxLos")
  }
  
  if (cm_info.value.minlosarrival==1){
    _data.push("MinLosArrival")
  }
  
  if (cm_info.value.maxlosarrival==1){
    _data.push("MaxLosArrival")
  }
  
  if (cm_info.value.minadvbooking==1){
    _data.push("MinAdvBooking")
  }
  
  if (cm_info.value.maxadvbooking==1){
    _data.push("MaxAdvBooking")
  }
  if (cm_info.value.fullpatternlos==1){
    _data.push("FullPatternLos")
  }


return _data



})

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