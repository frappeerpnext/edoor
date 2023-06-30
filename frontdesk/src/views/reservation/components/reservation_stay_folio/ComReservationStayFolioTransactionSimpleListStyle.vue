<template>
    {{ rs.selectedFolio }}
<ComPlaceholder text="There is no Folio transactions" :loading="loading" :isNotEmpty="rs.folio_summary.length > 0">
    
    <DataTable v-model:selection="rs.selectedFolioTransactions"
        :value="rs.folioTransactions?.filter(r => (r.parent_reference || '') == '')" tableStyle="min-width: 120rem">
        <Column selectionMode="multiple" headerStyle="width: 3rem" />
        <Column field="name" header="No. "></Column>
        <Column field="posting_date" header="Date">
            <template #body="slotProps">
                <span>{{ moment(slotProps.data?.posting_date).format("DD-MM-YYYY") }}</span>
            </template>
        </Column>
        <Column field="account_name" header="Account" style="min-width: 160px;">
            <template #body="slotProps">
                <span v-if="setting?.show_account_code_in_folio_transaction == 1">{{ slotProps.data.account_code }} - </span>
                <span>{{ slotProps.data.account_name }}</span>

            </template>
        </Column>
        <Column field="quantity" header="Qty" class="text-right"></Column>
        <Column field="price" header="Amount/Rate" class="text-right" style="min-width: 70px;">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.price"
                    class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="discount_amount" header="Discount" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.discount_amount" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="total_tax" header="Tax" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.total_tax" class="white-space-nowrap" />
            </template>
        </Column>
        <Column field="bank_fee_amount" header="Bank Fee" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.bank_fee_amount" class="white-space-nowrap" />
            </template>
        </Column>
        
        <Column field="total_amount" header="Total Amount" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.total_amount" class="white-space-nowrap" />
            </template>
        </Column>
        
        <Column field="note" header="Note" style="min-width: 160px;">
            <template #body="slotProps">
                <div v-if="slotProps.data.note" v-tooltip.top="slotProps.data.note">
                    {{ slotProps.data.note.slice(0, 20) + (slotProps.data.note.length > 20 ? '...' : '') }}
                </div>
            </template>
        </Column>
        <Column field="owner" header="Made By"></Column>
        <Column field="creation" header="Created"></Column>
        <Column header="">
            <template #body="slotProps">
                <div class="flex items-center justify-end">
                    <div class="res_btn_st">
                        <Button class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded icon="pi pi-ellipsis-v" @click="toggle"></Button>
                    </div>
                    <Menu :model="menus" :popup="true" ref="show" style="min-width: 180px;">
                        <template #end>
                            <button v-if="slotProps.data.name" @click="onViewFolioDetail(slotProps.data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Detail
                            </button>
                            <button @click="onEditFolioTransaction(slotProps.data)" v-if="!slotProps.data.parent_reference" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Edit
                            </button>
                            <button @click="onDeleteFolioTransaction(slotProps.data)" v-if="!slotProps.data.parent_reference" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                Delete
                            </button>
                        </template>
                    </Menu>
                </div>
            </template>
        </Column>
        <ColumnGroup type="footer">
            <Row>
                <Column footer="Total:" :colspan="4" footerStyle="text-align:right" />
                <Column footerStyle="text-align:right">
                    <template #footer>
                     
                       {{ getTotal('quantity')}}
                    </template>
                </Column>
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('amount')" />
                 
                    </template>
                </Column>
                
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('discount_amount')" />
                 
                    </template>
                </Column>
                
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_tax')" />
                 
                    </template>
                </Column>
                 
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('bank_fee_amount')" />
                 
                    </template>
                </Column>
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <CurrencyFormat :value="getTotal('total_amount')" />
                 
                    </template>
                </Column>
               
                <Column/>
                <Column/>
                <Column/>
                <Column/>
                <!-- <Column/>
                <Column/> -->
               
            </Row>
        </ColumnGroup>

    </DataTable>
    <div class="w-full flex justify-content-end my-2">
        <div class="w-30rem">
            <div v-for="(item, index) in rs.folio_summary" :key="index" class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency :title="item.account_category" :value="item.amount" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Debit" :value="rs.totalDebit" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Credit" :value="rs.totalCredit" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
                
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Balance" :value="(rs.totalDebit - rs.totalCredit)" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
        </div>  
    </div>
</ComPlaceholder>
</template>
<script setup>
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
import ComReservationStayMoreButton from '@/views/reservation/components/ComReservationStayMoreButton.vue'

import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast,deleteApi } from '@/plugin';
import ComNote from '@/components/form/ComNote.vue'
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';

const frappe = inject('$frappe');

const setting = JSON.parse( localStorage.getItem("edoor_setting"))

const call = frappe.call();
const dialog = useDialog();
const show = ref()
const confirm = useConfirm();
const rs = inject('$reservation_stay');
const moment = inject("$moment")
const toast = useToast();

const toggle = (event) => {
    show.value.toggle(event)
}

const getTotal = ref((column_name) => {
    if (rs.folioTransactions?.filter(r => (r.parent_reference || '') == '').length == 0) {
        return 0
    } else {
        return rs.folioTransactions?.filter(r => (r.parent_reference || '') == '').reduce((n, d) => n + d[column_name], 0)
    }
});


function onEditFolioTransaction(data) {
  
    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_transaction_number: data.name
        },
        props: {
            header: 'Edit Folio Transaction - ' + data.name,
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
                
            }

        }
    })
}

function onDeleteFolioTransaction(doc) {

    const dialogRef = dialog.open(ComNote, {
        props: {
            header: "Delete Folio Transaction - " + doc.name,
            style: {
                width: '350',
            },
            modal: true
        },
        onClose: (options) => {
            const data = options.data;

            if (data != undefined) {
                rs.loading = false;
                deleteApi('utils.delete_doc', { doctype: "Folio Transaction", name: doc.name, note: data })
                    .then((result) => {
                        rs.onLoadReservationFolios()
                        rs.onLoadFolioTransaction(rs.selectedFolio)
                        rs.loading = false;
                        
                    }
                    )


            }
        }
    })


}

const onViewFolioDetail = (doc) => {
 
 const dialogRef = dialog.open(ComFolioTransactionDetail, {
     data:{
         folio_transaction_number:doc.name
     },
     props: {
         header: 'Folio Transaction Detail - ' + doc.name ,
         style: {
             width: '50vw',
         },
         modal: true
     },
    
 });
  
}

</script>