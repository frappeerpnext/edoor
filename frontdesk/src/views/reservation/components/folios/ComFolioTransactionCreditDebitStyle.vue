<template>
    <ComPlaceholder text="There is no Folio transactions" :loading="loading" :isNotEmpty="folioTransactions.length > 0">
        <DataTable v-model:selection="selectedfolioTransactions" @row-dblclick="onViewFolioDetail"
            :value="folioTransactions" tableStyle="min-width: 50rem" :rowClass="rowStyleClass" paginator
            :stateKey="'folo_transaction_table_state_' + selectedFolio.name" :rows="10"
            :rowsPerPageOptions="[5, 10, 20, 50]" @row-select="onRowSelection" @row-unselect="onRowUnSelection">
            <div class="absolute bottom-6 left-4">
                <strong>Total Records: <span class="ttl-column_re">{{ folioTransactions.length }}</span></strong>
            </div>

            <Column selectionMode="multiple" headerStyle="width: 3rem" v-if="showCheckbox">

            </Column>
            <Column field="name" header="Name" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <button @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.name" class="link_line_action1">{{
                        slotProps.data?.name }}</button>
                </template>
            </Column>
            <Column field="room_number" header="Room #" headerClass="text-center" bodyClass="text-center"></Column>
            <Column field="posting_date" header="Post Date" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <span v-if="slotProps.data?.posting_date">{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY")
                    }}</span>
                </template>
            </Column>

            <Column field="account_name" header="Account Name " style="min-width: 160px;" />
            <Column field="quantity" header="QTY" headerClass="text-center" bodyClass="text-center">
                <template #body="slotProps">
                    <span v-if="slotProps.data.quantity > 0">{{ slotProps.data.quantity }}</span>
                </template>
            </Column>

            <Column field="debit" header="Debit(Charges)" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat v-if="slotProps.data.debit > 0" :value="slotProps.data.debit"
                        class="white-space-nowrap" />
                </template>
            </Column>
            <Column field="credit" header="Credit(Payments)" class="text-right" style="min-width: 70px;">
                <template #body="slotProps">
                    <CurrencyFormat v-if="slotProps.data.credit > 0" class="text-green-700 white-space-nowrap"
                        :value="slotProps.data.credit" />
                </template>
            </Column>
            <Column field="balance" header="Balance" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.balance" class="white-space-nowrap" />
                </template>
            </Column>

            <Column field="owner" header="Made By">
                <template #body="slotProps">
                    {{ slotProps.data.owner?.split("@")[0] }}
                </template>
            </Column>
            <Column field="creation" header="Created">
                <template #body="slotProps">
                    <span v-if="slotProps.data.creation">
                        <ComTimeago :date="slotProps.data.creation" />
                    </span>
                </template>
            </Column>
            
            <Column header="">
                <template #body="slotProps">
                    <div v-if="slotProps.data.name">
                        <ComReservationStayFolioTransactionAction :is-edit="true" :is-delete="false"
                            :data="slotProps.data" />
                    </div>
                </template>
            </Column>
            <ColumnGroup type="footer">
                <Row>
                    <Column footer="Total:" :colspan="showCheckbox ? 5 : 4" footerStyle="text-align:right" />
                    <Column footerStyle="text-align:center">
                        <template #footer>
                            {{ totalQuantity }}
                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>

                            <CurrencyFormat :value="selectedFolio.total_debit" />
                        </template>
                    </Column>

                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="selectedFolio.total_credit" />
                        </template>
                    </Column>
<!-- 
                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="totalBalance" />
                        </template>
                    </Column> -->


                    <Column footerStyle="text-align:right">
                        <template #footer>
                            <CurrencyFormat :value="(selectedFolio.total_debit - selectedFolio.total_credit)" />
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

import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioTransactionAction from '@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioTransactionAction.vue';

import Enumerable from 'linq'
const props = defineProps({
    folio: Object, doctype: {
        type: String,
        default: "Reservation Folio"
    },
    showCheckbox: {
        type: Boolean,
        default: true
    }
})
const selectedFolio = ref(props.folio)
const gv = inject('$gv');
const can_view_rate = window.can_view_rate;
const folioTransactions = ref([])
const selectedfolioTransactions = ref([])
const folio_summary = ref()

const dialog = useDialog();
const show = ref()

function onRowSelection(r) {

    selectedfolioTransactions.value.push(...folioTransactions.value.filter(x => x.parent_reference == r.data.name))

}
function onRowUnSelection(r) {

    selectedfolioTransactions.value = selectedfolioTransactions.value.filter(x => x.name || (x.parent_reference || "") != r.data.name)


}

watch(() => props.folio, (newValue, oldValue) => {
    selectedFolio.value = newValue

    LoadFolioTransaction()
    selectedfolioTransactions.value = []
})



//load data
function LoadFolioTransaction() {

    getApi('reservation.get_folio_transaction', {
        transaction_type: props.doctype,
        transaction_number: selectedFolio.value.name
    })
        .then((result) => {
            folioTransactions.value = result.message
        })
    setTimeout(function () {
        getFolioSummary()
    }, 2000)
}



function getFolioSummary() {
    getApi("reservation.get_folio_summary_by_transaction_type", {
        transaction_type: "Reservation Folio",
        transaction_number: selectedFolio.value.name
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
        if (r.is_auto_post) {
            classRow = classRow + ("auto-post ")
        }
        if (r.debit > 0) {
            classRow = classRow + ("row-debit ")
        }
        else if (r.credit > 0) {
            classRow = classRow + ("row-credit ")
        }
    }

    return classRow
};



const onViewFolioDetail = (doc) => {
    if (doc.data.name) {
        const dialogRef = dialog.open(ComFolioTransactionDetail, {
            data: {
                folio_transaction_number: doc.data.name
            },
            props: {
                header: 'Folio Transaction Detail - ' + doc.data.name,
                style: {
                    width: '50vw',
                },
                modal: true,
                position: 'top',
                closeOnEscape: false
            },
            onClose: (options) => {

            }
        });
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
</style>