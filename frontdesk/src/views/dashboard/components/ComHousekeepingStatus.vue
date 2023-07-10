<template>
    <div class="mx-1">
        <Listbox :options="data" optionLabel="status" class="w-full h-full border-round-xl" @change="onViewRoomList">
            <template #option="slotProps">
                <ComDashboardRowStatus :value="slotProps.option.total" :badgeColor="slotProps.option.color"
                    :icon="slotProps.option.icon">
                    <template #content>{{ slotProps.option.status }}
                    </template>
                </ComDashboardRowStatus>
            </template>
        </Listbox>
    </div>
</template>
<script setup>

import { inject, ref } from "@/plugin"
import { useDialog } from 'primevue/usedialog';
import ComDashboardRowStatus from '@/views/dashboard/components/ComDashboardRowStatus.vue';
import ComIFrameModal from "../../../components/ComIFrameModal.vue";

const frappe = inject("$frappe")
const call = frappe.call()
const data = ref([])

const dialog = useDialog();

call.get('edoor.api.frontdesk.get_house_keeping_status', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name
}).then((result) => {
    data.value = result.message
})

const onViewRoomList = (status) => {

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: "eDoor%20Housekeeping%20Status",
            extra_params: [{ key: "status", value: encodeURIComponent(status.value.status) }],
            view:"ui"
        },
        props: {
            header: status.value.status,
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        },
        
    });
}

</script>