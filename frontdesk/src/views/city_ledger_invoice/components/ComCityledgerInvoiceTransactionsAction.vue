<template>
 <div class="flex gap-2" >
    <BlockUI v-tippy="data.status == 'Closed' ? 'This City Ledger Invoice is Closed' : ''" :blocked="data.status == 'Closed'">
                    <Button @click="onAddTransaction">Add Transaction</Button>
    </BlockUI>
    <BlockUI v-tippy="data.status == 'Closed' ? 'This City Ledger Invoice is Closed' : ''" :blocked="data.status == 'Closed'">
                <Button class="h-full conten-btn white-space-nowrap"  iconPos="right" type="button"
                label="Remove" @click="onremove" aria-haspopup="true" aria-controls="folio_menu" />
    </BlockUI>
</div>
</template>
<script setup>
import { ref, inject, useDialog, useConfirm,postData } from '@/plugin'
import ComSelectCityLedgerTransferTransaction from "@/views/city_ledger_invoice/components/ComSelectCityLedgerTransferTransaction.vue"
const selectedFolioTransactions = ref({})

import BlockUI from 'primevue/blockui';

const dialogRef = inject("dialogRef")
const dialog = useDialog()
import {i18n} from '@/i18n';
const dialogConfirm = useConfirm();
const { t: $t } = i18n.global;
const props = defineProps({
    data: Object,
})
const selections = defineModel("selections")
function onremove(){
    dialogConfirm.require({
        message: 'Do you want to Remove this record from this Folio',
        header: 'Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: async () => { 
    const res = await postData(
        "city_ledger_invoice.remove_folio_transaction_from_invoice",
        {
            city_ledger_invoice: props.data.name,
            data: selections.value.map(t => t.name)
        },
        "",
        false,
        "edoor.edoor.doctype.city_ledger_invoice."
    );

    if (res.data) {
        window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
    }
}

    })
    
}
function onAddTransaction(){
    dialog.open(ComSelectCityLedgerTransferTransaction, {
        data: {
            city_ledger:props.data.city_ledger,
            name:props.data.name
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
       
    })
}
</script>