<template>
  <div class="col-12" v-if="rs.reservationStay.require_pickup || rs.reservationStay.require_drop_off">
    <ComReservationStayPanel title="Arrival & Departure Mode">
      <template #btn>
        <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" aria-haspopup="true"
          aria-controls="manu_arriaval_departure" text rounded @click="onMenuArriavalDeparture" />
        <Menu :model="items" ref="ManuArriavalDeparture" id="manu_arriaval_departure" :popup="true" />
      </template>
      <template #content>
        <div class="mt-2 Arrival-bg">
          <TabView :activeIndex="(rs.reservationStay.reservation_status == 'In-House' ? 1 : 0)">
            <TabPanel header="Arrival">
              <div v-if="rs.reservationStay.require_pickup" class="">
                <div class="flex mt-4 gap-2">
                  <ComBoxStayInformation title="Arrival Mode" :value="rs.reservationStay?.arrival_mode"
                    valueClass="col-7 " titleClass="col">
                  </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Flight No" :value="rs.reservationStay?.arrival_flight_number"
                    valueClass="col-7 " titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Location" :value="rs.reservationStay?.pickup_location" valueClass="col-7"
                    titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Pickup Time"
                    :value="moment(rs.reservationStay?.pickup_time, 'HH:mm:ss').format('h:mm a')" valueClass="col-7"
                    titleClass="col">
                  </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">                 
                  <ComBoxStayInformation @onClick="onEditDriver(rs.reservationStay?.pickup_driver)" title="Driver"
                    isAction="true" :value="rs.reservationStay?.pickup_driver_name" valueClass="col-7" titleClass="col">
                  </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Phone Number" :value="rs.reservationStay?.pickup_driver_phone_number"
                    valueClass="col-7" titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex flex-col mt-2 gap-2">
                  <div>Note</div>
                  <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                    {{ rs.reservationStay?.pickup_note }}
                  </div>
                </div>
              </div>
              <div v-else class="flex justify-center mt-3">
                <span @click="OnSetupForm()"
                  class="link_line_action text-xl line-height-3 px-3 py-2 text-center bg-white"><i
                    class="pi pi-car text-lg me-2"></i>Setup Arrival Mode</span>
              </div>
            </TabPanel>
            <TabPanel header="Departure">
              <div v-if="rs.reservationStay.require_drop_off">
                <div class="flex mt-4 gap-2">
                  <ComBoxStayInformation title="Departure Mode" :value="rs.reservationStay?.departure_mode"
                    valueClass="col-7 " titleClass="col">
                  </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Flight No" :value="rs.reservationStay?.departure_flight_number"
                    valueClass="col-7 " titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Location" :value="rs.reservationStay?.drop_off_location"
                    valueClass="col-7" titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Drop Off Time"
                    :value="moment(rs.reservationStay?.drop_off_time, 'HH:mm:ss').format('h:mm a')" valueClass="col-7"
                    titleClass="col">
                  </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Driver" :value="rs.reservationStay?.drop_off_driver_name"
                    valueClass="col-7" titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                  <ComBoxStayInformation title="Phone number" :value="rs.reservationStay?.drop_off_driver_phone_number"
                    valueClass="col-7" titleClass="col"></ComBoxStayInformation>
                </div>
                <div class="flex flex-col mt-2 gap-2">
                  <div>Note</div>
                  <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                    {{ rs.reservationStay?.drop_off_note }}
                  </div>
                </div>
              </div>
              <div v-else class="flex justify-center mt-3">
                <span @click="OnSetupForm()"
                  class="link_line_action text-xl line-height-3 py-2 text-center px-3 bg-white"><i
                    class="pi pi-car text-lg me-2"></i>Setup Departure Mode</span>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </template>
    </ComReservationStayPanel>
  </div>
  <div class="col" v-else>
    <div class="w-auto">
      <button class="w-full bg-orange-100 rounded-xl" @click="OnSetupForm">
        <div class="flex relative p-2">
          <span class="link_line_action text-xl line-height-3 py-2 text-center px-3 bg-white"><i
              class="pi pi-car text-lg me-2"></i>Setup Transportation</span>
          <!-- <span class="w-9rem" >
          <img class="icon-svg-setup-tran" src="../../../assets/svg/icon-transportation-mode.svg">
        </span>
        <span class="text-2xl">Setup Transportation</span> -->
        </div>
      </button>
    </div>
  </div>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import { useDialog } from 'primevue/usedialog';
import { ref } from "vue";
const dialog = useDialog();
import ComFormSetupArrivalAndDeparture from './ComFormSetupArrivalAndDeparture.vue';
import ComAddDriver from "../../other/driver/ComAddDriver.vue";
import { inject } from 'vue'
const rs = inject('$reservation_stay');
const moment = inject('$moment')
const ManuArriavalDeparture = ref()
const props = defineProps({
  reservationStay: {
    type: Object,
    default: {}
  }
})
const onMenuArriavalDeparture = (event) => {
  ManuArriavalDeparture.value.toggle(event);
};
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
      modal: true,
      closeOnEscape: false,
      position: 'top'
    }
  });
}
const items = ref([
  {
    label:
      'Edit'
    , icon: 'pi pi-fw pi-pencil'
    , command: () => {
      OnSetupForm()
    }
  },
]);
function onEditDriver(name) {
  dialog.open(ComAddDriver, {
    props: {
      header: `Edit Driver`,
      style: {
        width: '50vw',
      },
      breakpoints: {
        '960px': '75vw',
        '640px': '90vw'
      },
      modal: true,
      closeOnEscape: false
    },
    data: {
      drivername: name
    },
    onClose: (options) => {
      const data = options.data;

      stay.value.pickup_driver = data.name
      stay.value.pickup_driver_name = data.driver_name

    }
  })
}

</script>
<style scoped>
.h-min-note {
  min-height: 8rem;
  max-height: 8rem;
}

.p-button-icon-only {
  height: 20px;
  width: 20px;
  margin: auto -3px;
  margin-right: 5px;
}

.Arrival-bg {
  line-height: 21px;
}

.icon-svg-setup-tran {
  height: 60px;
  position: absolute;
  top: -17px;
}
</style>