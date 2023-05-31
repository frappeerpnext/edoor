<template>
        <div class="col">
    <ComReservationStayPanel title="Arrival & Departure Mode">
        <template #content>
            <div class="mt-2 Arrival-bg">
            <TabView>
            <TabPanel  header="Arrival">
                <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Arrival Mode" value="hi" valueClass="col-6 " titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Flight No"  valueClass="col-6 " titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Station"  valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Require Pickup"  valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
              <ComBoxStayInformation title="Driver"  valueClass="col-6" titleClass="grow" ></ComBoxStayInformation>
                </div>
               
            </TabPanel>
            <TabPanel header="Departure">
                <p>
                    Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim
                    ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Consectetur, adipisci velit, sed quia non numquam eius modi.
                </p>
            </TabPanel>
        </TabView>
            </div>
        </template>
    </ComReservationStayPanel>
        </div>
</template>
<script setup>
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import {inject} from 'vue'
const moment = inject('$moment')
 const props = defineProps({
    reservationStay: {
        type: Object,
        default: {}
    }
 })
</script>
<style scoped>

</style>