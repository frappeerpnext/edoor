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
        <template #guest_name="{ item, index }">
           Type={{ item.guest_name }} 
        </template>
        <!-- <template #header_reservation_type="{ column }">
            <span style="color: blue">Res. Type </span>
    </template> -->
        <!-- <template #header_reservation_date="{ column }">
            <span style="color: red">Res. Date </span>
    </template> -->
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
            { "fieldname": "guest", },
            { "fieldname": "guest_name",is_hide:true },
            // { "fieldname": "arrival_date" },
            // { "fieldname": "departure_date" },
            // { "fieldname": "owner" ,fieldtype:"Data",label:"Owner" },
            // { "fieldname": "modified_by",fieldtype:"Data" ,label:"Modified"},
            // { "fieldname": "creation", fieldtype:"Datetime",label:"Creation"},
            // { "fieldname": "modified" ,fieldtype:"Datetime",label:"Last Modified"}
            // { "fieldname": "business_source",is_hide:true },
        ]
,
    //    filterOptions:[
    //     {
    //         fieldname:"reservation_date",
    //         label:"Reservation Date"
    //     },
    //     {
    //         fieldname:"guest",
    //     },

    //    ],
        filters:[['property','=',window.property_name]],
        // settingMenus:[
         
        //     {
        //         label: 'Refresh',
        //         icon: 'pi pi-refresh'
        //     },
        //     {
        //         label: 'Export',
        //         icon: 'pi pi-upload'
        //     }
        
        // ],
    //     contextMenuOptions:[
    //     {label: 'View', icon: 'pi pi-fw pi-search', command: () => alert("View")},
    //     {label: 'Delete', icon: 'pi pi-fw pi-times', command: () => alert("Delete")}
    // ]
    }

    // function onRowDoubleClick(data){
    //     onOpenLink("view_reservation_detail",data.name)
    // }
    function onOpenLink(action,name){
        window.postMessage(action + '|' +name,'*')
    }
</script>