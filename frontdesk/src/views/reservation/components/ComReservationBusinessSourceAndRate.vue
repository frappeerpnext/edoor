<template lang="">
<ComReservationStayPanel title="Business Source & Rate">
                                <template #content>
                                <div class="flex">
                                    <div class="flex mt-2 w-full ">
                                        <div class="col-6">
                                            <div class="grid">
                                                <div class="col-fixed w-10rem">Business Sources</div>
                                                <div class="grow py-1 px-3 bg-white border-round-lg">
                                                    <div class="flex justify-content-between align-items-center">
                                                        <span>Direct Booking</span>
                                                        <Button icon="pi pi-pencil" text rounded aria-label="Filter" class="h-2rem w-2rem" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="grid">
                                                <div class="col-fixed w-10rem text-right">Rate Type</div>
                                                <div class="grow py-1 px-3 bg-white border-round-lg h-full">
                                                    <div class="flex justify-content-between align-items-center">
                                                        <span>Direct Booking</span>
                                                        <Button icon="pi pi-pencil" text rounded aria-label="Filter" class="h-2rem w-2rem" />
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
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
<style scoped></style>