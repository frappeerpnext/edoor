<template lang="">
     <ComReservationStayPanel title="Charge Summary">
      <template #content>
        <div class="flex gap-2">
            <div class="col p-2 bg-yellow-50 rounded-lg shadow-md border border-white">
                <div class="font-light" >Amount</div>
                <div class="font-bold" >{{data?.total_charge}}</div>
            </div>
            <div class="col p-2 bg-teal-50 rounded-lg shadow-md border border-white">
                <div class="font-light " >Paid</div>
                <div class="font-bold" >{{data?.total_payment}}</div>
            </div>
            <div class="col p-2 bg-green-50 rounded-lg shadow-md border border-white">
                <div class="font-light" >Balance</div>
                <div class="font-bold">${{data?.balance}}</div>
            </div>
        </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Room Charge" :value="data?.room_charge" valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Discount" :value="data?.room_discount" valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Total TAX" :value="data?.total_room_tax" valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Total Room Charge" :value="data?.total_charge" valueClass="col-6 bg-slate-400" titleClass="grow font-bold" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Extra Charge" :value="data?.extra_charge" valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Extra Charge TAX" :value="data?.extra_charge_tax" valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
          </div>
          <div class="flex mt-2">
              <ComBoxStayInformation title="Total" :value="data?.total_payment" valueClass="col-6 bg-slate-400" titleClass="grow font-bold" ></ComBoxStayInformation>
          </div>

      </template>
  </ComReservationStayPanel>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const props = defineProps({
  data: Object
})
</script>
<style lang="">
  
</style>