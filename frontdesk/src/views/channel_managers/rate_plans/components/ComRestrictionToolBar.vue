<template>
    <div id="sticky_filter">
        <div class="flex justify-content-between">

            <div class="flex gap-3">
                <ComSelectYear />
                <ComSelect v-model="selectedRoomType" :clear="false" @onSelected="onChangeRoomType"
                    :placeholder="$t('All Room Types')" :options="roomTypes" optionLabel="room_type_name"
                    optionValue="edoor_room_type" />
                <ComSelect v-model="selectedRestrictionTypes" :clear="false" @onSelected="onSelectRestrictionType"
                    :placeholder="$t('Restriction Types')" :options="restrictionTypes" optionLabel="restriction_type"
                    optionValue="restriction_type" isMultipleSelect />
            </div>
            <div>
                <Button class="border-0" label="Restriction ReSync"
                 @click="onOpenRestrictionSyncDailog" 
                 v-if="cm_info?.restrictions == 'Receive from PMS'"
                 :restriction = 'selectedRestrictionTypes'
                 />
                <Button class="border-0" label="Restriction Summary" @click="onOpenRoomRateDialog" />
            </div>
        </div>
    </div>
</template>
<script setup>
import { useRoute, useDialog,computed } from '@/plugin'
const dialog = useDialog();
import { i18n } from '@/i18n';
const route = useRoute();
import ComSelectYear from "@/views/channel_managers/rate_plans/components/ComSelectYear.vue"
import { useRatePlan } from "../hooks/useRatePlan";
import ComRestrictionSummary     from '@/views/channel_managers/rate_plans/components/ComRestrictionSummary.vue';
import { onMounted, ref, watch } from 'vue';
import ComRestrictionSync from './ComRestrictionSync.vue';

import ComBulkUpdateRestriction from '@/views/channel_managers/rate_plans/components/ComBulkUpdateRestriction.vue'; 
const selectedRoomType = ref()

const {
    roomTypes,
    cm_info,
    reloadRestrictionData,
    restrictionTypes,
    selectedRestrictionTypes,
    restrictionData
} = useRatePlan()

function onOpenRoomRateDialog() {
    dialog.open(ComRestrictionSummary, {
        props: {
            header: $t('Restriction Summary'),
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            closeOnEscape: false,
            position: "top",

        },
    });
}


const { t: $t } = i18n.global;

// we watch value add to selected ristrictype we only reload data only new added selected restriction 
// if it not load data yet

watch(
    selectedRestrictionTypes,
    async (newVal, oldVal) => {

        const added = newVal.filter(
            v => !oldVal.includes(v)
        );

        if (added.length) {
            let new_values = []
            added.forEach(key => {
                if (!(key in restrictionData.value)) {
                    new_values.push(key)
                }
            })
            console.log("added", added, "new key", new_values)
            if (new_values.length > 0) {
                await reloadRestrictionData(new_values);
            }

        }
    },
    { deep: true }
);

let lastValidSelection = [...selectedRestrictionTypes.value]

function onSelectRestrictionType(value) {
    if (value.length == 0) {
        selectedRestrictionTypes.value = ["Closed"]
    }



}



async function onChangeRoomType() {
    roomTypes.value.find(x => x.selected).selected = false
    roomTypes.value.find(x => x.edoor_room_type == selectedRoomType.value).selected = true

    await reloadRestrictionData()

}

onMounted(() => {
    selectedRoomType.value = roomTypes.value.find(x => x.selected).edoor_room_type
    document.body.addEventListener('scroll', handleScroll);
})


const handleScroll = () => {
    const sf = document.getElementById('sticky_filter')
    if (document.body.scrollTop > 50) {
        sf.classList.add("sicky_bar_top");
    } else {
        sf.classList.remove("sicky_bar_top");
    }

};

function onOpenRestrictionSyncDailog() {
    dialog.open(ComRestrictionSync, {
        data: {
            rate_type: route.params.name,
        },
        props: {
            header: $t('Restriction ReSync'),
            style: {
                width: '80vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            closeOnEscape: false,
            position: "top",
        },
    });
}




</script>
<style scoped>
#sticky_filter {
    position: -webkit-sticky;
    position: sticky;
    top: 62px;
    z-index: 4;
}

.sicky_bar_top {
    background-color: #eff2f7;
    padding: 10px 0;
}
</style>