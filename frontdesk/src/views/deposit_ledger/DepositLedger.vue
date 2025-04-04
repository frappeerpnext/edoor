<template>
    <ComDocumentList
        doctype="Deposit Ledger"
        list_view_setting="deposit_ledger_list"
        router_name="DepositLedger"
        :options= "options"
        @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
    >
        <template #action-button>
            <Button class="border-none white-space-nowrap" :label="isMobile ? 'Add New ' : $t('Add New Deposit Ledger') " icon="pi pi-plus"
                    @click="onAddDepositLedger()" />
        </template>  

        <template #room_number="{ item, index }">
           {{ item.room_number }} {{ item.room_type }}
        </template>
        <template #status="{ item, index }">
           <ComStatus :status="item.status"/>
        </template>
        <template #name="{item, index}" >
            <button class="link_line_action1" @click="onOpenLink('view_deposit_ledger_detail', item.name)" link>
                {{ item.name }}
            </button>
        </template>
        <template #guest="{item, index}" >
            <button class="link_line_action1" @click="onOpenLink('view_guest_detail', item.guest)" link>
                {{ item.guest }} - {{ item.guest_name }}
            </button>
        </template>
        


    </ComDocumentList>

</template>

<script setup> 
import {ref} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue" 
import ComAddDepositLedger from '@/views/deposit_ledger/components/ComAddDepositLedger.vue';
import {i18n} from '@/i18n';
import { useDialog } from 'primevue/usedialog';


const dialog = useDialog()
const { t: $t } = i18n.global;


const options = {
    fields:[
        {fieldname: "name" , label: "Deposit #"},
        {fieldname: "posting_date" , label: "Posting Date"},
        {fieldname: "guest" , label: "Guest"},
        {fieldname: "guest_name" , label: "Guest Name", is_hide:true},
        {fieldname: "room_number", label: "Room"},
        {fieldname: "room_type", label: "Room Type",is_hide:true},
        {fieldname: "total_debit" , label: "Debit"},
        {fieldname: "total_credit" , label: "Credit"},
        {fieldname: "balance" , label: "Balance"},
        {fieldname: "status" , label: "Status"},    
        {fieldname: "modified_by" , label: "Modified By"},     
        { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" }

    ],
    filterOptions: [
        { fieldname: "guest" },
        { fieldname: "posting_date" },
        { fieldname: "room_type",fieldtype:'Link',options:"Room Type",optionValue:"label",operator:"like" },
        { fieldname: "room_number",fieldtype:'Link',options:"Room",optionValue:"label",operator:"like" }, 
        { fieldname: "status" }, 
    ], 
    filters:[['property','=',window.property_name]],
}

const selectedRow = ref()

function onRowDblclick(event) {

    onOpenLink("view_deposit_ledger_detail", event.name)
}


function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

function onAddDepositLedger(data) {
    dialog.open(ComAddDepositLedger, {
        data: { data },
        props: {
            header: $t(`Add New Deposit Ledger`),
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
            const data = options.data;
            if (data) {
                window.postMessage("view_deposit_ledger_detail|" + data.name,"*")
                setTimeout(() => {
                    window.postMessage({action:"ComDocumentList"},"*")
                }, 5000);
                
            }
        }
    });
}

</script>

