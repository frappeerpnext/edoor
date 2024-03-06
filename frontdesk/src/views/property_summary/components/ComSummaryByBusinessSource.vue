<template>
    <DataTable :value="data">
        <Column :header="$t('No')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ data.indexOf(slotProps.data) + 1 }}
            </template>
        </Column>
        <Column field="business_source" :header="$t('Business Source')" />

        <Column field="total_room" :header="$t('Total Room(s)')" headerClass="text-center" bodyClass="text-center" />
        <Column field="total_room_sold" :header="$t('Room Sold')" headerClass="text-center" bodyClass="text-center" />
        <Column field="block" :header="$t('Room Block')" headerClass="text-center" bodyClass="text-center" />
        <Column :header="$t('PAX(A/C)')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.adult }} / {{ slotProps.data.child }}
            </template>
        </Column>
        <Column :header="$t('FIT/GIT')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.fit }} / {{ slotProps.data.git }}
            </template>
        </Column>
        <Column :header="$t('Pickup/Drop Off')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.pick_up }} / {{ slotProps.data.drop_off }}
            </template>
        </Column>
        <Column :header="$t('Checked In') + ' / ' + $t('Arrival')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.checked_in }} / {{ slotProps.data.arrival }}
            </template>
        </Column>
        <Column :header="$t('Stay Over')" field="stay_over" headerClass="text-center" bodyClass="text-center" />
        <Column :header="$t('Checked Out') + ' / ' + $t('Departure')" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                {{ slotProps.data.checked_out }} / {{ slotProps.data.departure }}
            </template>
        </Column>
        <Column field="no_show" :header="$t('No Show')" headerClass="text-center" bodyClass="text-center" />


        <Column headerClass="text-right" bodyClass="text-right" :header="$t('ADR')">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps?.data.adr" />
            </template>
        </Column>
        <Column headerClass="text-right" bodyClass="text-right" :header="$t('Total Room Rate')">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps?.data.total_rate" />
            </template>

        </Column>
        <Column headerClass="text-center" bodyClass="text-center" :header="$t('Occupancy')">
            <template #body="slotProps">
                {{ ( slotProps?.data?.occupancy || 0 ).toFixed(2)}}%
            </template>

        </Column>
        <ColumnGroup type="footer">
            <Row>
                <Column :footer="$t('Total') + ':'" :colspan="2" footerStyle="text-align:right" />
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ data?.length > 0 ? data[0]["total_room"] : 0 }}
                    </template>
                </Column>
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('total_room_sold') }}
                    </template>
                </Column>
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ data?.length > 0 ? data[0]["block"] : 0 }}
                    </template>
                </Column>
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('adult') }}/{{ getTotal('child') }}
                    </template>
                </Column>
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('fit') }}/{{ getTotal('git') }}
                    </template>
                </Column>

                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('pick_up') }}/{{ getTotal('drop_off') }}
                    </template>
                </Column>

                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('checked_in') }}/{{ getTotal('arrival') }}
                    </template>
                </Column>


                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('stay_over') }}
                    </template>
                </Column>

                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('checked_out') }}/{{ getTotal('departure') }}
                    </template>
                </Column>

                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ getTotal('no_show') }}
                    </template>
                </Column>
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_rate') / getTotal('total_room_sold')" />
                    </template>
                </Column>

                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_rate')" />
                    </template>
                </Column>
                <Column footerStyle="text-align:center">
                    <template #footer>
                        {{ (getTotal('total_room_sold') / (data?.length > 0 ? data[0]["occupancy_room"] : 1) *
                            100).toFixed(2)
                        }}%
                    </template>
                </Column>

            </Row>
        </ColumnGroup>

    </DataTable>
</template>
<script setup>
import { ref, onMounted, getApi, inject } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const data = ref()
const loading = ref(false)

const props = defineProps({
    property: String,
    date: String,
    room_type_id: String
})

const getTotal = ref((column_name) => {

    return data.value?.reduce((n, d) => n + d[column_name], 0)

});

onMounted(() => {
    setTimeout(() => {
        loading.value = true
        getApi("frontdesk.get_daily_summary_by_business_source", {
            property: props.property,
            date: props.date,
            room_type_id: props.room_type_id,
        }).then(result => {
            data.value = result.message
            loading.value = false
        }).catch(err => {
            loading.value = false
        })
    }, 5000);

})
</script>