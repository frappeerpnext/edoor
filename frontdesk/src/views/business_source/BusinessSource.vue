<template>
    <ComDocumentList
      doctype="Business Source"
      list_view_setting="business_source_list"
      :options="options"
      @row-dblclick="onRowDoubleClick"
    > 
    <template #action-button>
        <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New Business Source') " icon="pi pi-plus"  @click="onAddNewBusinessSource" />
    </template>

        <template #name="{ item, index }">
            <Button class="link_line_action1" @click="onOpenLink('view_business_source_detail', item.name)" link>
                {{ item.name }}
            </Button>
        </template>
    </ComDocumentList>
  </template> 
<script setup> 
import {useDialog} from "@/plugin"
import ComAddBusinessSource from '@/views/business_source/components/ComAddBusinessSource.vue';


const dialog = useDialog()


const options = {
    fields: [
        { fieldname: "name", label: "Business Source" }, 
        { fieldname: "business_source_type", label: "Business Source Type" }, 
        { fieldname: "country", label: "Country" }, 
        { fieldname: "city", label: "City" }, 
        { fieldname: "contact_name", label: "Contact Name" }, 
        { fieldname: "phone_number", label: "Phone Number" }, 
        { fieldname: "email", label: "Email" }, 
    ],
    filterOptions: [
        { fieldname: "business_source_type" }, 
        { fieldname: "country" }, 
        { fieldname: "city" }, 
        { fieldname: "contact_name" }, 
        { fieldname: "phone_number" }, 
        { fieldname: "email" }, 
    ],     
}

function onRowDoubleClick(event) {
    onOpenLink("view_business_source_detail", event.name)
}

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
function onAddNewBusinessSource(){
    dialog.open(ComAddBusinessSource, {
        data:{
            // name: name.value,
            is_city_ledger: true
        },
        props: {
            header: `Add New Businese Source`,
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
        onClose:(options) => {
            const data = options.data;
            if(data){
				loadData(data.name)
			}
        }
    });  
}
</script>