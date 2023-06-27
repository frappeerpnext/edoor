<template>
 
    <DataTable  v-model:selection="rs.selectedFolioTransactions"  :value="rs.folioTransactions" tableStyle="min-width: 50rem" :rowClass="rowStyleClass">
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
        <Column field="creation" header="Created"></Column>
        <Column >
            <template #body="slotProps" >
               <Button v-if="slotProps.data.name" @click="onViewFolioDetail( slotProps.data)">Detail</Button>
            </template>
        </Column>
    </DataTable>
    total_debit
    <CurrencyFormat :value="rs.totalDebit" /> 
    total credit:
    <CurrencyFormat :value="rs.totalCredit" /> balance:
    <CurrencyFormat :value="(rs.totalDebit - rs.totalCredit)" />
 
</template>
<script setup>

import { inject,ref,useDialog,computed} from '@/plugin';
 
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';

const dialog = useDialog();
 

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