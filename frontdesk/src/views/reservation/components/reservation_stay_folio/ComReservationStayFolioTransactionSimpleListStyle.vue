<template>
    <DataTable :value="rs.folioTransactions" tableStyle="min-width: 50rem">

        <Column field="name" header="No. "></Column>
        <Column field="posting_date" header="Date">
            <template #body="slotProps">
                <span>{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
            </template>
        </Column>
        <Column field="account_name" header="Account" style="min-width: 160px;">
            <template #body="slotProps">
                {{ slotProps.data.account_code }} - {{ slotProps.data.account_name }}
            </template>
        </Column>
        <Column field="quantity" header="Qty" class="text-right"></Column>
        <Column field="amount" header="Price" class="text-right" style="min-width: 70px;">
            <template #body="slotProps">
                <CurrencyFormat v-if="slotProps.data.type == 'Credit'" :value="slotProps.data.amount" />
            </template>
        </Column>
        <Column field="discount" header="Discount" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.discount" />
            </template>
        </Column>
        <Column field="total_tax" header="Tax" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.total_tax" />
            </template>
        </Column>
        <Column field="total_amount" header="Amount" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.total_amount" />
            </template>
        </Column>
        <Column field="note" header="Note">
            <template #body="slotProps">
                <div v-if="slotProps.data.note" v-tooltip.top="slotProps.data.note">
                    {{ slotProps.data.note.slice(0, 20) + (slotProps.data.note.length > 20 ? '...' : '') }}
                </div>
            </template>
        </Column>
        <Column header="">
            <template #body="slotProps">
                <button @click="onEditFolioTransaction(slotProps.data)"
                    v-if="!slotProps.data.parent_reference">Edit</button>

            </template>
        </Column>
        <Column header="">
            <template #body="slotProps">
                <button @click="onDeleteFolioTransaction(slotProps.data)"
                    v-if="!slotProps.data.parent_reference">Delete</button>
            </template>
        </Column>
    </DataTable>
    total credit:
    <CurrencyFormat :value="rs.totalCredit" /> total_debit
    <CurrencyFormat :value="rs.totalDebit" /> balance:
    <CurrencyFormat :value="(rs.totalDebit - rs.totalCredit)" />
</template>
<script setup>
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast } from '@/plugin';
import ComNote from '@/components/form/ComNote.vue'
const frappe = inject('$frappe');

const call = frappe.call();
const dialog = useDialog();
const confirm = useConfirm();
const rs = inject('$reservation_stay');
const moment = inject("$moment")
const toast = useToast();

function onEditFolioTransaction(data) {
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: data.name
        },
        props: {
            header: 'Edit Transaction - ' + data.account_code + ' - ' + data.account_name,
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;

            if (data) {
                rs.onLoadFolioTransaction(rs.selectedFolio.name)
            }
            // toast.add({ severity: 'success', summary: "Edit Transaction", detail: "Edit Transaction successfully", life: 3000 })
        }
    })
}

function onDeleteFolioTransaction(doc) {

    const dialogRef = dialog.open(ComNote, {
        props: {
            header: "Delete Folio Transaction - " + doc.name,
            style: {
                width: '350',
            },
            modal: true
        },
        onClose: (options) => {
            const data = options.data;

            if (data != undefined) {
                rs.loading = false;
                call
                    .delete('edoor.api.utils.delete_doc', { doctype: "Folio Transaction", name: doc.name, note: data })
                    .then((result) => {
                        rs.onLoadFolioTransaction(rs.selectedFolio.name)
                        rs.loading = false;
                        toast.add({ severity: 'success', summary: "Delete Folio Transaction", detail: "Delete Folio Transaction successfully", life: 3000 })
                    }
                    )


            }
        }
    })


}


</script>