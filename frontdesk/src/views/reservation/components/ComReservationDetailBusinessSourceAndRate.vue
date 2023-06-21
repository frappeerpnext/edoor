<template>
    <ComReservationStayPanel title="Business Source & Rate">
        <template #content>
        <div class="flex">
            <div class="flex mt-2 w-full ">
                <div class="col-6">
                    <div class="grid">
                        <div class="col-fixed pl-0 w-10rem">Business Sources</div>
                        <div class="grow py-2 px-3 bg-white border-round-lg">
                            <div class="flex justify-content-between align-items-center"> 
                                <span class="link_line_action" @click="onOpenChangeBusinessSource">{{ rs?.reservation?.business_source }}</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="col-6">
                    <div class="grid">
                        <div class="col-fixed w-10rem text-right">Rate Type</div>
                        <div class="grow py-2 px-3 bg-white border-round-lg">
                            <div class="flex justify-content-between align-items-center">
                                <span class="link_line_action" @click="onOpenChangeRateType">{{ rs?.reservation?.rate_type }}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </template>
    </ComReservationStayPanel>
    <OverlayPanel ref="opBusinessSource">
        <ComChangeBusinessSource :reservation="rs?.reservation?.name" :businessSource="rs?.reservation?.business_source" @onClose="closeOverlay" @onSave="onChangeBusinessSource"/>
    </OverlayPanel>

    <OverlayPanel ref="opRateType">
        <ComChangeRateType :reservation="rs?.reservation?.name" :rate_type="rs?.reservation?.rate_type" @onClose="closeOverlay" @onSave="onChangeRateType"/>
    </OverlayPanel>

    </template>
    <script setup>
    import {inject, ref} from "@/plugin"
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComBoxStayInformation from './ComBoxStayInformation.vue';
    import ComChangeBusinessSource from "./ComChangeBusinessSource.vue";
    import ComChangeRateType from "./ComChangeRateType.vue";
    const rs = inject("$reservation")

    const opBusinessSource = ref();
    const opRateType = ref();

    const onOpenChangeBusinessSource = (event) => {
        opBusinessSource.value.toggle(event);
    }
    const onOpenChangeRateType = (event) => {
        console.log(event)
        opRateType.value.toggle(event);
    }

    const closeOverlay = () => {
        opBusinessSource.value.hide();
        opRateType.value.hide();
    }
    const onChangeBusinessSource = (doc) => {
        rs.reservation = doc
        rs.reservation.business_source = doc.business_source

        opBusinessSource.value.hide();
    }

    const onChangeRateType = (doc) => {
        rs.reservation = doc
        opRateType.value.hide();
    }
    </script>