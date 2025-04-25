<template>
    <div>
 
        <Button class="border-none" icon="pi pi-chevron-down" iconPos="right" type="button" :label="$t('Mores')" @click="toggle"
            aria-haspopup="true" aria-controls="folio_menu" />
        <Menu ref="folio_menu" id="folio_menu" :popup="true">
            <template #end>
                <ComReservationStayMoreOptions @onDupicateReservation="onDupicateReservation" @onAuditTrail="onAuditTrail" @onRefresh="onRefresh"/>
            </template>
        </Menu>
    </div>
   
</template>
<script setup>
import { ref } from "@/plugin";
import ComReservationStayMoreOptions from "@/views/reservation/components/ComReservationStayMoreOptions.vue"; 
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
 
const emit = defineEmits(['onAuditTrail', "onRefresh","onDupicateReservation"]) 
const folio_menu = ref(); 

  

const toggle = (event) => {
    folio_menu.value.toggle(event);
}

const onAuditTrail = () => {
    emit("onAuditTrail")
}

const onDupicateReservation = () => {
    emit("onDupicateReservation")
}

const onRefresh = () => {
    emit("onRefresh")
}

 
 
 
</script>