<template lang="">
        <div class="col-12">
    <ComReservationStayPanel title="Charge Summary">
      <template #content>
        <div class="flex mb-2 mt-2 gap-2">
            <div class="grow p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div>Amount</div>
                <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservationStay?.total_charge"></CurrencyFormat></div>
            </div>
            <div class="col-4 p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div>Paid</div>
                <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservationStay?.total_payment"></CurrencyFormat></div>
            </div>
            <div class="grow p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                <div>Balance</div>
                <div class="text-xl line-height-2 font-semibold"><CurrencyFormat :value="rs?.reservationStay?.balance"></CurrencyFormat></div>
            </div>
        </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Room Charge" :value="rs?.reservationStay?.room_charge"  valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Discount" :value="rs?.reservationStay?.room_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total TAX" :value="rs?.reservationStay?.total_room_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total Room Charge" :value="rs?.reservationStay?.total_charge" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Extra Charge" :value="rs?.reservationStay?.extra_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Extra Charge TAX" :value="rs?.reservationStay?.extra_charge_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total" :value="rs?.reservationStay?.total_payment" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold" ></ComBoxStayInformation>
          </div>
    
      </template>
    </ComReservationStayPanel>
    </div>
    <div class="col-12">
    <ComReservationStayPanel title="Charge Summary">
        <template #content>
            <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Room Charge" :value="rs?.reservationStay?.room_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
            </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Discount" :value="rs?.reservationStay?.room_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total TAX" :value="rs?.reservationStay?.total_room_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total Room Charge" :value="rs?.reservationStay?.total_charge" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold" ></ComBoxStayInformation>
          </div>
          <div class="text-right w-full mt-2 font-italic">This room charge paid by</div>
          <div @click="onClick" class="text-right w-full color-purple-edoor text-md font-italic "><span  v-tooltip.top="rs?.stay?.master_guest?.customer_name_en.length > 20 ? rs?.stay?.master_guest?.customer_name_en : ''" class="link_line_action overflow-hidden text-overflow-ellipsis">{{ rs?.stay?.master_guest?.customer_name_en }}  </span></div>
        </template>
    </ComReservationStayPanel>
    </div>
</template>
<script setup>
import { inject } from '@/plugin';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const emit = defineEmits('onViewReservation')
const rs = inject('$reservation_stay');


function onClick(){
    emit('onViewReservation')
}
</script>
<style scoped>
.shadow-charge-total{
    box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 2px 0px;
}
</style>