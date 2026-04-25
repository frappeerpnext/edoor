<template> 
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh" :isSetting="true" :settingMenus="settingMenues">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center gap-2 w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">
                            {{ $t('Rate Plan') }} - {{ rateType }}
                        </div>
                        <Tag v-if="prodiverName" :value="`connected with ${prodiverName}`" class="border-round"/>
                    </div>
                </div>
            </template>
            <template #end>
                  
                <div class="flex gap-2 w-full justify-content-end">
                  <SplitButton
  label="Close/Open Sales"
  icon="pi pi-bars"
  class="border-0"
  :model="restrictionMenuItems"
  @click="onOpenCloseSalesDialog('Closed')"
/>
                    
                    <Button @click="onViewSyncStatus" class="border-0"  >{{$t("Sync Status")}}</Button>
                    
                </div>
            </template>
        </ComHeader>
        <div class="bg-white border-1 p-2 rounded-xl">
            <div class="tabs">
                <Button v-for="(t,index) in components" :label="t.title" @click="onSelectComponent(t.component)" class="tab" :class="selectedComponent == t.component?'active':''"></Button> 
            </div>
            <div v-if="selectedComponent"> 
                <ComSyncStatus :method="['Prices update','Restriction update']" v-if="rateInfo?.cm_rate_plan_list?.cm_rate_plan" />
                <br/> 
                <component  :is="componentsMap[selectedComponent]"/> 
            </div> 
        </div> 
    </div>
</template>
<script setup>
import Tag from 'primevue/tag';
import { i18n } from '@/i18n';
import { useRatePlan } from "./hooks/useRatePlan";
import { useRestriction } from "./hooks/useRestriction";
import { inject, onMounted, onUnmounted } from 'vue'
import { useRoute , computed } from '@/plugin'
import ComSyncStatus from "@/views/channel_managers/rate_plans/components/ComSyncStatus.vue"
import ComChannelManagerSyncStatus from "@/views/channel_managers/components/ComChannelManagerSyncStatus.vue"
import ComBulkUpdateRestriction from '@/views/channel_managers/rate_plans/components/ComBulkUpdateRestriction.vue'; 
const route = useRoute()
const { 
    components,
    selectedComponent,
    rateType,
    componentsMap,
    rateInfo,
    prodiverName,
    settingMenues,
    onRefresh,
    resetData,
    reloadRestrictionData


    
} = useRatePlan();
const { 
    loadRestrictionTypeList,    
    restrictionTypeList
} = useRestriction();

const restrictionMenuItems = computed(() => {
  return restrictionTypeList.value.map(item => ({
    label: item,
    command: () => onOpenCloseSalesDialog(item)
  }))
})
async function onOpenCloseSalesDialog(restriction_type) {
    const    result = await app.utils.openDialog (ComBulkUpdateRestriction,"Update Restriction - " + restriction_type, {
        data:{
            rate_type: route.params.name,
            restriction_type: restriction_type
        },
    });
    if (result){
     await reloadRestrictionData('Closed')
    }
}

const { t: $t } = i18n.global;

function onSelectComponent(component){
    selectedComponent.value = component
}

function onViewSyncStatus(){
     app.utils.openDialog(ComChannelManagerSyncStatus,"Channel Manager Sync Status")
}

onMounted(()=>{
    loadRestrictionTypeList()
       window.socket.on("ChannelManagerUpdateRatePlan", (arg) => {
        
            if(arg.status?.toLowerCase()=="success"){
                app.utils.showSuccess(arg.title,arg.message,0,"tr")
            }else {
               
                app.utils.showWarning(arg.title,arg.message,0,"tr",{action_title:"View sync log","action":"view_channel_manager_sync_log|" + arg.docname})
            }
           
         
    })
})
 
onUnmounted(()=>{
    resetData()
    window.socket.off("ChannelManagerUpdateRatePlan")
})
</script>
<style scoped>
.tabs {
    display: flex; 
    background: #fff;
    border-top: 12px;
    width: fit-content; 
}

.tab {
    position: relative;
    padding: 6px 10px !important;
    border: none; 
    font-size: 14px;
    font-weight: 500;
    color: #555;
    border-top-left-radius: 8px;
    border-top-left-radius: 8px;
    border-bottom-left-radius: 0px !important;
    border-bottom-right-radius: 0px !important;
    /* border-bottom: 1px solid var(--btn-border-color); */
    cursor: pointer;
    transition: all 0.25s ease;   
    background: linear-gradient(to bottom, #ffffff 0%, #d1e1ee 100%);
    border-left: 1px solid transparent;
    border-right: 1px solid transparent;  
    border-top: 3px solid #fff;  
    
}

/* Hover effect */
.tab:hover {
    border-top: 3px solid #6c63ff;
    border-left: 1px solid var(--btn-border-color);
    border-right: 1px solid var(--btn-border-color);
    background: rgba(0, 123, 255, 0.08);
    color: #6c63ff;
}

/* Active tab */
.tab.active { 
    color: #6c63ff;
    border-top: 3px solid #6c63ff;
    border-left: 1px solid var(--btn-border-color);
    border-right: 1px solid var(--btn-border-color);
    border-bottom: 0; 
}

/* Optional bottom indicator */
.tab.active::after {
    content: "";
    position: absolute;
    bottom: -6px;
    left: 20%;
    width: 60%;
    height: 3px;
    background: #6c63ff;
    border-radius: 10px;
}
 
</style>