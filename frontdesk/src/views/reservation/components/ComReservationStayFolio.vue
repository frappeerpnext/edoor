<template>
   
<div class="flex mt-2">
    <div>
        <Button :severity="item.name == selectedFolioNumber ? 'warning' : 'primary'" v-for="(item, index) in data" :key="index"
        @click="onClick(item.name)" class="border-none w-full">
        <img v-if="item.is_master == 1" :src="crown_svg" class="me-2" style="height: 13px;"> {{ item.name }}
    </Button>

    </div>
    <div class="flex-grow-1">
        <Button @click="onAddCharge" class="border-none">Post Charge</Button>
    <Button class="border-none">Post Payment</Button>
        
        <DataTable :value="folioTransactions" tableStyle="min-width: 50rem">

            <Column field="name" header="Name"></Column>
            <Column field="posting_date" header="Posting Date">
                <template #body="slotProps">
                    <span>{{ moment(slotProps.data?.posting_date).format("DD/MM/YYYY") }}</span>
                </template>
            </Column>
            <Column field="cashier_shift" header="Cashier Shift "></Column>

            <Column field="account_name" header="Account Name ">
                <template #body="slotProps">
                    {{ slotProps.data.account_code }} - {{ slotProps.data.account_name }}
                </template>
            </Column>

            <Column field="amount" header="Debit(Charges)" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat v-if="slotProps.data.type == 'Debit'" :value="slotProps.data.amount" />
                </template>
            </Column>
            <Column field="amount" header="Credit(Payments)" class="text-right">
                <template #body="slotProps" >
                    <CurrencyFormat class="text-green-700" v-if="slotProps.data.type == 'Credit'" :value="slotProps.data.amount" />
                </template>
            </Column>
            <Column field="balance" header="Balance" class="text-right">
                <template #body="slotProps">
                    <CurrencyFormat :value="slotProps.data.balance" />
                </template>
            </Column>

</DataTable>
total credit:
<CurrencyFormat :value="totalCredit" /> total_debit
<CurrencyFormat :value="totalDebit" /> balance:
<CurrencyFormat :value="(totalCredit - totalDebit)" />
<br>


<DataTable :value="folioTransactions" tableStyle="min-width: 50rem">

<Column field="name" header="No. "></Column>
<Column field="posting_date" header="Date">
    <template #body="slotProps">
        <span>{{ moment(slotProps.data?.posting_date).format("DD/MM/YYYY") }}</span>
    </template>
</Column>
<Column field="account_name" header="Account">
    <template #body="slotProps">
        {{ slotProps.data.account_code }} - {{ slotProps.data.account_name }}
    </template>
</Column>
<Column field="quantity" header="Qty"></Column>
<Column field="amount" header="Price">
    <template #body="slotProps">
        <CurrencyFormat v-if="slotProps.data.type == 'Credit'" :value="slotProps.data.amount" />
    </template>
</Column>
<Column field="discount" header="Discount">
    <template #body="slotProps">
        <CurrencyFormat :value="slotProps.data.discount" />
    </template>
</Column>
<Column field="total_tax" header="Tax">
    <template #body="slotProps">
        <CurrencyFormat :value="slotProps.data.total_tax" />
    </template>
</Column>
<Column field="total_amount" header="Amount">
    <template #body="slotProps">
        <CurrencyFormat :value="slotProps.data.total_amount" />
    </template>
</Column>
<Column field="note" header="Note"></Column>
<Column header="">
    <template #body="slotProps">
        <button @click="onEditFolioTransaction(slotProps.data)"
            v-if="!slotProps.data.parent_reference">Edit</button>

    </template>
</Column>
<Column header="">
    <template #body="slotProps">
        <button @click="onDeleteFolioTransaction(slotProps.data.name)"
            v-if="!slotProps.data.parent_reference">Delete</button>
    </template>
</Column>
</DataTable>
total credit:
<CurrencyFormat :value="totalCredit" /> total_debit
<CurrencyFormat :value="totalDebit" /> balance:
<CurrencyFormat :value="(totalCredit - totalDebit)" />


    </div>
</div>
    
</template>
<script setup>
import crown_svg from '@/assets/svg/icon-crown.svg'
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed } from '@/plugin';

const dialog = useDialog();


const confirm = useConfirm();
const frappe = inject('$frappe')
const db = frappe.db();
const rs = inject("$reservation_stay")
const moment = inject("$moment")
const data = ref([])
const folioTransactions = ref([])
const selectedFolioNumber = ref("")
const gv = inject("$gv")


const totalCredit = computed(() => {

    if (folioTransactions.value) {
        const credit = folioTransactions.value.filter(r => r.type == 'Credit')

        if (credit) {
            return credit.reduce((n, d) => n + d.amount, 0)
        }

    }
    return 0

})
const totalDebit = computed(() => {
    if (folioTransactions.value) {
        const debit = folioTransactions.value?.filter(r => r.type == 'Debit')
        if (debit) {
            return debit.reduce((n, d) => n + d.amount, 0)
        }

    }
    return 0

})


db.getDocList('Reservation Folio', {
    fields: ["name", "is_master"],
    filters: [['reservation_stay', '=', rs.reservationStay?.name]],
    limit: 1000
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
    onLoadData(name)
}
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
                onLoadData(selectedFolioNumber.value)
            }
        }
    })
}

function onDeleteFolioTransaction(name) {
    confirm.require({
        message: 'Do you want to delete this record?',
        header: 'Delete Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'p-button-danger',
        accept: () => {
            //toast.add({ severity: 'info', summary: 'Confirmed', detail: 'Record deleted', life: 3000 });
            db.deleteDoc('Folio Transaction', name)
                .then((response) => {
                    onLoadData(selectedFolioNumber.value)
                }
                ) // Message will be "ok"
                .catch((error) => {
                    gv.showErrorMessage(error)
                });
        },

    });
}
function onLoadData(name) {
    selectedFolioNumber.value = name
    db.getDocList('Folio Transaction', {
        fields: [
            'name',
            'quantity',
            'note',
            'discount',
            'posting_date',
            'cashier_shift',
            'account_code',
            'account_name',
            'type',
            'amount',
            'parent_reference',
            'total_amount',
            'total_tax',
        ],
        filters: [
            ['folio_number', '=', name]
        ],
        limit: 1000
    })
        .then((doc) => {
            let balance = 0
            doc.forEach(r => {
                balance = balance + (r.amount * (r.type == 'Debit' ? 1 : -1))
                r.balance = balance
            });
            folioTransactions.value = doc
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
                onLoadData(selectedFolioNumber.value)
            }
        }
    })
}
</script>