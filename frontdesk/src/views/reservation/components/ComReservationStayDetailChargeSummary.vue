<template lang="">
    <div class="grid">
        <div class="col-12">
    <ComReservationStayPanel title="Charge Summary">
      <template #content>
        <div class="flex mb-2 mt-2 gap-2">
            <div class="grow p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div>Amount</div>
                <div class="text-xl line-height-2 font-semibold" >{{data?.total_charge}}</div>
            </div>
            <div class="col-4 p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                <div>Paid</div>
                <div class="text-xl line-height-2 font-semibold" >{{data?.total_payment}}</div>
            </div>
            <div class="grow p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                <div>Balance</div>
                <div class="text-xl line-height-2 font-semibold">{{data?.balance}}</div>
            </div>
        </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Room Charge" :value="data?.room_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Discount" :value="data?.room_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Total TAX" :value="data?.total_room_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Total Room Charge" :value="data?.total_charge" valueClass="col-6 text-right bg-gray-edoor-10" titleClass="grow font-bold" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Extra Charge" :value="data?.extra_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Extra Charge TAX" :value="data?.extra_charge_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Total" :value="data?.total_payment" valueClass="col-6 text-right bg-gray-edoor-10" titleClass="grow font-bold" ></ComBoxStayInformation>
          </div>
    
      </template>
    </ComReservationStayPanel>
    </div>
    <div class="col-12">
    <ComReservationStayPanel title="Charge Summary">
        <template #content>
            <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Room Charge" :value="data?.room_charge" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Discount" :value="data?.room_discount" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Total TAX" :value="data?.total_room_tax" valueClass="col-6 text-right" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Total Room Charge" :value="data?.total_charge" valueClass="col-6 text-right bg-gray-edoor-10" titleClass="grow font-bold" ></ComBoxStayInformation>
          </div>
          <div class="text-right w-full mt-2">This room charge paid by</div>
          <div class="text-right w-full color-purple-edoor text-lg"><span>{{ data?.guest_name }}</span> Room {{data?.rooms}} </div>
        </template>
    </ComReservationStayPanel>
    </div>
</div>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const props = defineProps({
  data: Object
})
</script>
<style scoped>
.shadow-charge-total{
    box-shadow: rgba(0, 0, 0, 0.1) 0px 1px 2px 0px;
}
</style>