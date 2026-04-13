<template>
<div>
     <ComHeader :isRefresh="true" @onRefresh="onRefresh"> 
                <template #start>
                    <div class="flex">
                        <div class="flex align-items-center justify-content-between w-full">
                            <div   class="text-xl md:text-2xl white-space-nowrap">{{$t('Rate Plan')}}</div> 
                            
                        </div>
                    </div>
                </template>
                <template #end> 
                    <div class="flex gap-2 w-full justify-content-end">
                         <Button>Bulk Edit</Button>
                    </div> 
                </template>
            </ComHeader>
            <div class="bg-white border-1 p-2 rounded-xl">
   {{ data }}             
<DataTable :value="data" tableStyle="min-width: 50rem">
    <Column   header="Rate Plan">
       <template #body="slotProps">
         <RouterLink class="p-button p-component p-button-link link_line_action1" :to="`/frontdesk/channel-manager/rate-plan/${encodeURIComponent(slotProps.data.edoor_rate_plan)}`">{{  slotProps.data.rate_plan_name }}</RouterLink>
            
        </template>
    </Column>
    
    <Column   header="Prices Set Date">
       <template #body="slotProps"> 
            <template v-if="slotProps.data?.room_rates_max_min_date.length > 0">
                {{slotProps.data.room_rates_max_min_date.map(r=>moment(r.start_date).format("DD-MM-yyyy")).join('')}} &#8594;
                {{slotProps.data.room_rates_max_min_date.map(r=>moment(r.start_end).format("DD-MM-yyyy")).join('')}}
            </template>    
        </template>
    </Column>
    
    <Column   header="Restriction">
       <template #body="slotProps">
            Close Sale <br/>
            CTA <br/>
            CTD
        </template>
    </Column>
    <Column   header="Rate and Restriction Period">
       <template #body="slotProps">
            Min max date to display and can update 
        </template>
    </Column>
    <Column   header="Connted with Channel Manager">
       <template #body="slotProps">
            <Checkbox v-model="checked" :binary="true" :trueValue="1" :falseValue="0" @change="checked = 1"/>
            connected
        </template>
    </Column>


    
</DataTable>
            </div>
    
    
</div>
    </template>
    <script setup>
import { inject,  onMounted,  ref } from "vue";
import { i18n } from '@/i18n';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
const moment= inject("$moment")
const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem("edoor_property"))
const data = ref([])
const checked = ref(1)
async function getRatePlanList(){
    const l = await window.showLoading()
    const res = await app.getApi("rate_plan.get_rate_plan_list",{
        property: property.name
    })
    if (res.data){
        data.value = res.data
    }

    l.close()
}
onMounted(async ()=>{
await getRatePlanList()
})
</script>