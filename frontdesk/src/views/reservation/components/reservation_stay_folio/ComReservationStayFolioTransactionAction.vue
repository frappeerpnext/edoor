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
                    Print
                </button>
                <button v-if="data.name" @click="onViewFolioDetail"
                    class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    View Detail
                </button>
                <template v-if="isEdit">
                    <button @click="onEditFolioTransaction()"
                        v-if="!data.parent_reference"
                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        Edit
                    </button>
                    <button @click="onOpenDelete"
                        v-if="!data.parent_reference"
                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        Delete
                    </button>
                </template>
            </template>
        </Menu>
    </div>
    <ComDialogNote :header="`Delete Folio Transaction - ${data.name}`" :visible="opDelete" :loading="loading" @onOk="onDeleteFolioTransaction" @onClose="opDelete = false"/>
    </div>
    
</template>
<script setup>
import { ref, useDialog, inject, useConfirm, deleteApi } from '@/plugin'
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
const props = defineProps({
    data: Object,
    isEdit: {
        type: String,
        default: true
    }
})
const dialog = useDialog()
const show = ref()
const loading = ref()
const opDelete = ref(false)
const confirm = useConfirm();
const rs = inject('$reservation_stay')
const toggle = (event) => {
    show.value.toggle(event)
}

function onEditFolioTransaction() {
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: props.data.name
        },
        props: {
            header: 'Edit Folio Transaction - ' + props.data.name,
            style: {
                width: '50vw',
            },
            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                rs.onLoadReservationFolios()
                rs.onLoadFolioTransaction(rs.selectedFolio)
                rs.getChargeSummary(rs.reservationStay.name)
                setTimeout(function () {
                    rs.getReservationStay(rs.reservationStay.name);
                }, 2000)

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
                width: '50vw',
            },
            modal: true
        },

    });

}
function onPrintFolioTransaction() {

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            doctype: "Folio Transaction",
            name: props.data.name,
            report_name: props.data.print_format,
        },
        props: {
            header: 'Print PreviewXX',
            style: {
                width: '75vw',
            },
            position: "top",
            modal: true,
        },
    })
}
function onOpenDelete() {
    opDelete.value = true
}
function onDeleteFolioTransaction(note) {
    loading.value = true
    deleteApi('utils.delete_doc', { doctype: "Folio Transaction", name: props.data.name, note: note })
        .then((result) => {
            rs.onLoadReservationFolios()
            rs.onLoadFolioTransaction(rs.selectedFolio)
            setTimeout(function () {

                rs.getReservationStay(rs.reservationStay.name);
            }, 2000)
            rs.getChargeSummary(rs.reservationStay.name)
            loading.value = false;
            opDelete.value = false
        })

        .catch((error) => {
            loading.value = false
        })

}
</script>
<style lang="">
    
</style>