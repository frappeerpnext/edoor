<template>
    <ComPlaceholder :text="$t('There is no Folio transactions')" :loading="loading" :isNotEmpty="folioTransactions.length > 0">

        <DataTable :scrollable="folioTransactions.length > 10"
            :scrollHeight="(folioTransactions.length > 10 ? '500px' : 'auto')"
            :virtualScrollerOptions="{ itemSize: 40 }" v-model:selection="selectedfolioTransactions"
            :stateKey="'folo_transaction_table_state_' + selectedFolio.name" @row-dblclick="onViewFolioDetail"
            :value="folioTransactions" tableStyle="min-width: 50rem" :rowClass="rowStyleClass">

            <Column expander style="width: 5rem" v-if="showExpander" />
            <Column selectionMode="multiple" headerStyle="width: 3rem" v-if="showCheckbox">

            </Column>
            <Column field="is_package" bodyClass="text-center p-0" headerClass="text-center p-0">
                <template #body="slotProps">
                    <span @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.is_package"
                        class="package_room_rate">
                        <ComIcon icon="iconPackage" height="20px" />
                    </span>
                </template>
            </Column>
            <Column field="name" :header="$t('Tran. #')" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <button @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.name"
                        :class="'link_line_action1 ' + (slotProps.data?.is_auto_post == 1 ? 'auto_post' : '')">{{
                            slotProps.data?.name }}</button>
                    <slot name="name" :item="slotProps.data" :index="slotProps.data.name">
                    </slot>
                </template>
            </Column>
            <Column v-if="showSourceTransactionNumber" field="source_transaction_number" :header="$t('Folio #')"
                headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <button
                        @click="onOpenLink('view_reservation_folio_detail', slotProps.data.source_transaction_number)"
                        v-if="slotProps.data.source_transaction_type = 'Reservation Folio' && slotProps.data.source_transaction_number" class="link_line_action1">{{
                        slotProps.data.source_transaction_number }}</button>



                </template>
            </Column>
            <Column :header="$t('Room') + ' #'" headerClass="text-center white-space-nowrap" bodyClass="text-center">
                <template #body="slotProps">
                    {{ slotProps.data.room_number }}
                    <slot name="room" :item="slotProps.data" :index="slotProps.data.name">
                    </slot>
                </template>
            </Column>
            <Column field="posting_date" :header="$t('Post Date')" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <span v-if="slotProps.data?.posting_date">{{
                        moment(slotProps.data?.posting_date).format("DD-MM-YYYY")
                    }}</span>
                    <slot name="posting_date" :item="slotProps.data" :index="slotProps.data.name">
                    </slot>
                </template>
            </Column>

            <Column field="account_name" :header="$t('Account Name')" style="min-width: 160px;">
                <template #body="slotProps">
                    {{ $t(slotProps.data.account_name) }}

                    <span v-if="slotProps.data.sale">({{ slotProps.data.sale }}/{{ slotProps.data.tbl_number }})</span>
                    <slot name="description" :item="slotProps.data" :index="slotProps.data.name">
                    </slot>
                </template>
            </Column>

            <Column field="quantity" :header="$t('QTY')" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <span v-if="slotProps.data.quantity > 0">{{ slotProps.data.quantity }}</span>
                </template>
            </Column>

            <Column field="debit" :header="$t('Debit(Charge)')" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat v-if="slotProps.data.debit > 0" :value="slotProps.data.debit"
                        class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="credit" :header="$t('Credit(Payments)')" class="text-right" style="min-width: 70px;">
                <template #body="slotProps">
                    <CurrencyFormat v-if="slotProps.data.credit > 0" class="text-green-700 white-space-nowrap"
                        :value="slotProps.data.credit" />
                </template>
            </Column>
            <Column headerClass="white-space-nowrap" field="balance" :header="$t('Balance')" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.balance" class="white-space-nowrap" />
                </template>
            </Column>

            <Column field="owner" :header="$t('Made By')">
                <template #body="slotProps">
                    {{ slotProps.data.owner?.split("@")[0] }}
                </template>
            </Column>
            <Column field="creation" :header="$t('Created')">
                <template #body="slotProps">
                    <span v-if="slotProps.data.creation">
                        <ComTimeago :date="slotProps.data.creation" />
                    </span>
                </template>
            </Column>

            <Column header="">
                <template #body="slotProps">
                    <div v-if="slotProps.data.name">
                        <ComReservationStayFolioTransactionAction :is-edit="true" :is-delete="true"
                            :data="slotProps.data" />
                    </div>
                </template>
            </Column>
            <ColumnGroup type="footer">
                <Row>
                    <Column :footer="$t('Total') + ':'" :colspan="getTotalSpanColumn()"
                        footerStyle="text-align:right" />
                    <Column footerStyle="text-align:center">
                        <template #footer>
                            {{ totalQuantity }}
                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>

                            <CurrencyFormat v-if="can_view_rate" :value="totalDebit" />
                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat v-if="can_view_rate" :value="totalCredit" />
                        </template>
                    </Column>



                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat v-if="can_view_rate"
                                :value="(selectedFolio.total_debit - selectedFolio.total_credit)" />
                        </template>
                    </Column>

                    <Column />
                    <Column />
                    <Column />
                </Row>
            </ColumnGroup>

        </DataTable>

        <div v-if="can_view_rate" class="w-full flex justify-content-end my-2" id="detl_foloi">
            <div class="w-30rem">
                <div v-for="(item, index) in folio_summary" :key="index" class="flex mt-2 gap-2">
                    <ComBoxStayInformation :title="item?.account_category || 'Undefine'" :value="item?.amount || 0"
                        isCurrency valueClass="col-6 text-right bg-gray-edoor-10 font-semibold"
                        titleClass="col font-semibold">
                    </ComBoxStayInformation>
                </div>

            </div>
        </div>
    </ComPlaceholder>
</template>
<script setup>

import { inject, ref, useDialog, computed, onUnmounted, onMounted, getApi, watch } from '@/plugin';

import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioTransactionAction from '@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioTransactionAction.vue';

import Enumerable from 'linq'
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    folio: Object,
    doctype: {
        type: String,
        default: "Reservation Folio"
    },
    transaction_number: String,
    showCheckbox: {
        type: Boolean,
        default: true
    },
    showExpander: {
        type: Boolean,
        default: false
    },
    cityLedgerInvoice: {
        type: String,
        default: ""
    },
    showSourceTransactionNumber: Boolean
})
const selectedFolio = ref(props.folio)
const gv = inject('$gv');
const can_view_rate = window.can_view_rate;
const folioTransactions = ref([])
const selectedfolioTransactions = defineModel('selectedfolioTransactions')
const folio_summary = ref()

const dialog = useDialog();
const show = ref()



watch(() => props.folio, (newValue, oldValue) => {
    selectedFolio.value = newValue
    LoadFolioTransaction()
    selectedfolioTransactions.value = []
})


function getTotalSpanColumn() {
    let n = 5;
    if (props.showCheckbox) n = n + 1
    if (props.showSourceTransactionNumber) n = n + 1
    return n
}

//load data
function LoadFolioTransaction() {
    let show_package_breakdown = 0
    if (localStorage.getItem('displayViewFolioTransaction')) {
        show_package_breakdown = localStorage.getItem('displayViewFolioTransaction');
    }


    getApi('reservation.get_folio_transaction', {
        transaction_type: props.doctype,
        transaction_number: props.transaction_number ? props.transaction_number : selectedFolio.value.name,
        show_package_breakdown: show_package_breakdown,
        city_ledger_invoice: props.cityLedgerInvoice
    })
        .then((result) => {
            folioTransactions.value = result.message
        })
    setTimeout(function () {
        getFolioSummary()
    }, 2000)
}



function getFolioSummary() {
    let show_package_breakdown = 0
    if (localStorage.getItem('displayViewFolioTransaction')) {
        show_package_breakdown = localStorage.getItem('displayViewFolioTransaction');
    }
    getApi("reservation.get_folio_summary_by_transaction_type", {
        transaction_type: "Reservation Folio",
        transaction_number: selectedFolio.value.name,
        show_package_breakdown: show_package_breakdown
    }).then((result) => {
        folio_summary.value = result.message
    })
}


const toggle = (event) => {
    show.value.toggle(event)
}





const moment = inject("$moment")

const rowStyleClass = (r) => {
    var classRow = ''

    if (!r.name) {
        classRow = classRow + "ui-helper-hidden "
    } else {

        if (r.debit > 0) {
            classRow = classRow + ("row-debit ")
        }
        else if (r.credit > 0) {
            classRow = classRow + ("row-credit ")
        }
    }

    return classRow
};


function onOpenLink(action, name) {

    window.postMessage(action + '|' + name, '*')
}


const onViewFolioDetail = (doc) => {
    if (doc.data.name) {
        window.postMessage("view_folio_transaction_detail|" + doc.data.name, '*')

    }

}

const totalCredit = computed(() => {


    if (folioTransactions.value) {

        return folioTransactions.value.reduce((n, d) => n + (d.credit || 0), 0)

    }
    return 0

})

const totalQuantity = computed(() => {
    if (folioTransactions.value) {
        return folioTransactions.value.reduce((n, d) => n + (d.quantity || 0), 0)

    }
    return 0

})

const totalDebit = computed(() => {
    if (folioTransactions.value) {

        return folioTransactions.value.reduce((n, d) => n + (d.debit || 0), 0)



    }
    return 0

})

const totalBalance = computed(() => {
    return selectedFolio.value.total_debit - selectedFolio.value.total_credit;
});


const windowActionHandler = async function (e) {
    if (e.isTrusted) {
        if (e.data.action == "load_folio_transaction") {

            LoadFolioTransaction()


        }

    }
}
onMounted(() => {

    if (window.isMobile) {
        let elem = document.querySelectorAll(".p-dialog");
        if (elem) {
            elem = elem[elem.length - 1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', windowActionHandler, false);

    LoadFolioTransaction()
    //load stay from storate 
    let state = sessionStorage.getItem('folo_transaction_table_state_' + selectedFolio.value.name)
    if (state) {
        state = JSON.parse(state)
        state.first = 0
        sessionStorage.setItem('folo_transaction_table_state_' + selectedFolio.value.name, JSON.stringify(state))


    }

})
function clearState(name) {

    let state = sessionStorage.getItem("folo_transaction_table_state_" + name)
    if (state) {
        state = JSON.parse(state)
        state.selection = []
        sessionStorage.setItem("folo_transaction_table_state_" + name, JSON.stringify(state))
    }
}

onUnmounted(() => {
    window.removeEventListener('message', windowActionHandler, false);
    clearState(selectedFolio.name)
})
</script>
<style>
.ui-helper-hidden .p-selection-column .p-checkbox {
    display: none !important;
}

.link_line_action1.auto_post {
    border-bottom: 1px dashed #ff3720 !important;
    color: #ff3720 !important;
}
</style>