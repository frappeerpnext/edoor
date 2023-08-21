<template lang="">
        <div class="col-12">
    <ComReservationStayPanel title="Charge Summary">
      <template #content>
        <div class="flex mb-2 mt-2 gap-2 text-right">
            <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div class="text-500 uppercase text-sm">Total Debit</div>
                <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservationStay?.total_debit"></CurrencyFormat></div>
            </div>
            <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div class=" text-500 uppercase text-sm">Total Credit</div>
                <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservationStay?.total_credit"></CurrencyFormat></div>
            </div>
            <div class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                <div class="text-500 uppercase text-sm">Balance</div>
                <div class="text-xl line-height-2 font-semibold"><CurrencyFormat :value="rs?.reservationStay?.balance"></CurrencyFormat></div>
            </div>
        </div>
         
          <div v-for="items in rs.stay_summary" :key="items" class="flex gap-2 mt-2">
              <ComBoxStayInformation isCurrency v-if="items.amount != 0" :title="items?.account_category" :value="items?.amount"  valueClass="grow text-right" titleClass="col-5" ></ComBoxStayInformation>
          </div>
      </template>
    </ComReservationStayPanel>
     
    </div>
    <div class="col-12">
    <ComReservationStayPanel title="Room Rate Summary">
        
        <template #content>
            <div class="flex gap-2 mt-2">
              <ComBoxStayInformation titleTooltip="Average Daily Rate" isCurrency title="ADR" titleClass="col-4" :value="rs?.reservationStay?.adr" valueClass="grow text-right" >
              </ComBoxStayInformation>
              <span class="m-auto col-1 text-center text-xl p-0"><i class="pi pi-times"></i></span>
              <ComBoxStayInformation  :value="rs?.reservationStay?.room_nights" valueClass="col-2 surface-800 text-white text-center line-height-1 border-none" >
                <span class="text-xs block font-light">Nights</span>
              </ComBoxStayInformation>
            </div>
            <!-- <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Before Tax" :value="rs?.reservationStay?.room_rate_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
            </div>  -->
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Discount" :value="rs?.reservationStay?.room_rate_discount" valueClass="grow text-right" titleClass="col-4" >
              </ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total TAX" :value="rs?.reservationStay?.total_room_rate_tax" valueClass="grow text-right" titleClass="col-4" >
                <Button v-if="rs?.reservationStay?.room_rate_tax_1_amount || rs?.reservationStay?.room_rate_tax_2_amount || rs?.reservationStay?.room_rate_tax_3_amount" @click="toggleTAX"  icon="pi pi-question text-xs " class="float-left -ms-1 surface-border tax-info-btn" severity="secondary" rounded outlined aria-label="Total Tax" />
              </ComBoxStayInformation>
              <OverlayPanel ref="opTax">
                <div class="table-order-tax">
                <table>
                        <tr v-if="rs?.reservationStay?.room_rate_tax_1_amount" ><td class='p-2 text-right'> {{rs?.reservationStay?.tax_1_name}} - {{rs?.reservationStay?.tax_1_rate}} % : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservationStay?.room_rate_tax_1_amount"/> </td></tr>
                        <tr v-if="rs?.reservationStay?.room_rate_tax_2_amount" class='border-top-1 '><td class='p-2 text-right'>{{rs?.reservationStay?.tax_2_name}} - {{rs?.reservationStay?.tax_2_rate}} % : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservationStay?.room_rate_tax_2_amount"/> </td></tr>
                        <tr v-if="rs?.reservationStay?.room_rate_tax_3_amount" class='border-top-1 '><td class='p-2 text-right'>{{rs?.reservationStay?.tax_3_name}} - {{rs?.reservationStay?.tax_3_rate}} % : </td><td class='p-2'> <CurrencyFormat :value="rs?.reservationStay?.room_rate_tax_3_amount"/> </td></tr>
                </table>    
                </div>
                </OverlayPanel>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation isCurrency title="Total Room Rate" :value="rs?.reservationStay?.total_room_rate" valueClass="grow text-right bg-gray-edoor-10 font-semibold" titleClass="col-4 font-semibold" >

              </ComBoxStayInformation>
          </div>
          <div v-if="!(rs?.reservationStay?.is_master) && rs?.reservationStay?.pay_by_company">
            <div @click="onClick" class="cursor-pointer px-4 mt-3 py-2 bg-indigo-100 rounded-r-lg border-l-4 border-indigo-500 text-indigo-500"> Room Charge Paid by Master Room </div>
          </div>
        </template>
    </ComReservationStayPanel>
    </div>
</template>
<script setup>
import { ref, inject , computed } from '@/plugin';
import Message from 'primevue/message';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const emit = defineEmits('onViewReservation')
const rs = inject('$reservation_stay');
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