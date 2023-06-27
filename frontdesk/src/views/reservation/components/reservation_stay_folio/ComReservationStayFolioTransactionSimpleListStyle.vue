<template>
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
        
        <Column field="total_amount" header="Toal Amount" class="text-right">
            <template #body="slotProps">
                <CurrencyFormat :value="slotProps.data.total_amount" class="white-space-nowrap" />
            </template>
        </Column>
        

        <Column field="note" header="Note">
            <template #body="slotProps">
                <div v-if="slotProps.data.note" v-tooltip.top="slotProps.data.note">
                    {{ slotProps.data.note.slice(0, 20) + (slotProps.data.note.length > 20 ? '...' : '') }}
                </div>
            </template>
        </Column>
        <Column field="owner" header="Made By"></Column>
        <Column field="creation" header="Created"></Column>
        <Column>
            <template #body="slotProps">
                <Button class="border-none" v-if="slotProps.data.name" @click="onViewFolioDetail(slotProps.data)">Detail</Button>
            </template>
        </Column>
        <Column header="">
            <template #body="slotProps">
                <button @click="onEditFolioTransaction(slotProps.data)"
                    v-if="!slotProps.data.parent_reference">Edit</button>

            </template>
        </Column>
        <Column header="">
            <template #body="slotProps">
                <button @click="onDeleteFolioTransaction(slotProps.data)"
                    v-if="!slotProps.data.parent_reference">Delete</button>
            </template>
        </Column>
        <ColumnGroup type="footer">
            <Row>
                <Column footer="Total:" :colspan="4" footerStyle="text-align:right" />
                <Column footerStyle="text-align:right">
                    <template #footer>
                        <!-- <CurrencyFormat :value="getTotal('quantity')" /> -->
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
                <Column/>
                <Column/>
               
            </Row>
        </ColumnGroup>

    </DataTable>
    
    <div class="w-full flex justify-content-end">
        <div class="w-30rem">
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Credit" :value="totalCredit" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Total Debit" :value="totalDebit" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
            <div class="flex mt-2 gap-2">
                <ComBoxStayInformation isCurrency title="Balance" :value="(totalDebit - totalCredit)" valueClass="col-6 text-right bg-gray-edoor-10 font-semibold" titleClass="grow font-semibold"></ComBoxStayInformation>
            </div>
        </div>  
    </div>
</template>
<script setup>
import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';


import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast } from '@/plugin';
import ComNote from '@/components/form/ComNote.vue'
const frappe = inject('$frappe');

const setting = JSON.parse( localStorage.getItem("edoor_setting"))

const call = frappe.call();
const dialog = useDialog();
const confirm = useConfirm();
const rs = inject('$reservation_stay');
const moment = inject("$moment")
const toast = useToast();

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
            header: 'Edit Transaction - ' + data.account_code + ' - ' + data.account_name,
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;

            if (data) {
                rs.onLoadFolioTransaction(rs.selectedFolio.name)
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
                call
                    .delete('edoor.api.utils.delete_doc', { doctype: "Folio Transaction", name: doc.name, note: data })
                    .then((result) => {
                        rs.onLoadFolioTransaction(rs.selectedFolio.name)
                        rs.loading = false;
                        toast.add({ severity: 'success', summary: "Delete Folio Transaction", detail: "Delete Folio Transaction successfully", life: 3000 })
                    }
                    )


            }
        }
    })


}


const totalCredit = computed(() => {
    if (rs.folioTransactions) {

        return rs.folioTransactions?.filter(r => r.type == 'Credit').reduce((n, d) => n + (d.amount || 0), 0)


    }
    return 0

})

const totalDebit = computed(() => {
    if (rs.folioTransactions) {

        return rs.folioTransactions?.filter(r => r.type == 'Debit').reduce((n, d) => n + (d.amount || 0), 0)


    }
    return 0

})



</script>