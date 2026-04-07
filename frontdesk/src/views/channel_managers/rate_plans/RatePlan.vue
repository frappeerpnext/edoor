<template>
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh" :isSetting="true" :settingMenus="settingMenues">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">{{ $t('Rate Plan') }} - {{ rateType }}</div>
                    </div>
                </div>
            </template>
            <template #end>
                <div class="flex gap-2 w-full justify-content-end">
                    <Button @click="onBulkEdit">Bulk Edit</Button>
                    <Button @click="onBulkEdit">Open/Close Sale</Button>
                </div>
            </template>
        </ComHeader>
        <div class="bg-white border-1 p-2 rounded-xl">
            <div class="grid">
                <div class="col-2 px-4" style="min-width: 200px;">
                        <ComSidebar />   
                </div>
                <div class="col-10" style="margin-bottom: 75px;">
                    <ComFilter />
                    <ComRatePlanGridByRoomType :year="selectedYear" />
                </div>
            </div>
        </div>

        <ComBottomAction :selectionCount="selectedDates.size"  @update-rate="onBulkEdit()" @clear-selection="onClearSelection()"/>
    </div>
</template>
<script setup>
import { inject, ref,  computed, useRoute, useDialog} from '@/plugin'
import ComSidebar from "@/views/channel_managers/rate_plans/components/ComSidebar.vue"
import ComRatePlanGridByRoomType from "@/views/channel_managers/rate_plans/components/ComRatePlanGridByRoomType.vue"
import ComBulkEditRatePlan from "@/views/channel_managers/rate_plans/components/ComBulkEditRatePlan.vue"
import ComFilter from "@/views/channel_managers/rate_plans/components/ComFilter.vue"
import ComBottomAction from "@/views/channel_managers/rate_plans/components/ComBottomAction.vue"
import { i18n } from '@/i18n';


import { useRatePlan } from "./hooks/useRatePlan";
import { onUnmounted } from 'vue'
const route = useRoute();
const dialog = useDialog();

const {
    reloadRoomRatesData,
    rateType,
    settingMenues,
    resetData,
    selectedYear,
    selectedDates
} = useRatePlan();



const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem("edoor_property"))

async function onRefresh(){
    // check condition to reload, room rate or restriction

    await reloadRoomRatesData()
}

function onBulkEdit(){
     
   dialog.open(ComBulkEditRatePlan, {
        data:{
            rate_type: route.params.name
        },
        props: {
            header: $t('Bulk Edit Rate Plan') + " - " + route.params.name,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            closeOnEscape: false,
            position: "top",

        },
        onClose: (options) => {
            const data = options.data;
            if(data){
                reloadRoomRatesData()
            }
        }
    });
}

function onClearSelection(){
    selectedDates.value = new Set();
}
onUnmounted(()=>{
    resetData()
})
</script>