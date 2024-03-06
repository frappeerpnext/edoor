<template>
    <DataTable :value="data" paginator :rows="20" tableStyle="min-width: 50rem" :rowsPerPageOptions="[5, 10, 20, 50]">
        <Column :header="$t('No')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column :header="$t('Reservation') + ' #' " headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_detail', slotProps.data.reservation)" link>
                    {{ slotProps?.data.reservation }}
                </Button>
            </template>
        </Column>
        <Column field="name" :header="$t('Stay') + ' #' " headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <Button class="p-0 link_line_action1"
                    @click="onViewDetail('view_reservation_stay_detail', slotProps.data.name)" link>
                    {{ slotProps?.data.name }}
                </Button>
            </template>
        </Column>
        <Column field="reference_number" :header="$t('Ref') + '. #' "></Column>
        <Column field="business_source" :header="$t('Source')"></Column>
        <Column field="name" :header="$t('PAX(A/C)')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps?.data.adult }} / {{ slotProps?.data.child }}
            </template>
        </Column>
        <Column field="reservation_type" :header="$t('Type')"></Column>
        <Column :header="$t('Res. Date')">
            <template #body="slotProps">

                {{ moment(slotProps?.data.reservation_date).format("DD-MM-YYYY") }}
            </template>

        </Column>
        <Column field="name" :header="$t('Stay Date')">
            <template #body="slotProps">
                {{ moment(slotProps.data.arrival_date).format("DD-MM-YYYY") }} &#8594; {{
                    moment(slotProps.data.departure_date).format("DD-MM-YYYY") }}

            </template>
        </Column>
        <Column field="room_nights" headerClass="text-center" :header="$t('Room Nights')">
            <template #body="slotProps">
                <div class="text-center">
                    {{ slotProps?.data.room_nights }}
                </div>

            </template>
        </Column>
        <Column :header="$t('Room(s)')">
            <template #body="slotProps">
                <div>
                    <span v-tippy="slotProps?.data.room_type">
                        {{ slotProps?.data.room_type_alias }}
                    </span>/<span v-if="slotProps?.data.rooms">
                        {{ slotProps?.data.rooms }}
                    </span>
                    <span @click="onAssignRoom(slotProps?.data)" class="link_line_action w-auto" v-else>
                        <i class="pi pi-pencil"></i>
                        Assign Room
                    </span>
                </div>
            </template>
        </Column>
        <Column :header="$t('Guest')">
            <template #body="slotProps">
                <div>
                    <Button class="p-0 link_line_action1" @click="onViewDetail('view_guest_detail', slotProps.data.guest)"
                        link>
                        {{ slotProps?.data.guest }} - {{ slotProps?.data.guest_name }}
                    </Button>
                </div>

            </template>
        </Column>
        <Column headerClass="text-right" bodyClass="text-right" :header="$t('ADR')">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps?.data.adr" />
            </template>
        </Column>
        <Column headerClass="text-right" bodyClass="text-right" :header="$t('Discount')">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps?.data.room_rate_discount" />
            </template>

        </Column>
        <Column headerClass="text-right" bodyClass="text-right" :header="$t('Total Room Rate')">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps?.data.total_room_rate" />
            </template>

        </Column>
        <Column headerClass="text-center" bodyClass="text-center" :header="$t('Status')">
            <template #body="slotProps">
                <span class="px-2 rounded-lg text-white p-1px border-round-3xl"
                    :style="{ backgroundColor: slotProps?.data.status_color }">{{ $t(slotProps?.data.reservation_status)
                        }}</span>
            </template>
        </Column>
        <ColumnGroup type="footer">
            <Row>
                <Column :footer="$t('Total') + ':'" :colspan="2" footerStyle="text-align:right" />
                <Column :colspan="3" footerStyle="text-align:right" />
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('adult') }}/{{ getTotal('child') }}
                    </template>
                </Column>

                <Column :colspan="3" />

                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('room_nights') }}
                    </template>
                </Column>
                <Column :colspan="2" />
                <Column footerStyle="text-align:end">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_room_rate') / getTotal('room_nights')" />
                    </template>
                </Column>
                <Column footerStyle="text-align:end">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('room_rate_discount')" />
                    </template>
                </Column>
                <Column footerStyle="text-align:end">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_room_rate')" />
                    </template>
                </Column>
                <Column :colspan="1" />
            </Row>
        </ColumnGroup>
    </DataTable>
</template>
<script setup>
import { inject, getDoc, ref } from '@/plugin';
const moment = inject("$moment")
import ComReservationStayAssignRoom from '@/views/reservation/components/ComReservationStayAssignRoom.vue';

import { useDialog } from 'primevue/usedialog';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog();
const props = defineProps({
    data: Object
})
function onViewDetail(action, name) {

    window.postMessage(action + "|" + name, "*")
}

function onAssignRoom(data) {
    getDoc("Reservation Stay", data.name).then(doc => {
        const stay_room = doc.stays.find(r => !r.room_id)
        if (stay_room) {
            dialog.open(ComReservationStayAssignRoom, {
                data: { stay_room: stay_room },
                props: {
                    header: `Assign Room`,
                    style: {
                        width: '80vw',
                    },
                    modal: true,
                    closeOnEscape: false,
                    position: 'top',
                    breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
                },
                onClose: (options) => {
                    if (options.data && options.data.message) {
                        setTimeout(() => {
                            rs.getReservationDetail(options.data.message.name)
                        }, 1500);
                    }
                }
            })
        }
    })
}

const getTotal = ref((column_name) => {
    return props.data?.reduce((n, d) => n + d[column_name], 0)
});
</script>