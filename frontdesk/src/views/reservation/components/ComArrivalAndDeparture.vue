<template>
  <div class="col-12" v-if="rs.reservationStay.require_pickup || rs.reservationStay.required_drop_off ">
    <ComReservationStayPanel title="Arrival & Departure Mode" >
      <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded />
      </template>
      <template #content>
        <div  class="mt-2 Arrival-bg">
          <TabView>
            <TabPanel  header="Arrival">
              <div class="flex mt-4 gap-2">
                <ComBoxStayInformation title="Arrival Mode" :value="rs.reservationStay?.arrival_mode" valueClass="col-7 " titleClass="grow">
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Flight No" :value="rs.reservationStay?.arrival_flight_number" valueClass="col-7 " titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Location" :value="rs.reservationStay?.pickup_location" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Require Pickup" :value="moment(rs.reservationStay?.pickup_time  ,'HH:mm:ss').format('h:mm a')" valueClass="col-7" titleClass="grow">
                  <Button icon="pi pi-check" class="border-none" aria-label="Filter" />
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Driver" :value="rs.reservationStay?.driver" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex flex-col mt-2 gap-2">
                <div>Note</div>
                <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                  {{ rs.reservationStay?.pickup_note }}
                </div>
              </div>
              
            </TabPanel>
            <TabPanel header="Departure">
              <div class="flex mt-4 gap-2">
                <ComBoxStayInformation title="Departure Mode" :value="rs.reservationStay?.departure_mode" valueClass="col-7 " titleClass="grow">
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Flight No" :value="rs.reservationStay?.departure_flight_number" valueClass="col-7 " titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Location" :value="rs.reservationStay?.drop_off_location" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Require Departure" :value="moment(rs.reservationStay?.drop_off_time,'HH:mm:ss').format('h:mm a')" valueClass="col-7" titleClass="grow">
                  <Button icon="pi pi-check" class="border-none" aria-label="Filter" />
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Driver" :value="rs.reservationStay?.drop_off_driver" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex flex-col mt-2 gap-2">
                <div>Note</div>
                <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                  {{ rs.reservationStay?.drop_off_note }}
                </div>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </template>
    </ComReservationStayPanel>
  </div>
  <div class="col" v-else>
  <div class="w-auto mt-4 ">
    <button class="w-full bg-orange-100 rounded-xl" @click="OnSetupForm">
      <div class="flex relative px-5  py-4">
        <span class="w-9rem" >
          <img class="icon-svg-setup-tran" src="../../../assets/svg/icon-transportation-mode.svg">
        </span>
        <span class="text-2xl">Setup Transportation</span>
      </div>
    </button>
  </div>
  </div>

</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();
import ComFormSetupArrivalAndDeparture from './ComFormSetupArrivalAndDeparture.vue';
import { inject } from 'vue'
const rs = inject('$reservation_stay');
const moment = inject('$moment')
const props = defineProps({
  reservationStay: {
    type: Object,
    default: {}
  }
})
function OnSetupForm() {
    dialog.open(ComFormSetupArrivalAndDeparture, {
        props: {
            header: 'Setup Arrival & Departure Mode',
            style: {
                width: '60vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
    });
}
</script>
<style scoped>
  .h-min-note{
    min-height: 8rem;
    max-height: 8rem;
  }
  .p-button-icon-only{
    height: 1.7rem;
    width: 1.7rem;
    margin: auto -3px;
    margin-right: 5px;
  }
  .Arrival-bg{
    line-height: 21px;
  }
  .icon-svg-setup-tran{
    height: 60px;
    position: absolute;
    top: -17px;
  }
</style>