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
                <Button class="border-0" label="Rate Summary" @click="onOpenRoomRateDialog" />

            </div>
        </div>
    </div>
</template>
<script setup>
import { useRoute, useDialog } from '@/plugin'
const dialog = useDialog();
import { i18n } from '@/i18n';
import ComSelectYear from "@/views/channel_managers/rate_plans/components/ComSelectYear.vue"
import { useRatePlan } from "../hooks/useRatePlan";
import ComRateSummary from '@/views/channel_managers/rate_plans/components/ComRateSummary.vue';
import { onMounted, ref, watch } from 'vue';

const selectedRoomType = ref()

const {
    roomTypes,
    reloadRestrictionData,
    restrictionTypes,
    selectedRestrictionTypes,
    restrictionData
} = useRatePlan()




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