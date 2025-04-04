<template>
    
    <ComDocumentList 
    doctype="Reservation" 
    list_view_setting="reservation_list"
    :options="options"
     router_name="ReservationList"
     @row-dblclick="onRowDoubleClick"
     v-model:selectedRow="selectedRow"
     >
        <template #name="{ item, index }">
            <Button   class="link_line_action1"
                                @click="onOpenLink('view_reservation_detail',item.name)" link>
                                {{ item.name }}
                                
                            </Button> 
        </template>
        <template #reservation_type="{ item, index }">
           Type={{ item.reservation_type }} 
        </template>
        <!-- <template #header_reservation_type="{ column }">
            <span style="color: blue">Res. Type </span>
    </template>
        <template #header_reservation_date="{ column }">
            <span style="color: red">Res. Date </span>
    </template> -->
    </ComDocumentList>
</template>
<script setup>
import {ref} from "@/plugin"

    import ComDocumentList from "@/components/document/ComDocumentList.vue"
    const selectedRow = ref()
    const options  ={
       fields:[
            { "fieldname": "name",label:"Res. #", fieldtype:"Data" },
            { "fieldname": "reservation_type",is_hide:true },
            { "fieldname": "guest_name" },
            { "fieldname": "business_source" },
            { "fieldname": "adr" },
            { "fieldname": "reservation_date" },
            { "fieldname": "arrival_date" },
            { "fieldname": "departure_date" },
            { "fieldname": "owner" ,fieldtype:"Data",label:"Owner" },
            { "fieldname": "modified_by",fieldtype:"Data" ,label:"Modified"},
            { "fieldname": "creation", fieldtype:"Datetime",label:"Creation"},
            { "fieldname": "modified" ,fieldtype:"Datetime",label:"Last Modified"}
        ]
,
       filterOptions:[
        {
            fieldname:"reservation_date",
            label:"Reservation Date"
        },
        {
            fieldname:"guest",
        },

       ],
        filters:[['property','=',window.property_name]],
        settingMenus:[
         
            {
                label: 'Refresh',
                icon: 'pi pi-refresh'
            },
            {
                label: 'Export',
                icon: 'pi pi-upload'
            }
        
        ],
        contextMenuOptions:[
            {label: 'View Reservation Detail', icon: 'pi pi-fw pi-search', command: () => onOpenLink("view_reservation_detail",selectedRow.value.name)},
            {label: 'Delete', icon: 'pi pi-fw pi-times', command: () => alert("Delete")}
        ]
    }
    
    function onRowDoubleClick(data){
        onOpenLink("view_reservation_detail",data.name)
    }
    function onOpenLink(action,name){
        window.postMessage(action + '|' +name,'*')
    }
</script>