<template>
    <div v-if="cmInfo?.provider" style="padding: 0.6rem 0.65rem;margin-top: 3px;" v-tippy="'Channel Manager Sync Status'">
        <ProgressSpinner v-if="isLoading" style="width: 25px; height: 25p8" strokeWidth="8" animationDuration="2.5s"
            aria-label="Custom ProgressSpinner" />

        <div v-else>
            <i v-if="totalTaskCount > 0" ref="btn" v-badge.danger="totalTaskCount" @click="onToggle"
                class="pi pi-globe cursor-pointer text-white" style="font-size:18px" />
            <i v-else @click="onToggle" ref="btn" class="pi pi-globe cursor-pointer text-white"
                style="font-size:18px" />
        </div>


        <OverlayPanel ref="op">
            <div class="flex flex-column gap-3 w-25rem">
                <ComPendingSyncDataStatus />  
                <div class="flex gap-2">
                    <Chip class="cursor-pointer" :label="d" v-for="d in options" :class="{ 'active-tab text-white': d == selectedOption }"
                        @click="onSelect(d)" />
                </div>

                <div v-if="selectedOption == 'Notification'">
                    <ComSynNotificationLogList :data="cmSyncLogData" />
                    <br/>
                    <Button v-if="cmSyncLogData?.length>0" class="border-none w-full" label="View all sync logs" @click="onViewAllSyncLog" />
                </div>
                <div v-else>
                  
                    <ComSynNotificationTaskList :data="cmTaskData" />
                    <Button v-if="cmTaskData?.length > 0" class="border-0 w-full" label="View all Tasks" @click="onViewAllTask" />
                </div>
            </div>

        </OverlayPanel>


    </div>
</template>
<script setup>
import { useApp } from "@/hooks/useApp.js"
import { onMounted, ref, onUnmounted, inject, nextTick } from "vue"


import OverlayPanel from 'primevue/overlaypanel';
import ComSynNotificationLogList from '@/views/channel_managers/channel_manager/components/ComSynNotificationLogList.vue';
import ComSynNotificationTaskList from '@/views/channel_managers/channel_manager/components/ComSynNotificationTaskList.vue';

import ComPendingSyncDataStatus from '@/views/channel_managers/components/ComPendingSyncDataStatus.vue';

import ProgressSpinner from 'primevue/progressspinner';
import { useRouter } from "vue-router";
const router = useRouter()

const options = ["Notification", "Channel Manager Task"]
const selectedOption = ref("Notification")
const op = ref();
const btn = ref();
const cmSyncLogData = ref()
const cmTaskData = ref()
const totalTaskCount = ref(0)
const hasPendingData = ref(false)




const { getCMInfo } = useApp()
const cmInfo = ref()
const isLoading = ref(false)
const socket = inject("$socket")


const onToggle = (event) => {
    op.value.toggle(event);
    
        getCMSyncLog();
        // checkPendingSyncData()
   
}

async function onSelect(d) {
    selectedOption.value = d
    if (d == "Channel Manager Task" && !cmTaskData.value) {
        await getCMTaskData()
    }

    if (d == "Notification" && !cmSyncLogData.value) {
        await getCMSyncLog()
    }

}



async function getCMSyncLog() {
    const res = await app.getDocList("Channel Manager Sync Log", {
        fields: ["name", "request_type", "status", "response_text", "creation"],
        filters: [["property", "=", window.property_name]],
        orderBy: {
            field: 'creation',
            order: 'desc',
        }
    })
    if (res.data) {
        cmSyncLogData.value = res.data
    }
}

async function getCMTaskData() {
    const res = await app.getDocList("ToDo", {
        fields: ["name", "status", "priority", "custom_subject", "description","modified"],
        filters: [["custom_property", "=", window.property_name], ["status", "=", "Open"]],
        orderBy: {
            field: 'modified',
            order: 'desc',
        }
    })
    if (res.data) {
        cmTaskData.value = res.data
    }
}

async function getCMTaskCount() {
    
    const res = await app.getCount("ToDo", [["custom_property", "=", window.property_name], ["status", "=", "Open"]])

    totalTaskCount.value = res;

}

function onViewAllSyncLog() {
    op.value.toggle(event);
    router.push({ name: "ChannelManagerSyncLog" })
}

async function onViewAllTask() {
    op.value.toggle(event);
    const result = await app.dialog.viewChannelManagerTaskList("Channel Manager Task List")
    if (result) {
        // to do
    }
}



function socketEvent(arg){
   
  
   
    if (arg.action=="update_cm_notification_status" && arg.property == window.property_name){
        
        isLoading.value = arg.status;
      
                
                if(!isLoading.value){
                    getCMTaskData();
                    setTimeout(() => {
                        getCMTaskCount();   
                    }, 3000);
                }
                
            }
     
}

onMounted(async () => {
    cmInfo.value = await getCMInfo()



    await getCMTaskCount();
 

    setTimeout(async () => {

        if (totalTaskCount.value > 0 || hasPendingData.value) {
            selectedOption.value = "Channel Manager Task";

            await nextTick();
            const target =
                btn.value?.$el || btn.value;


            if (target) {
                op.value.show({
                    currentTarget: target
                });
            }

            // get task data
            await getCMTaskData();
            

        }
    }, 2000)

  
    socket.on("ChannelManagerUpdate",  socketEvent)
})




onUnmounted(() => {

    socket.off("ChannelManagerUpdate",socketEvent)
})
 
</script> 
<style scoped>
.active-tab {
    background: linear-gradient(135deg, #6366f1, #4f46e5);
}
</style>