<template lang="">
    <div class="h-full">
        <ComReservationStayPanel title="Charge Summary" style="height:100%">
            <template #content>
                <div class="flex mb-2 mt-2 gap-2">
                    <div class="grow p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100 h-full">
                        <div class="text-500 uppercase text-sm">Amount</div>
                        <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservation?.total_charge"></CurrencyFormat></div>
                    </div>
                    <div class="col-4 p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                        <div class="text-500 uppercase text-sm">Paid</div>
                        <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservation?.total_payment"></CurrencyFormat></div>
                    </div>
                    <div class="grow p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                        <div class="text-500 uppercase text-sm">Balance</div>
                        <div class="text-xl line-height-2 font-semibold"><CurrencyFormat :value="rs?.reservation?.balance"></CurrencyFormat></div>
                    </div>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Room Charge" :value="rs?.reservation?.room_charge"  valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Discount" :value="rs?.reservation?.room_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Total TAX" :value="rs?.reservation?.total_room_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Total Room Charge" :value="rs?.reservation?.total_charge" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Extra Charge" :value="rs?.reservation?.extra_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Extra Charge TAX" :value="rs?.reservation?.extra_charge_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Total" :value="rs?.reservation?.total_payment" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold" ></ComBoxStayInformation>
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


function onClick(){
emit('onViewReservation')
}
</script>
<style scoped>

</style>