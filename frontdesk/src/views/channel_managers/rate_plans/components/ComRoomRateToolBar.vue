<template>
<ComSelectYear />

<ComSelect :options="roomTypes" optionLabel="room_type_name" optionValue="edoor_room_type" />

<Button  label="Rate Summary" @click="onOpenRoomRateDialog"/>
<Button  label="Close/Open sales" @click="onOpenCloseSalesDialog"/>
</template>
    <script setup>
    import { useRoute, useDialog} from '@/plugin'
    const dialog = useDialog();
    import { i18n } from '@/i18n';
    import ComSelectYear  from "@/views/channel_managers/rate_plans/components/ComSelectYear.vue"
    import { useRatePlan } from "../hooks/useRatePlan";
    import ComRateSummary from '@/views/channel_managers/rate_plans/components/ComRateSummary.vue';
    import ComCloseOpenSale from '@/views/channel_managers/rate_plans/components/ComCloseOpenSale.vue';
    const {roomTypes,roomRatesData,ratePlan,occupancyCodes}  = useRatePlan()
    const { t: $t } = i18n.global;
    function onOpenRoomRateDialog(){
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
    function onOpenCloseSalesDialog(){
    dialog.open(ComCloseOpenSale, {
            props: {
                header: $t('Close/Open Sales'),
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
        });
    }
</script>