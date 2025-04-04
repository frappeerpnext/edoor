<template>
    <ComDocumentList
        doctype="Deposit Ledger"
        list_view_setting="deposit_ledger_list"
        router_name="DepositLedger"
        :options= "options"
        @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
    >
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
                {{ item.guest }}
            </button>
        </template>
        


    </ComDocumentList>

</template>

<script setup> 
import { ref } from "vue"
import ComDocumentList from "@/components/document/ComDocumentList.vue"


const options = {
    fields:[
        {fieldname: "name" , label: "Deposit #"},
        {fieldname: "posting_date" , label: "Posting Date"},
        {fieldname: "guest" , label: "Guest"},
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
        { fieldname: "property" },
        { fieldname: "room_number" },
        { fieldname: "room_type" },
        { fieldname: "status" }
    ],
}

const selectedRow = ref()

function onRowDblclick(event) {

    onOpenLink("view_deposit_ledger_detail", event.name)
}


function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
</script>

<!-- <template>
    <ComDocumentList 
        doctype="Deposit Ledger"
        list_view_setting="deposit_ledger_list"
        router_name="DepositLedger"
        :options= "options"
        @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
    >
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
                {{ item.guest }}
            </button>
        </template>
    

    </ComDocumentList>

</template>

<script setup> 
import ComDocumentList from "@/components/document/ComDocumentList.vue"


const options = {
    fields:[
        {fieldname: "name" , label: "Deposit #"},
        {fieldname: "posting_date" , label: "Posting Date"},
        {fieldname: "guest" , label: "Guest"},
        {fieldname: "room_number", label: "Room"},
        {fieldname: "room_type", label: "Room Type",is_hide:true},
        {fieldname: "total_debit" , label: "Debit"},
        {fieldname: "total_credit" , label: "Credit"},
        {fieldname: "balance" , label: "Balance"},
        {fieldname: "status" , label: "Status"},    
        {fieldname: "modified_by" , label: "Modified By"},     
        { fieldname: "modified", label: "Last Modified", fieldtype: "Datetime" }

    ],
    filters:[['property','=',window.property_name]],

}


const selectedRow = ref()

function onRowDblclick(event) {

    onOpenLink("view_deposit_ledger_detail", event.name)
}

function onOpenLink(action, name){
    window.postMessage(action + '|' + name, '*')

}

</script> -->