<template>
    <Button @click="onAddCharge">Add Charge</Button>
    <Button>Add Payment</Button>

    <Button v-for="(item, index) in data" :key="index" @click="onClick(item.name)">{{ item.name }}</Button>
    <DataTable :value="folioTransactionDetail" tableStyle="min-width: 50rem">
        <Column field="posting_date" header="Posting Date">
            <template #body="slotProps">
                <span>{{ moment(slotProps.folioTransactionDetail?.posting_date).format("DD/MM/YYYY") }}</span>
            </template>
        </Column>
        <Column field="cashier_shift" header="Cashier Shift "></Column>
        <Column field="account_code" header="Account Code "></Column>
        <Column field="account_name" header="Account Name "></Column>
        <Column field="type" header="Account Type "></Column>
        <Column field="amount" header="Amount"></Column>
    </DataTable>
</template>
<script setup>
import { inject, ref } from '@/plugin';
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
const frappe = inject('$frappe')
const rs = inject("$reservation_stay")
const moment = inject("$moment")
const data = ref([])
const folioTransactionDetail = ref([])
const db = frappe.db();
const dialog = useDialog();

db.getDocList('Reservation Folio', {
    filters: [['reservation_stay', '=', rs.reservationStay?.name]],
})
    .then((doc) => {
        data.value = doc
    })
    .catch((error) => console.error(error));



function onClick(name) {

    db.getDocList('Folio Transaction', {

        fields: ['posting_date'],
        fields: ['cashier_shift'],
        fields: ['account_code'],
        fields: ['account_name'],
        fields: ['type'],
        fields: ['amount'],

        filters: [
            ['folio_number', '=', name]
        ]
    })
        .then((doc) => {
            folioTransactionDetail.value = doc
        })
        .catch((error) => console.error(error));
}

function onAddCharge() {

    const dialogRef = dialog.open(ComAddFolioTransaction, {
        props: {
            header: 'Add Change',
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                console.log(data)
            }
        }
    })
}

</script>