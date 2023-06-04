<template lang="">
<ComReservationStayPanel title="Business Source & Rate">
                                <template #content>
                                <div class="flex">
                                    <div class="flex mt-2 w-full ">
                                        <div class="col-6">
                                            <div class="grid">
                                                <div class="col-fixed pl-0 w-10rem">Business Sources</div>
                                                <div class="grow py-2 px-3 bg-white border-round-lg">
                                                    <div class="flex justify-content-between align-items-center">
                                                        <span class="link_line_action">{{ rs?.reservationStay?.business_source }}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="col-6">
                                            <div class="grid">
                                                <div class="col-fixed w-10rem text-right">Rate Type</div>
                                                <div class="grow py-2 px-3 bg-white border-round-lg">
                                                    <div class="flex justify-content-between align-items-center">
                                                        <span class="link_line_action">{{ rs?.reservationStay?.rate_type }}</span>
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
import {inject} from "@/plugin"
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
const rs = inject("$reservation_stay")
</script>
<style scoped></style>