<template>
    <Button @click="onAddCharge">Add Charge</Button>

    <Button>Add Payment</Button>
    <Button :severity="item.name == selectedFolioNumber ? 'warning' : 'primary'" v-for="(item, index) in data" :key="index"
        @click="onClick(item.name)">{{ item.name }} master: {{ item.is_master }}</Button>
    <DataTable :value="folioTransactionDetail" tableStyle="min-width: 50rem">
        <Column field="name" header="Name "></Column>
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
const selectedFolioNumber = ref("")

db.getDocList('Reservation Folio', {
    fields: ["name", "is_master"],
    filters: [['reservation_stay', '=', rs.reservationStay?.name]],
})
    .then((doc) => {
        data.value = doc
        const masterFolio = doc.find(r => r.is_master == 1)
        if (masterFolio == undefined) {
            if (doc.length > 0) {
                onClick(doc[0].name)
            }
        } else {
            onClick(masterFolio.name)
        }

    })
    .catch((error) => console.error(error));



function onClick(name) {
    selectedFolioNumber.value = name
    db.getDocList('Folio Transaction', {

        fields: [
            'name',
            'posting_date',
            'cashier_shift',
            'account_code',
            'account_name',
            'type',
            'amount'],
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
        data: {
            folio_number: selectedFolioNumber.value
        },
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