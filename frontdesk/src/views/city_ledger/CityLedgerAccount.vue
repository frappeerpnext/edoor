<template>
<ComDocumentList doctype="City Ledger"
    list_view_setting="city_ledger_account_list"
    router_name="CityLedgerAccount"
    :options ="options"
>
<template #action-button>
      <Button
        class="border-none"
        :label="$t('New City Ledger Account')"
        icon="pi pi-plus"
        @click="onAddCityLedgerAccount"
      />
    </template>

<template #status="{ item, index }">
      <ComStatus :status="item.status" />
    </template>
</ComDocumentList>
</template>
<script setup>
import { inject, ref, useDialog,  } from '@/plugin'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const gv = inject("$gv")
// const toast = useToast()
const dialog = useDialog()


    const options = {
        fields:[
            {fieldname:"name",action:"view_city_ledger_detail"},
            {fieldname:"city_ledger_name"},
            {fieldname:"city_ledger_type"},
            {fieldname:"business_source"},
            {fieldname:"company_name"},
            {fieldname:"phone_number"},
            {fieldname:"contact_name"},
            {fieldname:"total_debit"},
            {fieldname:"total_credit"},
            {fieldname:"balance"},
            {fieldname:"status"},
            {fieldname:"owner",label:"Creatd By"},
            {fieldname:"creation",fieldtype:"Datetime",label:"Created Date"},
        ],
        filterOptions:[
            {fieldname:"city_ledger_type"},
            {fieldname:"business_source"},
            {fieldname:"status"}
        ],
        filters:[["property","=",window.property_name]]
    }

    
function onAddCityLedgerAccount() {
    if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
    dialog.open(ComAddCityLedgerAccount, {
        data: {
            // name: name.value,
        },
        props: {
            header: `Add New City Ledger Account`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            
        }
    });
}

</script>