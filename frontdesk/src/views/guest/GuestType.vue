<template>
    <ComDocumentList
        doctype="Customer Group" 
        list_view_setting="guest_type_list"
        router_name="GuestType"
        :options="options"
        @row-dblclick="onRowDblclick"
        v-model:selectedRow="selectedRow"
        >

        <template #action-button>
            <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New Guest Type') " icon="pi pi-plus" @click="onAddNewGuestType" />
        </template> 
 
 
        <template #action="{ item }" >
                <div class="flex gap-2 justify-end">
                    <Button
                    @click="onEdit(item)"
                    icon="pi pi-pencil text-sm"
                    class="h-2rem border-none"
                    :label="$t('Edit')"
                    rounded
                    />
                    <Button
                    @click="onDelete(item.name)"
                    severity="danger"
                    icon="pi pi-trash text-sm"
                    class="h-2rem border-none"
                    :label="$t('Delete')"
                    rounded
                    />
                </div>
        </template>

    </ComDocumentList>
    
</template>

<script setup> 
import {ref,useDialog, useConfirm, deleteDoc} from "@/plugin"
import ComDocumentList from "@/components/document/ComDocumentList.vue"
import ComAddGuestType from "@/views/guest/components/ComAddGuestType.vue"
import { i18n } from '@/i18n'


const dialog = useDialog()
const selectedRow = ref()
const { t: $t } = i18n.global
const confirm = useConfirm()

 const options = ref({
        fields:[
            {fieldname: "name", is_hide:true},
            {fieldname: "name as customer_group_en", label: "Guest Type"},
            {fieldname: "note"},
            {fieldname: "modified", label: "Modified", fieldtype:"Datetime"},
            {fieldname: "modified_by", label: "Modified By"},

            {fieldname: "name as action", label:"Action",custom_class:"text-right" },
        ]
    })


function onDelete(name) {
    confirm.require({
        message: $t('Are you sure you want to delete guest type?'),
        header: $t('Confirmation'),
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleteDoc('Customer Group', name)
            .then(() => {
                window.postMessage({action:"ComDocumentList"},"*")
                loading.value = false
            }).catch((err) => {
                loading.value = false
            })
        },
    });
} 



function onEdit(edit) { 

    dialog.open(ComAddGuestType, {
        props: {
            header: `Edit Guest Type: ${edit.name}`,
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
        data: edit,
        
    });
} 

function onAddNewGuestType() {
    dialog.open(ComAddGuestType, {
        props: {
            header: $t(`Add New Guest Type`),
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
        
    });
}


</script>