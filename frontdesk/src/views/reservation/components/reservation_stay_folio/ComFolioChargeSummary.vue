<template>
     
    <div v-for="items in rs.stay_summary" :key="items" class="flex gap-2 mt-2">
        <ComBoxStayInformation isCurrency v-if="items.amount != 0" :title="items?.account_category" :value="items?.amount"  valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
    </div>

</template>
<script setup>
import { inject } from '@/plugin';
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
</script>