<template>
    <ComDocumentList doctype="Folio Transaction" list_view_setting="foliotransaction_list" :options="options"
        router_name="FolioTransaction" @row-dblclick="onRowDoubleClick">
        <template #name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_folio_transaction_detail', item.name)" link>
                {{ item.name }}

            </Button>
        </template>
        <template #reservation="{ item, index }">
            <Button v-if="item.reservation" class="link_line_action1" @click="onOpenLink('view_reservation_detail', item.reservation)" link>
                {{ item.reservation }}

            </Button>
        </template>
        <template #reservation_stay="{ item, index }">
            <Button  v-if="item.reservation_stay" class="link_line_action1" @click="onOpenLink('view_reservation_stay_detail', item.reservation_stay)"
                link>
                {{ item.reservation_stay }}

            </Button>
        </template>
        <template #transaction_number="{ item, index }">

            <Button  class="link_line_action1" @click="onOpenLink(getTransactionTypeViewDetail(item.transaction_type), item.transaction_number)" link>
                {{ item.transaction_type == 'City Ledger'? item.city_ledger_name : item.transaction_number }}

            </Button>
            

        </template>
        <template #guest="{ item, index }">
            <Button  v-if="item.guest_name" class="link_line_action1" @click="onOpenLink('view_guest_detail', item.guest)" link>
                {{ item.guest_name }}

            </Button>
        </template>
        <template #account_code="{ item, index }">
            {{ item.account_code }}-{{ item.account_name }}
        </template>
    </ComDocumentList>
</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
const options = {
    fields: [
        { "fieldname": "name", label: "Folio Transaction", fieldtype: "Data" },
        { "fieldname": "reservation", label: "Reservation #" },
        { "fieldname": "reservation_stay", label: "Stay #" },
        { "fieldname": "transaction_number", label: "Folio #" },
        { "fieldname": "transaction_type", label: "Folio #", is_hide: true },
        { "fieldname": "city_ledger_name", label: "city_ledger",is_hide:true },
        { "fieldname": "room_number", label: "Rooms" },
        { "fieldname": "guest", label: "Guest" },
        { "fieldname": "guest_name", is_hide: true},
        { "fieldname": "account_code", label: "Account Code" },
        { "fieldname": "account_name", is_hide: true },
        { "fieldname": "price" },
        { "fieldname": "discount" },
        { "fieldname": "total_tax" },
        { "fieldname": "bank_fee_amount" },
        { "fieldname": "total_amount" },
        { "fieldname": "modified_by", fieldtype: "Data", label: "Modified By" },
        { "fieldname": "modified", fieldtype: "Datetime", label: "Last Modified" },
    ]
    ,
    filterOptions: [
        { fieldname: "posting_date" },
        { fieldname: "transaction_type", label: "Ledger Type", options: "Ledger Type" },
        { fieldname: "reservation" },
        { fieldname: "reservation_stay" },
        { fieldname: "business_source" },

    ],
    filters: [
        ['property', '=', window.property_name],
        ['is_base_transaction', '=', 1]
    ],
 
}

function onRowDoubleClick(data) {
    onOpenLink("view_folio_transaction_detail", data.name)
}
function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

function getTransactionTypeViewDetail(transaction_type){
    if(transaction_type == "Reservation Folio"){
        return "view_reservation_folio_detail"
    }else if (transaction_type == "City Ledger"){
    return "view_city_ledger_detail"
    }else if (transaction_type == "Cashier Shift"){
    return "view_cashier_shift_detail"
    }else if (transaction_type == "Deposit Ledger"){
    return "view_deposit_ledger_detail"
    }else if (transaction_type == "Desk Folio"){
    return "view_desk_folio_detail"
    }else if (transaction_type == "Payable Ledger"){
    return "view_payable_ledger_detail"
    }
}
</script>