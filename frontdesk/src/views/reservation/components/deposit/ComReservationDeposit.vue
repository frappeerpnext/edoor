<template>
     
    <Button v-for="(d, index) in setting?.account_group.filter(r => r.show_in_deposit_tab==1)" :key="index"
        @click="onAddFolioTransaction(d)" class="conten-btn mr-1 my-2">Post {{ d.account_name }}</Button>

    <ComReservationDepositTransactionCreditDebitStyle v-if="setting.folio_transaction_style_credit_debit == 1" />
    <ComReservationDepositTransactionSimpleStyle v-else />

</template>
<script setup>
import { inject, ref, computed, useToast,useConfirm,useDialog } from '@/plugin';
import ComReservationDepositTransactionCreditDebitStyle from "@/views/reservation/components/deposit/ComReservationDepositTransactionCreditDebitStyle.vue"
import ComReservationDepositTransactionSimpleStyle from "@/views/reservation/components/deposit/ComReservationDepositTransactionSimpleStyle.vue"
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"

import Tooltip from 'primevue/tooltip';

const setting = JSON.parse(localStorage.getItem("edoor_setting")) 


const toast = useToast();
const dialog = useDialog();
const confirm = useConfirm();
const rs = inject("$reservation")
const moment = inject("$moment")
const gv = inject("$gv")

 
function onAddFolioTransaction(account_code) {
 
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                new_doc:{
                    transaction_type:"Reservation",
                    transaction_number:rs.reservation.name,
                    reservation:rs.reservation.name,
                    property: rs.reservation.property,
                    account_group:account_code.name
                },
                balance:  Math.abs( rs.getDepositBalance())
            },
            props: {
                header: 'Post ' + account_code.account_name,
                style: {
                    width: '50vw',
                },

                modal: true,
                position: "top",
                closeOnEscape: false
            },
            onClose: (options) => {
                const data = options.data;

                if (data) {
                    
                    rs.getDepositTransaction(rs.reservation.name)
                
                    // we use setime here is wait ting for update reservation summay finish

                    setTimeout(function () {

                        rs.LoadReservation(rs.reservation.name,false);
                        rs.getChargeSummary(rs.reservation.name)
                    }, 2000)
                    if ((data.show_print_preview || 0) == 1) {
                        if (data.print_format) {
                            showPrintPreview(data)
                        }
                    }
                }

            }
        })
    
       

  

}


</script>