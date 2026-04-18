<template>
    <div>
        <ComHeader :isRefresh="true" @onRefresh="onRefresh">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div class="text-xl md:text-2xl white-space-nowrap">{{ $t('Rate Plan') }} - {{ rateType }}</div>
                    </div>
                </div>
            </template>
            <template #end>
                  
                <div class="flex gap-2 w-full justify-content-end">
                    <Button @click="onViewSyncStatus" class="border-0"  >{{$t("Sync Status")}}</Button>
                    
                </div>
            </template>
        </ComHeader>
        <div class="bg-white border-1 p-2 rounded-xl">
            <Button 
                v-for="(t,index) in components" :label="t.title" 
                :severity="selectedComponent == t.component?'warning':''"
                @click="onSelectComponent(t.component)"
                class="border-0"
             ></Button> 
            <div v-if="selectedComponent"> 
                <ComSyncStatus method="Prices update"/>
              
                <component  :is="componentsMap[selectedComponent]"/>
            </div> 
        </div> 
    </div>
</template>
<script setup>
 import { i18n } from '@/i18n';


import { useRatePlan } from "./hooks/useRatePlan";
import { inject, onMounted, onUnmounted } from 'vue'
import ComSyncStatus from "@/views/channel_managers/rate_plans/components/ComSyncStatus.vue"
import ComChannelManagerSyncStatus from "@/views/channel_managers/components/ComChannelManagerSyncStatus.vue"
 
const { 
    components,
    selectedComponent,
    rateType,
    componentsMap,
    resetData
    
} = useRatePlan();



const { t: $t } = i18n.global;

function onSelectComponent(component){
    selectedComponent.value = component
}

function onViewSyncStatus(){
     app.utils.openDialog(ComChannelManagerSyncStatus,"Channel Manager Sync Status")
}

onMounted(()=>{
       window.socket.on("ChannelManagerUpdate", (arg) => {
        if (arg.action == "update_sync_rate_plan_status" ) {
            if(arg.status?.toLowerCase()=="success"){
                app.utils.showSuccess(arg.title,arg.message,0,"tr",{hello:"World"})
            }else {
               
                app.utils.showWarning(arg.title,arg.message,0,"tr",{action_title:"View sync log","action":"view_channel_manager_sync_log|" + arg.docname})
            }
           
        }
    })
})
 
onUnmounted(()=>{
    resetData()
    window.socket.off("ChannelManagerUpdate")
})
</script>