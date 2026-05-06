<template>
    <div class="header" id="sticky_filter">
        <div class="flex justify-content-between ">

            <div class="flex gap-3">
                <ComSelectYear />
                <ComSelect v-model="selectedRoomType" :clear="false" @onSelected="onChangeRoomType"
                    :placeholder="$t('All Room Types')" :options="roomTypes" optionLabel="room_type_name"
                    optionValue="edoor_room_type" />
            </div>
            <div>
                <Button class="border-0" label="Resync Room Rate" @click="RoomRateResyncDialog" 
                  v-if="cm_info?.prices_for_accommodation == 'Receive from PMS'"
                />
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
import RoomRateResync from '@/views/channel_managers/rate_plans/components/RoomRateResync.vue';
import { onMounted, ref } from 'vue';
const route = useRoute();
const selectedRoomType = ref()
const { roomTypes, reloadRoomRatesData,cm_info } = useRatePlan()

const { t: $t } = i18n.global;
function onOpenRoomRateDialog() {
    dialog.open(ComRateSummary, {
        props: {
            header: $t('Rate Summary'),
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

function RoomRateResyncDialog() {
    dialog.open(RoomRateResync, {
        data: {
            rate_type: route.params.name,
        },
        props: {
            header: $t('Resync Room Rate'),
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

async function onChangeRoomType() {
    roomTypes.value.find(x => x.selected).selected = false
    roomTypes.value.find(x => x.edoor_room_type == selectedRoomType.value).selected = true

    await reloadRoomRatesData()

}

onMounted(() => {
    selectedRoomType.value = roomTypes.value.find(x => x.selected)?.edoor_room_type
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