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
                    <Button class="border-0">{{$t("Sync Now")}}</Button>
                    
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
                <Message>{{ syncRoomRateActionStatus }} </Message>
            
                <component  :is="componentsMap[selectedComponent]"/>
            </div> 
        </div> 
    </div>
</template>
<script setup>
 import { i18n } from '@/i18n';


import { useRatePlan } from "./hooks/useRatePlan";
import { onUnmounted } from 'vue'
 
 
const { 
    components,
    selectedComponent,
    rateType,
    componentsMap,
    syncRoomRateActionStatus,
    resetData
    
} = useRatePlan();



const { t: $t } = i18n.global;

function onSelectComponent(component){
    selectedComponent.value = component
}
 
 
onUnmounted(()=>{
    resetData()
})
</script>