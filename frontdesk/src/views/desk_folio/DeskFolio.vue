<template>
    <ComDocumentList 
    doctype="Desk Folio" 
    list_view_setting="deskfolio_list"
    :options="options"
     router_name="DeskFolio"
     @row-dblclick="onRowDoubleClick"
     >
        <template #name="{ item, index }">
            <Button   class="link_line_action1"
                                @click="onOpenLink('view_desk_folio_detail',item.name)" link>
                                {{ item.name }}
                                
                            </Button> 
        </template>
        <template #guest="{ item, index }">
           <Button   class="link_line_action1"
                                @click="onOpenLink('view_guest_detail',item.guest)" link>
                                {{ item.guest }} {{ item.guest_name }}
                                
                            </Button> 
        </template>
    </ComDocumentList>
</template>
<script setup>
    import ComDocumentList from "@/components/document/ComDocumentList.vue"
 
    const options  ={
       fields:[
            { "fieldname": "name",label:"Desk Folio #", fieldtype:"Data" },
            { "fieldname": "room_number", label: "Room"},
            { "fieldname": "reference_number" },
            { "fieldname": "room_type", label: "Room Type" },
            { "fieldname": "guest"},
            { "fieldname": "guest_name",is_hide:true},
            { "fieldname": "posting_date", label: "Desk Folio. Date"},
            { "fieldname": "total_debit", label: "Debit"},
            { "fieldname": "total_credit", label: "Credit" },
            { "fieldname": "balance" },
            { "fieldname": "owner", fieldtype:"Data", label:"Created By"},
            { "fieldname": "creation", fieldtype:"Datetime", label: "Creation"},
            { "fieldname": "status"},
        ]
,
       filterOptions:[
        {
           fieldname:"guest",
        },
        {
            fieldname:"status",
        },
        {
            fieldname:"room_type",
        },
        {
            fieldname:"room_number",
        },
        {
            fieldname:"posting_date",
        },

       ],
        filters:[['property','=',window.property_name]],
    }

    function onRowDoubleClick(data){
        onOpenLink("view_desk_folio_detail",data.name)
    }
    function onOpenLink(action,name){
        window.postMessage(action + '|' +name,'*')
    }
</script>