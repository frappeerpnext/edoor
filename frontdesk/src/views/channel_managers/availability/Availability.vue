<template>
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh"> 
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div   class="text-xl md:text-2xl white-space-nowrap">{{$t('Availability')}}</div> 
                        
                    </div>
                </div>
            </template>
            <template #end> 
                <div class="flex gap-2 w-full justify-content-end">
                     <SplitButton :disabled="selectedData.length==0" label="Action" @click="save" :model="actionMenus" />
                     <Button>Bulk Edit</Button>
                </div> 
            </template>
        </ComHeader>



<Calendar :selectOtherMonths="true"  :modelValue="filters.start_date" @date-select="onStartDateChange" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
<Calendar :selectOtherMonths="true"  :modelValue="filters.end_date" @date-select="onEndDateChange" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
 <Button @click="onClearSelection">Clear Selection</Button>
<RoomAvailability
v-if="roomTypes"
        ref="refAvailability"
  :startDate="filters.start_date"
  :endDate="filters.end_date"
  :roomTypes= "roomTypes"
  :data="data"
  @update:selected="onSelected"
  @onUpdateStatus = "onToggleUpdate"
/>
 
  </div>
</template>
<script setup>

import RoomAvailability from "@/views/channel_managers/availability/components/RoomAvailability.vue"
import { inject,  ref } from "vue";
import { i18n } from '@/i18n';
import { useAvailability } from "@/views/channel_managers/availability/hooks/useAvailability.js";
const { t: $t } = i18n.global;
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";

const confirm = useConfirm();

const {
    data,
    roomTypes,
    filters,
    onRefresh,
    refAvailability,
    selectedData,
    updateAvailabiltyRestricion,
    getData,
    toggleUpdateAvailabilityRestriction
} = useAvailability();



const moment = inject('$moment')


const actionMenus = [
    {
        label: 'Open Sale',
        command: () => {
             confirm.require({
                    message: 'Are you sure you want to proceed?',
                    header: 'Confirmation',
                    icon: 'pi pi-exclamation-triangle',
                    rejectClass: 'p-button-secondary p-button-outlined',
                    rejectLabel: 'Cancel',
                    acceptLabel: 'Yes',
                    accept: () => {
                        updateAvailabiltyRestricion(0);
                    },
         
    });

            
            
        }
    },
    {
        label: 'Stop Sale',
        command: () => {
            confirm.require({
                    message: 'Are you sure you want to proceed?',
                    header: 'Confirmation',
                    icon: 'pi pi-exclamation-triangle',
                    rejectClass: 'p-button-secondary p-button-outlined',
                    rejectLabel: 'Cancel',
                    acceptLabel: 'Yes',
                    accept: () => {
                       updateAvailabiltyRestricion(1);
                    },
                });
            
        }
    },
]


function onSelected(data){
    selectedData.value =data; 
}

async function onStartDateChange(event){
    const l = await window.showLoading();
    const date = moment.utc(moment(event).format("YYYY-MM-DD")).toDate()
    let endDate = filters.value.end_date;
    if (date>=moment.utc(filters.value.end_date).toDate()){
        endDate = moment.utc(moment(date).add(1,"month").add(-1,"day"))   
         
    }
     
 
     await getData( date,moment.utc(endDate).toDate());
    filters.value.start_date = date;
    filters.value.end_date = moment.utc(endDate).toDate();
    l.close();

}

async function onEndDateChange(event){
    const l = await window.showLoading();
    const date = moment.utc(moment(event).format("YYYY-MM-DD")).toDate()
     
    let startDate = filters.value.end_date;
    if (date<=moment.utc(filters.value.start_date).toDate()){
        startDate = moment.utc(moment(date).add(-1,"month").add(1,"day")) 
        filters.value.start_date = moment.utc(startDate).toDate();   
    }
     

    
    await getData(filters.value.start_date, date);
    filters.value.end_date = date;
    l.close();


    
 
    

}
 
function onClearSelection(){
    refAvailability.value.clearSelections()
}

async function onToggleUpdate(data){
    
    await toggleUpdateAvailabilityRestriction(data.room_type_id,data.date,data.status)
  

}


 
 
</script>
