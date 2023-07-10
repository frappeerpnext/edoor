<template>
    <ComPlaceholder text="There is no Folio transactions" :loading="loading" :isNotEmpty="rs.folio_summary.length > 0">

        <DataTable v-model:selection="rs.selectedFolioTransactions"
            paginator  
            stateKey="folo_transaction_simple_stype_table_state"
            :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
            :value="rs.folioTransactions?.filter(r => (r.parent_reference || '') == '')" tableStyle="min-width: 120rem">
            <Column selectionMode="multiple" headerStyle="width: 3rem" />
            <Column field="name" header="No. "></Column>

            <Column field="posting_date" header="Date">
                <template #body="slotProps">
                    <span>{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
                </template>
            </Column>
            <Column field="room_number" header="Room #"></Column>
            <Column field="account_name" header="Account" style="min-width: 160px;">
                <template #body="slotProps">
                    <span v-if="setting?.show_account_code_in_folio_transaction == 1">{{ slotProps.data.account_code }} -
                    </span>
                    <span>{{ slotProps.data.account_name }}</span>

                </template>
            </Column>
            <Column header="Qty" class="text-right">
                <template #body="slotProps">
                    <span v-if="slotProps?.data?.account_name == 'Loundry'">{{slotProps.data.quantity}}</span>

                </template>
            </Column>
            <Column field="price" header="Amount/Rate" class="text-right" style="min-width: 70px;">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.price" :class="slotProps.data.price<0?'white-space-nowrap text-green-700':'white-space-nowrap'" />
                </template>
            </Column>
            <Column field="discount_amount" header="Discount" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.discount_amount" class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="total_tax" header="Tax" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.total_tax" class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="bank_fee_amount" header="Bank Fee" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.bank_fee_amount" class="white-space-nowrap" />
                </template>
            </Column>

            <Column field="total_amount" header="Total Amount" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.total_amount" :class="slotProps.data.total_amount< 0?'white-space-nowrap text-green-700':'white-space-nowrap'" />
                </template>
            </Column>

            <Column field="note" header="Note" style="min-width: 160px;">
                <template #body="slotProps">
                    <div v-if="slotProps.data.note" v-tooltip.top="slotProps.data.note">
                        {{ slotProps.data.note.slice(0, 20) + (slotProps.data.note.length > 20 ? '...' : '') }}
                    </div>
                </template>
            </Column>
            <Column field="owner" header="Made By"></Column>
            <Column field="creation" header="Created">
                <template #body="slotProps">
                    <span v-if="slotProps.data.creation">{{ gv.datetimeFormat(slotProps.data.creation) }}</span>
                </template>
            </Column>
            <Column>
                <template #body="slotProps">
                    <div  v-if="slotProps.data.name">
                        <ComReservationStayFolioTransactionAction :data="slotProps.data"/> 
                    </div>
                </template>
            </Column>
            <ColumnGroup type="footer">
                <Row>
                    <Column footer="Total:" :colspan="5" footerStyle="text-align:right" />
                    <Column footerStyle="text-align:right">
                        <template #footer>

                            {{ getTotal('quantity') }}
                        </template>
                    </Column>
                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('amount')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('discount_amount')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('total_tax')" />

                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('bank_fee_amount')" />

                        </template>
                    </Column>
                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="getTotal('total_amount')" />

                        </template>
                    </Column>

                    <Column />
                    <Column />
                    <Column />
                    <Column />
                    <!-- <Column/>
                <Column/> -->

                </Row>
            </ColumnGroup>

        </DataTable>
        <div class="w-full flex justify-content-end my-2">
            <div class="w-30rem">
                <div v-for="(item, index) in rs.folio_summary" :key="index" class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency :title="item.account_category" :value="item.amount"
                        valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Total Debit" :value="rs.totalDebit"
                        valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold">
                    </ComBoxStayInformation>
                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Total Credit" :value="rs.totalCredit"
                        valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold">
                    </ComBoxStayInformation>

                </div>
                <div class="flex mt-2 gap-2">
                    <ComBoxStayInformation isCurrency title="Balance" :value="(rs.totalDebit - rs.totalCredit)"
                        valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold">
                    </ComBoxStayInformation>
                </div>
            </div>
        </div>
    </ComPlaceholder>
</template>
<script setup>
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import { inject, ref } from '@/plugin';
import ComReservationStayFolioTransactionAction from "./ComReservationStayFolioTransactionAction.vue";
const gv = inject('$gv');
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const rs = inject('$reservation_stay');
const moment = inject("$moment")
const getTotal = ref((column_name) => {
    if (rs.folioTransactions?.filter(r => (r.parent_reference || '') == '').length == 0) {
        return 0
    } else {
        return rs.folioTransactions?.filter(r => (r.parent_reference || '') == '').reduce((n, d) => n + d[column_name], 0)
    }
});




 
</script>