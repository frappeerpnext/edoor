<template>
    <div class="flex mt-3 min-h-folio-cus" v-if="rs.folios?.length > 0">
        <ComResevationStayFolioList />
        <div class="col py-0 overflow-x-auto"> 
            <ComReservationStayFolioAction />
            <ComReservationStayFolioTransactionDebitCreditStyle v-if="setting.folio_transaction_style_credit_debit == 1" />
            <ComReservationStayFolioTransactionSimpleListStyle v-else />
        </div>
    </div>
    <div v-else class="min-h-folio-cus flex flex-column justify-content-center">
        <div class="text-center mb-3">
            <Button class="conten-btn" label="Create Folio" icon="pi pi-folder-open" @click="onAddCreatNewFolio()"></Button>
        </div>
        <div class="text-center text-600">Create a Folio to post transactions.</div>
    </div>
</template>

<script setup>

import ComResevationStayFolioList from "@/views/reservation/components/reservation_stay_folio/ComResevationStayFolioList.vue"
import ComReservationStayFolioAction from "@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioAction.vue"
import ComReservationStayFolioTransactionDebitCreditStyle from "@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioTransactionDebitCreditStyle.vue"
import ComReservationStayFolioTransactionSimpleListStyle from "@/views/reservation/components/reservation_stay_folio/ComReservationStayFolioTransactionSimpleListStyle.vue"
import ComNewReservationStayFolio from "@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast } from '@/plugin';
import Tooltip from 'primevue/tooltip';

const toast = useToast();
const dialog = useDialog();
const confirm = useConfirm();
const frappe = inject('$frappe')
const db = frappe.db();
const rs = inject("$reservation_stay")
const moment = inject("$moment")
const gv = inject("$gv")

const setting = JSON.parse(localStorage.getItem("edoor_setting"))

rs.onLoadReservationFolios()
    .then((doc) => {
        if (doc) {
            const masterFolio = doc.find(r => r.is_master == 1)
            if (masterFolio == undefined) {
                if (doc.length > 0) {
                    rs.onLoadFolioTransaction(doc[0])
                }
            } else {
                rs.onLoadFolioTransaction(masterFolio)
            }
        }
    })

function onAddCreatNewFolio() {

    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            reservation_stay: rs.reservationStay,
        },
        props: {
            header: 'Create New Folio ',
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                rs.onLoadReservationFolios().then(() => {
                    rs.onLoadFolioTransaction(data)
                })
            }
        }
    })
}

</script>