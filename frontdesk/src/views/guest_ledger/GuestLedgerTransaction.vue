<template>
    <ComDocumentList doctype="Folio Transaction" list_view_setting="foliotransaction_list" :options="options"
        router_name="GuestLedgerTransaction" @row-dblclick="onRowDoubleClick"
        title="Guest Ledger Transaction"
        >
         
        
        <template #guest="{ item, index }">
            <Button  v-if="item.guest_name" class="link_line_action1" @click="onOpenLink('view_guest_detail', item.guest)" link>
                {{ item.guest_name }}

            </Button>
        </template>
        <template #account_code="{ item, index }">
            {{ item.account_code }}-{{ item.account_name }}
        </template>
        <template #reservation_status="{ item, index }">
            <ComReservationStatus :statusName="item.reservation_status" />
        </template>
    </ComDocumentList>
</template>
<script setup>
import ComDocumentList from "@/components/document/ComDocumentList.vue"
const options = {
    fields: [
        { "fieldname": "name", label: "Folio Transaction", fieldtype: "Data",action:"view_folio_transaction_detail" },
        { "fieldname": "reservation", label: "Res. #",action:"view_reservation_detail" },
        { "fieldname": "reservation_stay", label: "Stay #",action:"view_reservation_stay_detail" },
        { "fieldname": "transaction_number", label: "Folio #",action:"view_reservation_folio_detail"  },
        { "fieldname": "transaction_type",   is_hide: true },
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
        {fieldname:"account_code",fieldtype:"Tree"},
        { fieldname: "reservation" },
        { fieldname: "reservation_stay" },
        { fieldname: "business_source" },
        { fieldname: "reservation_status" },

    ],
    filters: [
        ['property', '=', window.property_name],
        ['is_base_transaction', '=', 1],
        ['transaction_type','=','Reservation Folio']
    ],
 
}

function onRowDoubleClick(data) {
    onOpenLink("view_folio_transaction_detail", data.name)
}
function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}


</script>