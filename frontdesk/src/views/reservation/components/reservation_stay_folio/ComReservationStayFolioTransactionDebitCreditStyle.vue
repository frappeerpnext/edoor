<template>
    <ComPlaceholder text="There is no Folio transactions" :loading="loading" :isNotEmpty="rs.folio_summary.length > 0">
    <DataTable  v-model:selection="rs.selectedFolioTransactions"  :value="rs.folioTransactions" tableStyle="min-width: 50rem" :rowClass="rowStyleClass"
    paginator  
            stateKey="folo_transaction_credit_debit_table_state"
            :rows="10" :rowsPerPageOptions="[5, 10, 20, 50]"
    >
        <Column selectionMode="multiple" headerStyle="width: 3rem">
            
        </Column>
        <Column field="name" header="Name">

        </Column>
        <Column field="room_number" header="Room"></Column>
        <Column field="posting_date" header="Post Date">
            <template #body="slotProps">
                <span v-if="slotProps.data?.posting_date">{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
            </template>
        </Column>

        <Column field="account_name" header="Account Name " style="min-width: 160px;"/>

        <Column field="debit" header="Debit(Charges)" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat v-if="slotProps.data.debit>0" :value="slotProps.data.debit" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="credit" header="Credit(Payments)" class="text-right" style="min-width: 70px;">
            <template #body="slotProps">
                <CurrencyFormat  v-if="slotProps.data.credit>0" class="text-green-700 white-space-nowrap" 
                    :value="slotProps.data.credit" />
            </template>
        </Column>
        <Column field="balance" header="Balance" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.balance" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="owner" header="Made By"></Column>
        <Column field="creation" header="Created">
            <template #body="slotProps">
                <span v-if="slotProps.data.creation">{{ gv.datetimeFormat(slotProps.data.creation) }}</span>
            </template>
        </Column>
        <Column header="">
            <template #body="slotProps" >
                <div v-if="slotProps.data.name"> 
                    <ComReservationStayFolioTransactionAction :is-edit="false" :data="slotProps.data"/>
                </div>
            </template>
        </Column>
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


    <!-- <ul>
        <li v-for="(item, index) in rs.folio_summary" :key="index">{{item.account_category}} => {{item.amount}}</li>
    </ul> -->
    <!-- total_debit
    <CurrencyFormat :value="rs.totalDebit" /> 
    total credit:
    <CurrencyFormat :value="rs.totalCredit" /> balance:
    <CurrencyFormat :value="(rs.totalDebit - rs.totalCredit)" /> -->
</ComPlaceholder> 
</template>
<script setup>

import { inject,ref,useDialog,computed} from '@/plugin';
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioTransactionAction from './ComReservationStayFolioTransactionAction.vue';
const gv = inject('$gv');

const dialog = useDialog();
const show = ref()
 
const toggle = (event) => {
    show.value.toggle(event)
}

const rs = inject('$reservation_stay');
const moment = inject("$moment")
 
const rowStyleClass = (row) => {
 
    return row.name?"": "ui-helper-hidden";
};

const onViewFolioDetail = (doc) => {
 
    const dialogRef = dialog.open(ComFolioTransactionDetail, {
        data:{
            folio_transaction_number:doc.name
        },
        props: {
            header: 'Folio Transaction Detail - ' + doc.name ,
            style: {
                width: '50vw',
            },
            modal: true
        },
        onClose: (options) => {
            
        }
    });
     
}

</script>
<style>
.ui-helper-hidden .p-selection-column .p-checkbox{
    display: none !important;
}
</style>