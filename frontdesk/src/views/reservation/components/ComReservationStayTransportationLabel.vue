<template lang="">
   
    <span v-tippy="(st.require_pickup && st.require_drop_off) ? $t('Guest Request Pickup') + ' & ' + $t('Drop Off') : ((st.require_pickup) ? $t('Guest Request Pickup') : ((st.require_drop_off) ? $t('Guest Request Drop Off') : ''))" v-if="st && (st.require_pickup || st.require_drop_off)" v-badge.warning="st.require_pickup + st.require_drop_off" class="bg-yellow-tran p-2 rounded-xl flex justify-center items-center w-2rem h-2rem p-overlay-badge cs-badge-tran">
        <i class="pi pi-car" style="font-size: 1rem"></i>
    </span>
</template>
<script setup>
import {inject,computed} from 'vue';
const rs = inject('$reservation_stay')
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const st = computed(()=>{
    if(rs){
        return rs.reservationStay;
    }
    return false
})
</script>
<style scoped>
    .bg-yellow-tran{
   background: #f2e1ca;
}
</style>