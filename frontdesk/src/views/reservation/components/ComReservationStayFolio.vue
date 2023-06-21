<template>
    <div class="grid mt-1">
        <div class="col-fixed pr-0" style="width: 250px;">
            <div class="h-full res-stay-folio-btn-site-bg">
                <div class="flex justify-content-between align-items-center flex-wrap p-2">
                    <span>Room Folio</span>
                    <Button class="btn-add-folio"><img :src="plus_svg" style="height: 13px;"></Button>
                </div>
                <Button :severity="item.name == selectedFolioNumber ? 'folio-active' : 'primary'" v-for="(item, index) in data"
                    :key="index" @click="onClick(item.name)" class="flex w-full btn-folio-name mr-1">
                    <span v-if="item.is_master == 1"><img :src="crown_svg" class="me-2" style="height: 13px;"></span>
                    <span class="flex flex-column align-items-start">
                        <span class="line-height-2">{{ item.name }}</span>
                        <span class="text-gray-600 line-height-2 font-italic text-sm" v-if="item.status == 'Closed'">Folio Closed</span>
                    </span>
                </Button>
                
            </div>
        </div>

        <div class="col-fixe my-2 px-0" style="margin-left:-1px"><div class="res-stay-folio-divider"></div></div>

        <div class="col">
            <div class="flex justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio" style="margin-bottom: 10px;">
                <div>
                    <Button v-for="(d, index) in setting?.account_group" :key="index" @click="onAddFolioTransaction(d)"
                    class="conten-btn mr-1">Post {{ d.account_name }}</Button>
                </div>
                <div>
                    <SplitButton class="spl__btn_cs sp mr-1" label="Print" icon="pi pi-print" :model="more_item_folio_stay" />
                    <SplitButton class="spl__btn_cs sp" label="Mores" icon="pi pi-list" :model="more_item_folio_stay" />
                </div>
            </div>

            <DataTable :value="folioTransactions" tableStyle="min-width: 50rem">

                <Column field="name" header="Name"></Column>
                <Column field="posting_date" header="Posting Date">
                    <template #body="slotProps">
                        <span>{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
                    </template>
                </Column>
                <Column field="cashier_shift" header="Cashier Shift "></Column>

                <Column field="account_name" header="Account Name " style="min-width: 160px;">
                    <template #body="slotProps">
                        {{ slotProps.data.account_code }} - {{ slotProps.data.account_name }}
                    </template>
                </Column>

                <Column field="amount" header="Debit(Charges)" class="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat v-if="slotProps.data.type == 'Debit'" :value="slotProps.data.amount" />
                    </template>
                </Column>
                <Column field="amount" header="Credit(Payments)" class="text-right" style="min-width: 70px;">
                    <template #body="slotProps">
                        <CurrencyFormat class="text-green-700" v-if="slotProps.data.type == 'Credit'"
                            :value="slotProps.data.amount" />
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
                        <button @click="onDeleteFolioTransaction(slotProps.data.name)"
                            v-if="!slotProps.data.parent_reference">Delete</button>
                    </template>
                </Column>
            </DataTable>
            total credit:
            <CurrencyFormat :value="totalCredit" /> total_debit
            <CurrencyFormat :value="totalDebit" /> balance:
            <CurrencyFormat :value="( totalDebit -totalCredit)" />


        </div>
    </div>
</template>

<script setup>
import crown_svg from '@/assets/svg/icon-crown.svg'
import plus_svg from '@/assets/svg/icon-add-plus-sign-purple.svg'
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed } from '@/plugin';
import Tooltip from 'primevue/tooltip';
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
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
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
    fields: ["name","status", "is_master"],
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

function onAddFolioTransaction(account_code) {

    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_number: selectedFolioNumber.value,
            account_group: account_code.name,
            balance : totalDebit.value - totalCredit.value
        },
        props: {
            header: 'Post ' + account_code.account_name,
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

const more_item_folio_stay = [
    {
        label: 'Update',
        icon: 'pi pi-refresh',
    },
    {
        label: 'Delete',
        icon: 'pi pi-times',
    },
    {
        label: 'Vue Website',
        icon: 'pi pi-external-link',
    },
    { label: 'Upload', icon: 'pi pi-upload', }
];


</script>