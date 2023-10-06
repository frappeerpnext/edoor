<template lang="">
    <span v-tooltip.top="(st.require_pickup && st.require_drop_off) ? 'Guest Request Pickup & Drop Off' : ((st.require_pickup) ? 'Guest Request Pickup' : ((st.require_drop_off) ? 'Guest Request Drop Off' : ''))" v-if="st && (st.require_pickup || st.require_drop_off)" v-badge.warning="st.require_pickup + st.require_drop_off" class="bg-yellow-tran p-2 rounded-xl flex justify-center items-center w-2rem h-2rem p-overlay-badge cs-badge-tran">
        <i class="pi pi-car" style="font-size: 1rem"></i>
    </span>
</template>
<script setup>
import {inject,computed} from 'vue';
const rs = inject('$reservation')
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