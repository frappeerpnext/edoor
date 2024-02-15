<template>
    <div class="mx-1">
        <Listbox :options="data" optionLabel="status" class="w-full h-full border-round-xl wrp-housekeeping"
            @change="onViewRoomList">
            <template #option="slotProps">
                <ComDashboardRowStatus
                    v-tippy="slotProps.option.is_block_room ? 'Today Room Block  ' + slotProps.option.total + ' & Total Room Block ' + slotProps.option.total_block_room : ''"
                    :is_room_block="slotProps.option.is_block_room" :value_room_block="slotProps.option.total_block_room"
                    :value="`${slotProps.option.total}`" :badgeColor="slotProps.option.color" :icon="slotProps.option.icon">
                    <template #content>{{ slotProps.option.status }}
                    </template>
                </ComDashboardRowStatus>
            </template>
        </Listbox>
    </div>
</template>
<script setup>
import { ref, getApi, onMounted, onUnmounted } from "@/plugin"
import { useDialog } from 'primevue/usedialog';
import ComDashboardRowStatus from '@/views/dashboard/components/ComDashboardRowStatus.vue';
import ComIFrameModal from "@/components/ComIFrameModal.vue";
const data = ref([])
const working_day = JSON.parse(localStorage.getItem('edoor_working_day'))
const dialog = useDialog();
const loading = ref(false)


function loadData(showLoading = true) {
    loading.value = showLoading
    getApi('frontdesk.get_house_keeping_status', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        working_day: working_day.date_working_day
    }).then((result) => {
        data.value = result.message
        loading.value = false
    }).catch(() => {
        loading.value = false
    })
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ComHousekeepingStatus"){
            setTimeout(()=>{
                loadData(false)
            },1000*2)
            
        }
    };
}

onMounted(() => {
    window.addEventListener('message', actionRefreshData, false)
    loadData()
})
const onViewRoomList = (status) => {
    if (status.value.is_block_room == 0) {
        const dialogRef = dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Business%20Branch",
                name: JSON.parse(localStorage.getItem("edoor_property")).name,
                // report_name: "eDoor%20Housekeeping%20Status",
                report_name: "eDoor%20Housekeeping%20Status",
                extra_params: [{ key: "housekeeping_status", value: encodeURIComponent(status.value.status) }],
                view: "ui",
                filter_options: ['keyword', 'building', 'floor', 'room_type']
            },
            props: {
                header: status.value.status,
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
            },
        });
    } else {
        const dialogRef = dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Business%20Branch",
                name: JSON.parse(localStorage.getItem("edoor_property")).name,
                report_name: "eDoor%20Room%20Block",//"eDoor%20Room%20Block",
                extra_params: [{ key: "housekeeping_status", value: encodeURIComponent(status.value.status) }, { key: "date", value: working_day.date_working_day }],
                view: "ui",
                filter_options: ['keyword']
            },
            props: {
                header: status.value.status,
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                pt: {
                root: `${window.isMobile ? 'p-dialog-maximized' : ''}`
            }
            },

        });
    }
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})

</script>