<template>
    <DataTable :value="data" paginator :rows="20" :rowsPerPageOptions="[5, 10, 20, 50]">
        <Column :header="$t('No')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column field="reservation" :header="$t('Reservation #')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_detail', slotProps.data.reservation)" link>
                    {{ slotProps.data.reservation }}
                </Button>
            </template>
        </Column>


        <Column field="reservation_stay" :header="$t('Stay #') " headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_stay_detail', slotProps.data.name)" link>
                    {{ slotProps.data.reservation_stay }}
                </Button>
            </template>
        </Column>
        <Column field="reference_number" :header="$t('Ref. #')" headerClass="text-center" headerStyle="min-width:100px;"
            bodyClass="text-center" />
        <Column field="business_source" :header="$t('Source')"></Column>
        <Column :header="$t('Pax(A/C)')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.adult }} / {{ slotProps.data.child }}

            </template>

        </Column>
        <Column field="reservation_type" :header="$t('Type')" headerClass="text-center" bodyClass="text-center" />
        <Column :header="$t('Stay Date')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ moment(slotProps.data.arrival_date).format("DD-MM-YYYY") }}  {{$t('to')}} {{
                    moment(slotProps.data.departure_date).format("DD-MM-YYYY") }}

            </template>

        </Column>
        <Column :header="$t('Room(s)')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.room_type_alias }}
                <span v-if="slotProps.data.rooms">/ {{ slotProps.data.rooms }}</span>
            </template>

        </Column>
        <Column field="guest" :header="$t('Guest')">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1" @click="onViewDetail('view_guest_detail', slotProps.data.guest)" link>
                    {{ slotProps.data.guest }} - {{ slotProps.data.guest_name }}
                </Button>

            </template>
        </Column>

        <Column field="business_source" :header="$t('Source')" />
        <Column header="Time" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <span v-if="slotProps.data.time">
                    {{ slotProps.data.time.split(":")[0] }} :
                    {{ slotProps.data.time.split(":")[1] }}
                </span>

            </template>

        </Column>
        <Column field="mode" :header="$t('Mode')" />
        <Column field="flight_number" :header="$t('Flight') + ' #' " headerStyle="min-width:100px;" />
        <Column field="location" :header="$t('Location')" />
        <Column field="driver_name" :header="$t('Driver')" />
        <Column field="driver_phone_number" :header="$t('Phone') + '#' " />
        <Column :header="$t('Type')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.type }}
            </template>
        </Column>
        <Column field="note" :header="$t('Note')" />

    </DataTable>
</template>
<script setup>
import { inject } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
const props = defineProps({
    data: Object
})
function onViewDetail(action, name) {

    window.postMessage(action + "|" + name, "*")
}    
</script>