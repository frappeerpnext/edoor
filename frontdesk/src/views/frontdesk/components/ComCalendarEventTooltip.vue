<template>
    <div class="p-2 w-full " v-if="event.extendedProps.type == 'stay'">
        <div class="text-center mb-3 border-1 p-2 border-round-lg overflow-hidden text-overflow-ellipsis ">
            <span class="me-2"> {{ event.title }}
            </span>
        </div>
        <table class="tip_description_stay_table m-1 pt-4">
            <tbody>
                <tr class="table-rs-de">
                    <td>Res. No</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.reservation || '' }}</td>
                </tr>
                <tr class="table-rs-de" v-if="event.extendedProps.reservation_color">
                    <td>Res Special Color</td>
                    <td class="px-2">:</td>
                    <div class="flex mt-1 align-items-center">
                        <div style="height:14px !important;" class="px-4 inline-block border-1 border-white me-2"
                            :style="{ background: event.extendedProps.reservation_color }"></div> <span>
                            {{ event.extendedProps.reservation_color_code }} </span>
                    </div>
                </tr>
                <tr class="table-rs-de">
                    <td>Res Stay Status</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.reservation_status || '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Res Stay. No</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.reservation_stay || '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Ref. No</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.reference_number || '' }} </td>
                </tr>
                <tr class="table-rs-de">
                    <td>Int. No</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.internal_reference_number ?? '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Ref. type</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.reservation_type || '' }} </td>
                </tr>
                <tr class="table-rs-de"
                    v-if="event.extendedProps?.group_name || event.extendedProps?.group_code || event.extendedProps?.group_color">
                    <td>Group</td>
                    <td class="px-2">:</td>
                    <td>
                        <div style="height:14px !important;" class="px-4 inline-block border-1 border-white me-2"
                            :style="{ background: event.extendedProps.group_color }"></div><span
                            v-if="event.extendedProps?.group_name">{{ event.extendedProps?.group_name || '' }}</span> <span
                            v-if="event.extendedProps?.group_code"> - {{ event.extendedProps?.group_code || '' }}</span>
                    </td>
                </tr>
                <tr class="table-rs-de">
                    <td>Arrival</td>
                    <td class="px-2">:</td>
                    <td>{{ moment(event.extendedProps?.arrival_date).format('DD-MM-YYYY') }} -
                        {{ moment(event.extendedProps?.start_time, "HH:mm:ss").format("h:mm A") }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Departure</td>
                    <td class="px-2">:</td>
                    <td>{{ moment(event.extendedProps?.departure_date).format('DD-MM-YYYY') }} -
                        {{ moment(event.extendedProps?.end_time, "HH:mm:ss").format("h:mm A") }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Nights</td>
                    <td class="px-2">:</td>
                    <td>{{ moment(event.extendedProps?.departure_date).diff(event.extendedProps?.arrival_date, 'days') }}
                    </td>
                </tr>
                <tr class="table-rs-de">
                    <td>Room</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps.stay_rooms || event.extendedProps?.room_number }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Pax</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.adult }} / {{ event.extendedProps?.child }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Source</td>
                    <td class="px-2">:</td>
                    <td>{{ event.extendedProps?.business_source || '' }}</td>
                </tr>
                <template v-if="can_view_rate">
                    <tr class="table-rs-de">
                        <td>ADR</td>
                        <td class="px-2">:</td>
                        <td>
                            <CurrencyFormat :value="event.extendedProps?.reservation_stay_adr" />
                        </td>
                    </tr>
                    <tr class="table-rs-de">
                        <td>Total Room Rate</td>
                        <td class="px-2">:</td>
                        <td>
                            <CurrencyFormat :value="event.extendedProps?.total_room_rate" />
                        </td>
                    </tr>
                    <tr class="table-rs-de">
                        <td>Total Debit</td>
                        <td class="px-2">:</td>
                        <td>
                            <CurrencyFormat :value="event.extendedProps?.total_debit" />
                        </td>
                    </tr>
                    <tr class="table-rs-de">
                        <td>Total Credit</td>
                        <td class="px-2">:</td>
                        <td>
                            <CurrencyFormat :value="event.extendedProps?.total_credit" />

                        </td>
                    </tr>
                    <tr class="table-rs-de">
                        <td>Balance</td>
                        <td class="px-2">:</td>
                        <td>
                            <CurrencyFormat :value="event.extendedProps?.balance" />
                        </td>
                    </tr>
                </template>
                <tr v-if="event.extendedProps?.note != 'null' && event.extendedProps?.note">
                    <td><span class="mt-2">Note</span></td>
                </tr>
                <tr v-if="event.extendedProps?.note != 'null' && event.extendedProps?.note">
                    <td colspan="3">
                        <div class="border-round-lg p-2 reason-box-style">{{ event.extendedProps?.note.length > 220 ?
                            event.extendedProps?.note.substring(0, 220) + '...' : event.extendedProps?.note }}</div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-else-if="event.extendedProps.type == 'room_block'" class="w-full p-2">
        <div class="text-center border-1 p-2 border-round-lg"> {{ event.title }}</div>

        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
            <tbody>

                <tr class="table-rs-de">
                    <td>Block Number</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.publicId || '' }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Start Date</td>
                    <td class="px-3">:</td>
                    <td> {{ moment(event?.start_date).format('DD-MM-YYYY') }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Release Date</td>
                    <td class="px-3">:</td>
                    <td> {{ moment(event?.end_date).format('DD-MM-YYYY') }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Night Of Block</td>
                    <td class="px-3">:</td>
                    <td>{{ moment(event?.end_date).diff(event?.start_date, 'days') }} Nights </td>
                </tr>
                <tr class="table-rs-de">
                    <td>Blocked by</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps?.block_by || '' }}</td>
                </tr>
                <tr>
                    <td><span class="mt-2">Reason</span></td>
                </tr>
                <tr>
                    <td colspan="3">
                        <div class="border-round-lg p-2 reason-box-style"> {{ event.extendedProps?.reason }}</div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

    <div v-else-if="event.extendedProps.type == 'room_type_event'" class="w-full p-2">

        <div class="text-center border-1 p-2 border-round-lg">Available Room <span class="mx-3"
                :style="{ color: event.ui.backgroundColor }"> {{ event.extendedProps.room_available }} of {{
                    event.extendedProps.total_room || 0 }}</span> </div>
        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
            <tbody>
                <tr class="table-rs-de">
                    <td>Room Type</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.room_type }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Date</td>
                    <td class="px-3">:</td>
                    <td> {{ moment(event.extendedProps.current_date).format("DD-MM-YYYY") }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Total Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.total_room || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Total Room Sold</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.total_room_sold || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Occupacy</td>
                    <td class="px-3">:</td>
                    <td> {{ occupancy || 0 }}%</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Unassign Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.unassign_room || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Arrival</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.arrival }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Stay Over</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.stay_over }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Departure</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.departure }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Room Block</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.room_block }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Adult</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.adult }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Child</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps?.child }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-else-if="event.extendedProps.type == 'property_summary'">
        <div class="text-center border-1 p-2 border-round-lg">Available Room <span class="mx-3"> {{
            event.extendedProps.room_available }} of {{ event.extendedProps.total_room || 0 }}</span> </div>

        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
            <tbody>
                <tr class="table-rs-de">
                    <td>Date</td>
                    <td class="px-3">:</td>
                    <td> {{ moment(event.extendedProps.current_date).format("DD-MM-YYYY") }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Total Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.total_room || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Total Room Sold</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.total_room_sold || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Occupacy</td>
                    <td class="px-3">:</td>
                    <td> {{ occupancy || 0 }}%</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Unassign Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.unassign_room || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Arrival</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.arrival }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Stay Over</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.stay_over }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Deprture</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.departure }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Room Block</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.room_block }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Adult</td>
                    <td class="px-3">:</td>
                    <td> {{ event?.extendedProps?.adult }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Child</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps?.child }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-else-if="event.extendedProps.type == 'room_inventory_room_type_summary'">

        <table class="tip_description_stay_table mx-1 my-2 pt-3 ">
            <tbody>
                <tr class="table-rs-de">
                    <td>Room Type</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.room_type }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Date</td>
                    <td class="px-3">:</td>
                    <td> {{ moment(event.extendedProps.current_date).format("DD-MM-YYYY") }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Vacant Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.room_available || 0 }}</td>
                </tr>
                <tr class="table-rs-de">
                    <td>Unassign Room</td>
                    <td class="px-3">:</td>
                    <td> {{ event.extendedProps.unassign_room || 0 }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import { computed } from "vue"
import CurrencyFormat from "@/components/CurrencyFormat.vue"
import moment from "@/utils/moment.js";
const props = defineProps({
    event: Object
})

const occupancy = computed(() => {
    const d = props.event.extendedProps

    return (((d.total_room_sold || 0) / ((d.total_room || 0) - (window.setting.calculate_room_occupancy_include_room_block == 1 ? 0 : (d.room_block || 0)))) * 100).toFixed(2)

})

const can_view_rate = window.can_view_rate



</script>
