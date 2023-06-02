<template>
  <div class="col-12">
    <ComReservationStayPanel title="Arrival & Departure Mode">
      <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded />
      </template>
      <template #content>
        <div class="mt-2 Arrival-bg">
          <TabView>
            <TabPanel header="Arrival">
              <div class="flex mt-4 gap-2">
                <ComBoxStayInformation title="Arrival Mode" value="TukTuk" valueClass="col-7 " titleClass="grow">
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Flight No" value="N/A" valueClass="col-7 " titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Station" value="Siem Reap Airport 02" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Require Pickup" value="9:00 AM" valueClass="col-7" titleClass="grow">
                  <Button icon="pi pi-check" class="border-none" aria-label="Filter" />
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Driver" value="balabong Dav" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex flex-col mt-2 gap-2">
                <div>Note</div>
                <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                  Do not late Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                </div>
              </div>
              
            </TabPanel>
            <TabPanel header="Departure">
              <div class="flex mt-4 gap-2">
                <ComBoxStayInformation title="Departure Mode" value="TukTuk" valueClass="col-7 " titleClass="grow">
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Flight No" value="N/A" valueClass="col-7 " titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Station" value="Siem Reap Airport 02" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Require Pickup" value="9:00 AM" valueClass="col-7" titleClass="grow">
                  <Button icon="pi pi-check" class="border-none" aria-label="Filter" />
                </ComBoxStayInformation>
              </div>
              <div class="flex mt-2 gap-2">
                <ComBoxStayInformation title="Driver" value="balabong Dav" valueClass="col-7" titleClass="grow"></ComBoxStayInformation>
              </div>
              <div class="flex flex-col mt-2 gap-2">
                <div>Note</div>
                <div class="w-full overflow-y-auto h-min-note bg-white rounded-xl p-3 break-words">
                  Do not late Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                </div>
              </div>
            </TabPanel>
          </TabView>
        </div>
      </template>
    </ComReservationStayPanel>
  </div>
  <div class="col">
  <div class="w-auto mt-4 ">
    <button class="w-full ">
      <div class="flex relative px-5 bg-orange-100 rounded-xl py-4">
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
import { inject } from 'vue'
const moment = inject('$moment')
const props = defineProps({
  reservationStay: {
    type: Object,
    default: {}
  }
})
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