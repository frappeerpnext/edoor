<template lang="">
<ComReservationStayPanel title="Business Source & Rate">
    <template #content>
    <div class="grid">
            <div class="col-12">
                    <div class="">Business Sources</div>
                    <div class="py-2 px-3 bg-white border-round-lg">
                        <div class="flex justify-content-between align-items-center">
                            <span class="link_line_action" @click="onOpenChangeBusinessSource">{{ rs?.reservationStay?.business_source }}</span>
                        </div>
                    </div>
            </div>
            <div class="col-12">
                    <div class="">Rate Type</div>
                    <div class="py-2 px-3 bg-white border-round-lg">
                        <div class="flex justify-content-between align-items-center">
                            <span class="link_line_action" @click="onOpenChangeRateType">{{ rs?.reservationStay?.rate_type }}</span>
                        </div>
                    </div>
            </div>
    </div>
    </template>
</ComReservationStayPanel>
<OverlayPanel ref="opBusinessSource">
    <ComChangeBusinessSource :reservation="rs?.reservation?.name" :reservation_stay="rs?.reservationStay?.name"  :businessSource="rs?.reservationStay?.business_source" @onClose="closeOverlay" @onSave="onChangeBusinessSource"/>
</OverlayPanel>

<OverlayPanel ref="opRateType">
    <ComChangeRateType :reservation="rs?.reservation?.name" :reservation_stay="rs?.reservationStay?.name" :rate_type="rs?.reservationStay?.rate_type" @onClose="closeOverlay"   @onSave="onChangeRateType"/>
</OverlayPanel>

</template>
<script setup>
import { inject, ref } from "@/plugin"
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComChangeBusinessSource from "./ComChangeBusinessSource.vue";
import ComChangeRateType from "./ComChangeRateType.vue";

const rs = inject("$reservation_stay")
const opBusinessSource = ref();
const opRateType = ref();

function onOpenChangeBusinessSource(event) {
    opBusinessSource.value.toggle(event);
}
function onOpenChangeRateType(event) {
    opRateType.value.toggle(event);
}
const closeOverlay = () => {
    opBusinessSource.value.hide();
    opRateType.value.hide();
}
function onChangeBusinessSource(result) {
    if(result.reservation_stay){
        rs.reservationStay = result.reservation_stay
    }
    
    if(result.reservation){
        rs.reservation = doc
        rs.reservationStay.business_source = doc.business_source   
    }
    window.socket.emit("RefreshData", { property: rs.reservationStay.property, action: "refresh_res_list" })
    opBusinessSource.value.hide();
}

function onChangeRateType(doc) { 
    rs.getReservationStay(rs.reservationStay.name)
    window.socket.emit("RefreshReservationDetail", rs.reservation.name);
    window.socket.emit("RefreshData", { action:"refresh_reservation_stay",reservation_stay:rs.reservationStay.name})
    window.socket.emit("RefreshData", { property: rs.reservationStay.property, action: "refresh_iframe_in_modal" });
    window.socket.emit("RefreshData", { property: rs.reservationStay.property, action: "refresh_res_list" })
    opRateType.value.hide();
}


</script>
<style scoped></style>