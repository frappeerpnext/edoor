<template>
 <div class="flex gap-2 justify-content-end" >
    <!-- <BlockUI v-tippy="data.status == 'Closed' ? 'This City Ledger Invoice is Closed' : ''" :blocked="data.status == 'Closed'"> -->
        <tippy :content="data.status == 'Closed' ? $t('This City Ledger Invoice is Closed') : ''" placement="bottom">
            <Button :disabled="data.status == 'Closed'" class="conten-btn" @click="onAddTransaction">
                <i class="pi pi-download me-2" />
                Add Transaction</Button>
        </tippy>
    <!-- </BlockUI> -->
    
              
               
    <!-- <BlockUI v-tippy="data.status == 'Closed' ? 'This City Ledger Invoice is Closed' : ''" :blocked="data.status == 'Closed'"> -->
        <tippy :content="data.status == 'Closed' ? $t('This City Ledger Invoice is Closed') : ''" placement="bottom">
            <Button :disabled="data.status == 'Closed'" class="conten-btn white-space-nowrap" icon="pi pi-chevron-down" iconPos="right" type="button"
                label="Option" @click="toggle" aria-haspopup="true" aria-controls="folio_menu" /> 
        </tippy>
    <!-- </BlockUI>  -->
        <Menu ref="folio_menu" id="folio_menu" :popup="true">
            <template #end>
                    <button  @click="onremove()"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-upload" />
                        <span class="ml-2 ">{{ $t('Remove') }}</span>
                    </button>
                    <button  @click="Transfer()"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-upload" />
                        <span class="ml-2 ">{{ $t('Transfer Item') }}</span>
                    </button>
            </template>        
        </Menu>
</div>
</template>
<script setup>
import { ref, useDialog, useConfirm ,postData, useToast } from '@/plugin'
import ComSelectCityLedgerTransferTransaction from "@/views/city_ledger_invoice/components/ComSelectCityLedgerTransferTransaction.vue"
import ComCityLedgerInvoiceTransfer from "@/views/city_ledger_invoice/components/ComCityLedgerInvoiceTransfer.vue"
const folio_menu = ref(); 
const dialog = useDialog()
const toast = useToast();
import {i18n} from '@/i18n';
const dialogConfirm = useConfirm();
const { t: $t } = i18n.global;
const props = defineProps({
    data: Object,
})
const toggle = (event) => {
    folio_menu.value.toggle(event);
}
const selections = defineModel("selections")
function onremove(){
    if (selections.value.length>0) {
        dialogConfirm.require({
            message: 'Do you want to Remove this record from this City Ledger Invoice',
            header: $t('Confirmation'),
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
    }else{
        toast.add({
            severity: 'warn',
            detail: 'Please select records to remove', life: 3000
        });
    }
    
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
function Transfer(){
    dialog.open(ComCityLedgerInvoiceTransfer, {
        data: {
            city_ledger:props.data.city_ledger,
            name:props.data.name,
            selections:selections.value
        },
        props: {
            header: $t("Select city ledger transaction"),
            style: {
                width: '50vw',
            },

            modal: true,
            position: "top",
            closeOnEscape: false,
            breakpoints: {
                '960px': '50vw',
                '640px': '70vw'
            },
        },
       
    })
}
</script>