<template lang="">
    <div> 
  
    <div class="flex items-center justify-end">
        <div class="res_btn_st">
            <Button class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded icon="pi pi-ellipsis-v"
                @click="toggle"></Button>
        </div>
        <Menu :model="menus" :popup="true" ref="show" style="min-width: 180px;">
            <template #end>
                <button v-if="data.print_format" @click="onPrintFolioTransaction"
                    class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    {{$t('Print')}}
                    
                </button>
                <button v-if="data.name" @click="onViewFolioDetail"
                    class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    {{$t('View Detail')}}
                </button>
                <template v-if="isEdit">
                    <button @click="onEditFolioTransaction()"
                        v-if="!data.parent_reference"
                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        {{$t('Edit')}}
                    </button>
                </template>
                <template v-if="isDelete">
                    <button @click="onOpenDelete"
                        v-if="!data.parent_reference"
                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        {{$t('Delete')}} 
                    </button>
                </template>
            </template>
        </Menu>
    </div>
    </div>
    
</template>
<script setup>
import { ref, useDialog, inject, useConfirm, deleteApi } from '@/plugin'
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Enumerable from 'linq'
import {i18n} from '@/i18n';
const props = defineProps({
    data: Object,
    isEdit: {
        type: Boolean,
        default: true
    },
    isDelete: {
        type: Boolean,
        default: true
    }
})
const dialog = useDialog()
const show = ref()
const loading = ref()
const opDelete = ref(false)
const toggle = (event) => {
    show.value.toggle(event)
}

function onEditFolioTransaction() {
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: props.data.name,
            reservation:props.data.reservation
        },
        props: {
            header: 'Edit Folio Transaction - ' + props.data.name,
            style: {
                width: '60vw',
            },
            modal: true,
            position:'top',
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                //load folio list and folio transaction 
 
                window.postMessage({action:"load_reservation_folio_list"},"*")
                window.postMessage({action:"load_reservation_stay_folio_list"},"*")
                window.postMessage({action:"load_folio_transaction"})


            }

        }
    })
}
const onViewFolioDetail = () => {

    const dialogRef = dialog.open(ComFolioTransactionDetail, {
        data: {
            folio_transaction_number: props.data.name
        },
        props: {
            header: 'Folio Transaction Detail - ' + props.data.name,
            style: {
                width: '90vw',
            },
            modal: true,
            position:'top',
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },

    });

}
function onPrintFolioTransaction() {
    console.log(props.data.print_format)

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            doctype: "Folio Transaction",
            name: props.data.name,
            report_name: props.data.print_format,
        },
        props: {
            header: 'Print Preview',
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    })
}

function onOpenDelete() {
   
    const dialogRef = dialog.open(ComDialogNote, {
        data: {
                api_url: "utils.delete_doc",
                method: "DELETE",
                confirm_message: "Are you sure you want to delete this folio?",
                data:{ doctype: "Folio Transaction", name: props.data.name },
            },
        props: {
            header: "Delete Folio Transaction" + " " + props.data.name,
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: false,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            if(options.data){
                window.postMessage({action:"load_reservation_folio_list"},"*")
                window.postMessage({action:"load_reservation_stay_folio_list"},"*")
                window.postMessage({action:"load_folio_transaction"},"*") 
                window.postMessage({action:"ComDeskFolioDetail"},"*")
            }
            
            loading.value = false;
            opDelete.value = false     
         }
    });
}
</script>
<style lang="">
    
</style>