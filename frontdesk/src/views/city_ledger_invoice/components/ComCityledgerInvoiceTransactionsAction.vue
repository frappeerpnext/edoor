<template>
 <div class="flex gap-2">
                    <Button @click="onAddTransaction">Add Transaction</Button>
                <Button class=" conten-btn white-space-nowrap"  iconPos="right" type="button"
                label="Remove" @click="onremove" aria-haspopup="true" aria-controls="folio_menu" />
                </div>
</template>
<script setup>
import { ref, inject, useDialog, useConfirm, onMounted,   getDocument , getApi , postApi } from '@/plugin'
import ComSelectCityLedgerTransferTransaction from "@/views/city_ledger_invoice/components/ComSelectCityLedgerTransferTransaction.vue"
const selectedFolioTransactions = ref({})
const dialogRef = inject("dialogRef")
const dialog = useDialog()
import {i18n} from '@/i18n';
const dialogConfirm = useConfirm();
const { t: $t } = i18n.global;
const props = defineProps({
    data: Object,
})
function onremove(){
    dialogConfirm.require({
        message: 'Do you want to Remove this record from this Folio',
        header: 'Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
alert(234)
        }
    })
    selectedFolioTransactions.value = JSON.parse( sessionStorage.getItem("folo_transaction_table_state_" + props.data.name) ).selection
    

}
function onAddTransaction(){
    dialog.open(ComSelectCityLedgerTransferTransaction, {
        data: {
            city_ledger:props.data.city_ledger
        },
        props: {
            header: $t("Select city ledger transaction"),
            style: {
                width: '80vw',
            },

            modal: true,
            position: "top",
            closeOnEscape: false,
            breakpoints: {
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data.message;
            if (data) {
                alert("add to to folio transaction to city ledger invoice")
            }

        }
    })
}
</script>