<template lang="">
    <div class="h-full">
        <ComReservationStayPanel title="Charge Summary" style="height:100%">
            <template #content>
                <div class="flex mb-2 mt-2 gap-2">
                    <div class="col-4 p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                        <div class="text-500 uppercase text-sm">Total Debit</div>
                        <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservation?.total_debit"></CurrencyFormat></div>
                    </div>
                    <div class="grow p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100 h-full">
                        <div class="text-500 uppercase text-sm">Total Credit</div>
                        <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservation?.total_credit"></CurrencyFormat></div>
                    </div>
                    <div class="grow p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                        <div class="text-500 uppercase text-sm">Balance</div>
                        <div class="text-xl line-height-2 font-semibold"><CurrencyFormat :value="rs?.reservation?.balance"></CurrencyFormat></div>
                    </div>
                </div>
                <div class="mt-3">
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation  isCurrency title="Room Rate" :value="rs?.reservation?.room_rate" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                    </div>
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation  isCurrency title="Room Rate Discount" :value="rs?.reservation?.room_rate_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                    </div>
                    <div class="flex mt-2 gap-2 relative">
                       
                        <ComBoxStayInformation  isCurrency title="Total Room Rate Tax" :value="rs?.reservation?.total_room_rate_tax" valueClass="col-6 text-right" titleClass="grow" >
                        <Button v-if="rs?.reservation?.room_rate_tax_1_amount || rs?.reservation?.room_rate_tax_2_amount || rs?.reservation?.room_rate_tax_3_amount" @click="toggleTAX"  icon="pi pi-question text-xs " class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined aria-label="Total Tax" />
                        </ComBoxStayInformation>
                        <OverlayPanel ref="opTax">
                        <div class="table-order-tax">
                        <table>
                                <tr v-if="rs?.reservation?.room_rate_tax_1_amount" ><td class='p-2'>Tax-1 : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservation?.room_rate_tax_1_amount"/> </td></tr>
                                <tr v-if="rs?.reservation?.room_rate_tax_2_amount" class='border-top-1 '><td class='p-2'>Tax-2 : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservation?.room_rate_tax_2_amount"/> </td></tr>
                                <tr v-if="rs?.reservation?.room_rate_tax_3_amount" class='border-top-1 '><td class='p-2'>Tax-3 : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservation?.room_rate_tax_3_amount"/> </td></tr>
                        </table>    
                        </div>
                        </OverlayPanel>
                    </div>
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation isCurrency title="ADR" titleTooltip="Average Daily Rate" :value="rs?.reservation?.adr" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                    </div>
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation isCurrency title="Total Room Rate" :value="rs?.reservation?.total_room_rate" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                    </div>
                </div>
                <div v-for="items in rs.stay_summary" :key="items" class="flex gap-2 mt-2">
                    <ComBoxStayInformation isCurrency v-if="items.amount > 0" :title="items?.label" :value="items?.amount"  valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
            </template>
        </ComReservationStayPanel>
    </div>
</template>
<script setup>
import { inject } from '@/plugin';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const emit = defineEmits('onViewReservation')
const rs = inject('$reservation');
import { ref } from "vue";

const opTax = ref();
const toggleTAX = (event) => {
    opTax.value.toggle(event);
}

function onClick(){
emit('onViewReservation')
}
</script>
<style scoped>

</style>