<template>
    <div> 
        <ComRoomRateToolBar />
        <ComRatePlanGridByRoomType :year="selectedYear" />
        <ComBottomAction :selectionCount="selectedDates.size" @update-rate="onBulkEdit()"
            @clear-selection="onClearSelection()" 
            @update-restriction="onCloseSale()"
            v-if="cm_info?.prices_for_accommodation == 'Receive from PMS' || !rateInfo?.cm_rate_plan_list?.cm_rate_plan"
            />
    </div>
</template>
<script setup>
import { useRoute, useDialog } from '@/plugin'

import ComRatePlanGridByRoomType from "@/views/channel_managers/rate_plans/components/ComRatePlanGridByRoomType.vue"
import ComBulkEditRatePlan from "@/views/channel_managers/rate_plans/components/ComBulkEditRatePlan.vue"
import ComRoomRateToolBar from "@/views/channel_managers/rate_plans/components/ComRoomRateToolBar.vue"
import ComBottomAction from "@/views/channel_managers/rate_plans/components/ComBottomAction.vue"
import ComBulkUpdateRestriction from "@/views/channel_managers/rate_plans/components/ComBulkUpdateRestriction.vue"
import { i18n } from '@/i18n';

import { useRatePlan } from "@/views/channel_managers/rate_plans/hooks/useRatePlan.js";

import { onMounted } from 'vue'

const route = useRoute();
const dialog = useDialog();

const {
    reloadRoomRatesData,
    components,
    selectedYear,
    selectedDates,
    reloadRestrictionData,
    cm_info,
    rateInfo
} = useRatePlan();

 


const { t: $t } = i18n.global;


function onBulkEdit() {

    dialog.open(ComBulkEditRatePlan, {
        data: {
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
            if (data) {
                reloadRoomRatesData()
            }
        }
    });
}


async function onCloseSale(){
    
    const result = await app.utils.openDialog(ComBulkUpdateRestriction,"Update Restriction - Close Sale",
        {
            data:{
                rate_type: route.params.name,
                restriction_type:"Closed"
            }
        }
    );
    
    if (result){
        await reloadRestrictionData('Closed')
    }


}

function onClearSelection() {
    selectedDates.value = new Set();
}

onMounted(async () => {
    const component = components.value.find(x => x.component == "ComRoomRate")
    if (!component.is_loaded) {
        // load specific component
        await reloadRoomRatesData()

        component.is_loaded = true;
    }

})

</script>