<template>
 
    <DataTable :value="rs.folioTransactions" tableStyle="min-width: 50rem" >

        <Column field="name" header="Name"></Column>
        <Column field="room_number" header="Room"></Column>
        <Column field="posting_date" header="Posting Date">
            <template #body="slotProps">
                <span v-if="slotProps.data?.posting_date">{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
            </template>
        </Column>

        <Column field="account_name" header="Account Name " style="min-width: 160px;"/>

        <Column field="debit" header="Debit(Charges)" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat v-if="slotProps.data.debit>0" :value="slotProps.data.debit" />
            </template>
        </Column>
        <Column field="credit" header="Credit(Payments)" class="text-right" style="min-width: 70px;">
            <template #body="slotProps">
                <CurrencyFormat  v-if="slotProps.data.credit>0" class="text-green-700" 
                    :value="slotProps.data.credit" />
            </template>
        </Column>
        <Column field="balance" header="Balance" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.balance" />
            </template>
        </Column>
        <Column field="owner" header="By"></Column>
        <Column field="creation" header="Created"></Column>
    </DataTable>
    total_debit
    <CurrencyFormat :value="rs.totalDebit" /> 
    total credit:
    <CurrencyFormat :value="rs.totalCredit" /> balance:
    <CurrencyFormat :value="(rs.totalDebit - rs.totalCredit)" />
</template>
<script setup>

import { inject  } from '@/plugin';
const rs = inject('$reservation_stay');
const moment = inject("$moment")
</script>