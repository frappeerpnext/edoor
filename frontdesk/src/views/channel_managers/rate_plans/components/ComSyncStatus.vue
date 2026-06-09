<template>
    <div v-if="data?.request_type">
        <Message severity="warn">
            <h1 class="text-xl">{{ title }}</h1>
            <div v-html="data?.response_text"></div>
            <div>
                {{ data?.sync_action }} at: {{ moment(data?.creation).format("DD-MM-YYYY hh:mm A") }}
            </div>
            <div class="flex gap-2 mt-4">
                <Button severity="secondary" @click="onViewSyncData">View Sync Data</Button>
                <Button severity="secondary" @click="onViewSyncStatus">View Sync Status</Button>
                <Button @click="onRestartResync">Resync Data</Button>
            </div>
        </Message>
    </div>
</template>
<script setup>

import { computed, inject, onMounted, onUnmounted, ref } from "vue";
import { useDialog } from 'primevue/usedialog';
import ComRestartSyncDataConfirmation from "@/views/channel_managers/rate_plans/components/ComRestartSyncDataConfirmation.vue"
import ComChannelManagerSyncStatus from "@/views/channel_managers/components/ComChannelManagerSyncStatus.vue"
import ComViewSyncData from "@/views/channel_managers/components/ComViewSyncData.vue"
import { i18n } from '@/i18n';

const props = defineProps({
    method: String
})
const moment = inject("$moment")
const dialog = useDialog();

const { t: $t } = i18n.global;

const data = ref({})
const property = JSON.parse(localStorage.getItem("edoor_property"))


const title = computed(() => {
    let _title = `Sync ${data.value?.request_type} to  ${data.value?.provider} has been Stoped`;
    if (data.value?.sync_action == "Delay Sync") {
        _title = `Sync ${data.value?.request_type} to ${data.value?.provider} has been Delay`;
    }
    return _title
})

async function onViewSyncStatus() {
    await app.utils.openDialog(ComChannelManagerSyncStatus, "Channel Manager Sync Status")
}
async function onViewSyncData() {
    const result = await app.utils.openDialog(ComViewSyncData, "Sync Data", {
        data: {
            docname: data.value.name
        }
    })

    if (result) {
        if (result.retry_sync) {
            onRestartResync()
        }
    }
}


function onRestartResync() {

    dialog.open(ComRestartSyncDataConfirmation, {
        data: {
            data: data.value
        },
        props: {
            header: $t('Restart Sync Data'),
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            closeOnEscape: true,
            position: "top",

        },
        onClose: (options) => {

        }
    });
}

async function getSyncRoomRateActionStatus() {

    const resp = await app.postApi("edoor.channel_managers.utils.get_sync_action_status", {
        request_type: props.method,
        property: property.name
    }, "", false)
    if (resp.data) {
        data.value = resp.data


    }
}

function socketEvent(arg) {

    if (arg.action == "update_sync_rate_plan_status" && arg.property == window.property_name) {
        setTimeout(function () {
            getSyncRoomRateActionStatus()
        }, 1000)

    }

}

onMounted(() => {
    getSyncRoomRateActionStatus()

    window.socket.on("ChannelManagerUpdate", socketEvent)

})

onUnmounted(() => {
    window.socket.off("ChannelManagerUpdate", socketEvent)
})

</script>