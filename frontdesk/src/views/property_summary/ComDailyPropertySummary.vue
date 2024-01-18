<template>
    <Button @click="loadData" class="btn-refresh-in-night-audit arrival_guest"><i class="pi pi-refresh"></i></Button>
    <ComDialogContent hideButtonClose hideButtonOK>
        <ComSkeleton v-if="loading" />
        <template v-else>
            <ComStatistic :property="dialogRef.data.property" :date="dialogRef.data.date"
                :room_type_id="dialogRef.data.room_type_id" />

            <hr />


            <TabView>
                <TabPanel header="Arrival/Stay Over/Departure">
                    <Accordion :multiple="true" :activeIndex="[0, 1, 2]">
                        <AccordionTab :header="'Arrival Guests (' + data?.arrival.length + ')'">
                            <ComArrivalGuest :data="data?.arrival" />
                        </AccordionTab>
                        <AccordionTab :header="'Stay Over Guest (' + data?.stay_over.length + ')'">
                            <ComArrivalGuest :data="data?.stay_over" />
                        </AccordionTab>
                        <AccordionTab :header="'Departure Guest (' + data?.departure.length + ')'">
                            <ComArrivalGuest :data="data?.departure" />
                        </AccordionTab>

                    </Accordion>
                </TabPanel>
                <TabPanel :header="'Unassign room (' + data?.unassign_room.length + ')'">
                    <ComArrivalGuest :data="data?.unassign_room" />
                </TabPanel>
                <TabPanel header="Pickup & Drop Off Guest">
                    <ComPickUpandDropOff :data="data?.pickup_drop_off" />
                </TabPanel>
                <TabPanel :header="'No Show, Cancelled & Void (' + data?.inactive_reservation.length + ')'"> 
                    <Accordion :multiple="true" :activeIndex="[0, 1, 2]">
                        <AccordionTab :header="'No Show (' + data?.inactive_reservation.length + ')'">
                            <ComInactiveReservation :data="data?.inactive_reservation" />
                        </AccordionTab> 
                        <AccordionTab :header="'Cancelled & Void (' + data?.today_cancelled_and_void.length + ')'">
                            <ComInactiveReservation :data="data?.today_cancelled_and_void" />
                        </AccordionTab> 
                    </Accordion>
                </TabPanel>
                <TabPanel :header="'Room Block (' + data?.room_block.length + ')'">
                    <ComRoomBlock :data="data?.room_block" />
                </TabPanel>
                <TabPanel header="Summary">
                    <Accordion :multiple="true" :activeIndex="[0, 1, 2]">
                        <AccordionTab header="Summary by Business Source">
                            <ComSummaryByBusinessSource :property="dialogRef.data.property" :date="dialogRef.data.date"
                                :room_type_id="dialogRef.data.room_type_id" />
                        </AccordionTab>

                        <AccordionTab header="Summary by Reservation Type">
                            <ComSummaryByReservationType :property="dialogRef.data.property" :date="dialogRef.data.date"
                                :room_type_id="dialogRef.data.room_type_id" />
                        </AccordionTab>

                        <AccordionTab header="Summary by Room Type">
                            <ComSummaryByRoomType :property="dialogRef.data.property" :date="dialogRef.data.date"
                                :room_type_id="dialogRef.data.room_type_id" />
                        </AccordionTab> 
                    </Accordion> 
                </TabPanel>
            </TabView> 
        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, getApi, inject } from '@/plugin';
const data = ref()
const loading = ref(false)
const dialogRef = inject("dialogRef");

import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';


import ComStatistic from '@/views/property_summary/components/ComStatistic.vue';
import ComArrivalGuest from '@/views/property_summary/components/ComArrivalGuest.vue';
import ComPickUpandDropOff from '@/views/property_summary/components/ComPickUpandDropOff.vue';
import ComInactiveReservation from '@/views/property_summary/components/ComInactiveReservation.vue';
import ComRoomBlock from '@/views/property_summary/components/ComRoomBlock.vue';
import ComSummaryByRoomType from '@/views/property_summary/components/ComSummaryByRoomType.vue';
import ComSummaryByBusinessSource from '@/views/property_summary/components/ComSummaryByBusinessSource.vue';
import ComSummaryByReservationType from '@/views/property_summary/components/ComSummaryByReservationType.vue';
import ComSkeleton from '@/views/property_summary/components/ComSkeleton.vue';

onMounted(() => {
    loadData()
})
const loadData = () => {
    loading.value = true
    setTimeout(function () {
        getApi("frontdesk.get_daily_property_data_detail", {
            property: dialogRef.value.data.property,
            date: dialogRef.value.data.date,
            room_type: dialogRef.value.data.room_type_id,

        }).then(r => {
            data.value = r.message
            loading.value = false
        }).catch(err => {
            loading.value = false
        })
    }, 500) 
}
</script>
<style scoped>
    .arrival_guest{
        top:8px !important;
        right:69px !important;
    }
</style>