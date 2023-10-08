<template>
 
    <ComPlaceholder 
        text="There is no Folio transactions" 
        :loading="loading" 
        :isNotEmpty="rs.folioTransactions.length > 0">

    <DataTable 
        v-model:selection="rs.selectedFolioTransactions"
        @row-dblclick="onViewFolioDetail" :value="rs.folioTransactions" 
 
        tableStyle="min-width: 50rem" 
            :rowClass="rowStyleClass"
            paginator  
            :stateKey="'folo_transaction_credit_debit_table_state_' + rs.selectedFolio.name"
            :rows="10" 
            :rowsPerPageOptions="[5, 10, 20, 50]"
        >
            <div class="absolute bottom-6 left-4">
                    <strong>Total Records: <span class="ttl-column_re">{{ rs.folioTransactions?.length }}</span></strong>
                </div>
            
        <Column selectionMode="multiple" headerStyle="width: 3rem">
            
        </Column>
        <Column field="name" header="Name" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <button @click="onViewFolioDetail(slotProps)" v-if="slotProps.data?.name" class="link_line_action1">{{slotProps.data?.name}}</button>
            </template>
        </Column>
        <Column field="room_number" header="Room #" headerClass="text-center" bodyClass="text-center"></Column>
        <Column field="posting_date" header="Post Date" headerClass="text-center" bodyClass="text-center">
            <template #body="slotProps">
                <span v-if="slotProps.data?.posting_date">{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
            </template>
        </Column>

        <Column field="account_name" header="Account Name " style="min-width: 160px;"/>

        <Column field="debit" header="Debit(Charges)" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat v-if="slotProps.data.debit>0" :value="slotProps.data.debit" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="credit" header="Credit(Payments)" class="text-right" style="min-width: 70px;">
            <template #body="slotProps">
                <CurrencyFormat  v-if="slotProps.data.credit>0" class="text-green-700 white-space-nowrap" 
                    :value="slotProps.data.credit" />
            </template>
        </Column>
        <Column field="balance" header="Balance" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.balance" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="owner" header="Made By"></Column>
        <Column field="creation" header="Created">
            <template #body="slotProps">
                <span v-if="slotProps.data.creation">{{ gv.datetimeFormat(slotProps.data.creation) }}</span>
            </template>
        </Column>
        <Column header="">
            <template #body="slotProps" >
                <div v-if="slotProps.data.name"> 
                    <ComReservationStayFolioTransactionAction :is-edit="true" :is-delete="false" :data="slotProps.data"/>
                </div>
            </template>
        </Column>
    </DataTable>

    <div v-if="can_view_rate" class="w-full flex justify-content-end my-2" id="detl_foloi">
        <div class="w-30rem">
            <div v-for="(item, index) in rs?.folio_summary" :key="index" class="flex mt-2 gap-2">
                <ComBoxStayInformation :title="item?.account_category || 'Undefine'" :value="item?.amount || 0" isCurrency
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Debit" :value="rs?.totalDebit"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Credit" :value="rs?.totalCredit"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>

            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Balance" :value="(rs?.totalDebit - rs?.totalCredit)"
                    valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="col font-semibold">
                </ComBoxStayInformation>
            </div>
        </div>
    </div>
</ComPlaceholder> 
</template>
<script setup>

import { inject,ref,useDialog,computed,onUnmounted} from '@/plugin';
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayFolioTransactionAction from './ComReservationStayFolioTransactionAction.vue';
import ComReservationStayTransportationLabel from '../ComReservationStayTransportationLabel.vue';
const gv = inject('$gv');
const can_view_rate=window.can_view_rate;
const dialog = useDialog();
const show = ref()
 
const toggle = (event) => {
    show.value.toggle(event)
}

 
const rs = inject('$reservation_stay');
const moment = inject("$moment")
 
const rowStyleClass = (r) => {
    var classRow = ''
 
    if(!r.name){
        classRow = classRow + "ui-helper-hidden "
    }else{
        if(r.is_auto_post){
            classRow = classRow + ("auto-post ")
        }
        if (r.debit > 0){
            classRow = classRow + ("row-debit ")
        }
        else if(r.credit > 0){
            classRow = classRow + ("row-credit ")
        }
    }
    
    return classRow
};

 

const onViewFolioDetail = (doc) => { 
    if (doc.data.name){
        const dialogRef = dialog.open(ComFolioTransactionDetail, {
            data:{
                folio_transaction_number:doc.data.name
            },
            props: {
                header: 'Folio Transaction Detail - ' + doc.data.name ,
                style: {
                    width: '50vw',
                },
                modal: true,
                position:'top',
                closeOnEscape: false
            },
            onClose: (options) => {
                
            }
        });
    }
     
}
 
</script>
<style>
    .ui-helper-hidden .p-selection-column .p-checkbox{
        display: none !important;
    }
    /*#detl_foloi div.w-30rem div.flex.mt-2.gap-2:nth-child(4) .box-input span{
        color: var(--green-700) !important;
    }*/
</style>