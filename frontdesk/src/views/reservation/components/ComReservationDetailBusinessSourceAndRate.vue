<template>
    <ComReservationStayPanel title="Business Source & Rate">
        <template #content>
        <div class="grid">
                <div class="col-12">
                    <div class="">Business Sources</div>
                    <div class="grow py-2 px-3 bg-white border-round-lg">
                        <div class="flex justify-content-between align-items-center"> 
                            <span class="link_line_action" @click="onOpenChangeBusinessSource">{{ rs?.reservation?.business_source }}</span>
                        </div>
                    </div>
                </div>
                <div class="col-12">
                    <div class="">Rate Type</div>
                    <div class="py-2 px-3 bg-white border-round-lg">
                        <div class="flex justify-content-between align-items-center">
                            <span class="link_line_action" @click="onOpenChangeRateType">{{ rs?.reservation?.rate_type }}</span>
                        </div>
                    </div> 
                    <Message v-if="isMultipleStayRate > 1" severity="info" :closable="false">
                        <p>This reservation has deference reservation stay's rate types.</p>
                        <p><b>Note:</b> if you change this. It will override all reservation stays.</p>
                    </Message>
                </div>
        </div>
    </template>
    </ComReservationStayPanel>
    <OverlayPanel ref="opBusinessSource">
        <ComChangeBusinessSource :reservation="rs?.reservation?.name" :businessSource="rs?.reservation?.business_source" @onClose="closeOverlay" @onSave="onChangeBusinessSource"/>
    </OverlayPanel>

    <OverlayPanel ref="opRateType">
        <ComChangeRateType hideApplyAll :reservation="rs?.reservation?.name" :rate_type="rs?.reservation?.rate_type" @onClose="closeOverlay" @onSave="onChangeRateType"/>
    </OverlayPanel>

    </template>
    <script setup>
    import {inject, ref,computed} from "@/plugin"
    import Enumerable from 'linq'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComChangeBusinessSource from "./ComChangeBusinessSource.vue";
    import ComChangeRateType from "./ComChangeRateType.vue";
    
    const rs = inject("$reservation")
    const opBusinessSource = ref();
    const opRateType = ref();
    const isMultipleStayRate = computed(()=>{
        // return Enumerable.from(rs.reservationStays).group(`$.rate_type != '${rs.reservation.rate_type}' && $.is_active_reservation==1`).count()
        return Enumerable.from(rs.reservationStays).where(`$.is_active_reservation==1`).groupBy(
        "{rate_type:$.rate_type}",
        "{is_active_reservation:$.is_active_reservation}",
        "{rate_type:$.rate_type,is_active_reservation: $$.sum('$.is_active_reservation')}",
        "$.rate_type+','+$.is_active_reservation"
        ).count()
    })
    const onOpenChangeBusinessSource = (event) => {
        opBusinessSource.value.toggle(event);
    }
    const onOpenChangeRateType = (event) => {
        opRateType.value.toggle(event);
    }

    const closeOverlay = () => {
        opBusinessSource.value.hide();
        opRateType.value.hide();
    }
    const onChangeBusinessSource = (doc) => {
        // rs.reservation = doc
        alert(window.reservation_stay)
        // window.socket.emit("ReservationStayDetail", { reservation_stay: rs.reservationStays.name })
        
        opBusinessSource.value.hide();
    }

    const onChangeRateType = (doc) => {
        if(doc){
            rs.LoadReservation(rs.reservation.name)
            opRateType.value.hide();
            window.socket.emit("ReservationDetail", window.reservation)
        }
            
    }
    </script>