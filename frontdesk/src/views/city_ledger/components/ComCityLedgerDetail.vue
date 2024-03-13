<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" style="max-height: 80vh;">
        <TabView>
            <TabPanel :header=" $t('Account Information')">
                <table class="w-full mt-3">
                    <tr>
                        <td colspan="2" class="p-0">
                            <div class="flex w-full gap-2">
                                <div class="flex flex-column rounded-lg  grow p-2 shadow-charge-total border">
                                    <span class="text-500 uppercase text-sm text-end">{{ $t('total debit') }} </span><span
                                        class="text-xl line-height-2 font-semibold text-end">
                                        <span>
                                            <CurrencyFormat :value="data?.total_debit" />
                                        </span></span>
                                </div>
                                <div class="flex flex-column rounded-lg grow p-2 shadow-charge-total border">
                                    <span class="text-500 uppercase text-sm text-end"> {{ $t('total credit') }} </span><span
                                        class="text-xl line-height-2 font-semibold text-end">
                                        <span>
                                            <CurrencyFormat :value="data?.total_credit" />
                                        </span></span>
                                </div>
                                <div
                                    class="flex flex-column rounded-lg grow p-2 shadow-charge-total bg-green-50 border border-green-edoor">
                                    <span class="text-500 uppercase text-sm text-end"> {{ $t('Balance') }} </span><span
                                        class="text-xl line-height-2 font-semibold text-end">
                                        <span>
                                            <CurrencyFormat :value="data?.balance" />
                                        </span></span>
                                </div>
                            </div>
                        </td>
                    </tr>
                </table>
                <div class="mt-3">
                    <table>
                        <tr>
                            <td class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center" colspan="2">{{ $t('City Ledger Information') }} </td>
                        </tr>
                        <ComStayInfoNoBox label="City Ledger Name" :value="data?.city_ledger_name" />
                        <ComStayInfoNoBox label="City Ledger Type" :value="data?.city_ledger_type" />
                        <ComStayInfoNoBox label="Business Source" :value="data?.business_source" />
                        <ComStayInfoNoBox label="Company Name" :value="data?.company_name" />
                        <ComStayInfoNoBox label="Phone Number" :value="data?.phone_number" />
                        <ComStayInfoNoBox label="Email" :value="data?.email_address" />
                        <ComStayInfoNoBox label="Address" :value="data?.address" />
                    </table>
                    <div class="grid">
                        <div class="col-12 md:col-6">
                            <table class="mt-3">
                                <tr>
                                    <td class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center" colspan="2">
                                        {{ $t('Bank Information') }} </td>
                                </tr>
                                <ComStayInfoNoBox label="Bank Name" :value="data?.bank_name" />
                                <ComStayInfoNoBox label="Bank Account Number" :value="data?.bank_account_number" />
                                <ComStayInfoNoBox label="Bank Account Name" :value="data?.bank_account_name" />
                            </table>
                        </div>
                        <div class="col-12 md:col-6">
                            <table class="mt-3">
                                <tr>
                                    <td class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center" colspan="2">
                                        {{ $t('Contact Person Information') }} </td>
                                </tr>
                                <ComStayInfoNoBox label="Contact Name" :value="data?.contact_name" />
                                <ComStayInfoNoBox label="Contact Phone Number" :value="data?.contact_phone_number" />
                            </table>
                        </div>
                    </div>
                    <div class="w-full mt-3">
                        <label>{{ $t('Note') }} </label>
                        <div class="w-full bg-slate-100 rounded-lg p-3 h-10rem overflow-auto ">
                            {{ data?.note }}
                        </div>
                    </div>
                </div>
                <hr class="my-2">
                <div class="w-full flex justify-end flex-column md:flex-row text-sm -mb-2">
                    <div class="flex">
                    <span class="italic white-space-nowrap">{{ $t('Created by') }} : </span>
                    <span class="text-500 font-italic white-space-nowrap">
                        {{ data?.owner.split("@")[0] }}
                        <ComTimeago :date="data?.creation" />
                    </span>
                    </div>
                    <div class="flex">
                    <span class="italic ms-0 md:ms-2 white-space-nowrap"> {{ $t('Last Modified') }} : </span>
                    <span class="text-500 font-italic white-space-nowrap">
                        {{ data?.modified_by.split("@")[0] }}
                        <ComTimeago :date="data?.modified" />
                    </span>
                    </div>
                </div>
            </TabPanel>
            <TabPanel :header=" $t('City Ledger Transaction') ">
                <ComCityLedgerTransaction v-if="data" :name="data?.name" />
            </TabPanel>
            <TabPanel>
                <template #header>
                            <span class="me-2">{{ $t('Document') }} </span>
                            <ComDocumentBadge doctype="City Ledger"
                                :doctypes="['City Ledger']" :docname="data?.name"
                                :attacheds="[data?.name]" v-if="data?.name" />
                        </template>
                <div>

                    <ComDocument v-if="data?.name" doctype="City Ledger" :doctypes="['City Ledger']" :docname="data?.name"
                        :fill="false" :attacheds="[data?.name]" />
                </div>
            </TabPanel>
        </TabView>
        <template #footer-right>
            <Button class="border-none" @click="onEditcityLedger">
                <i class="pi pi-pencil me-2" /> {{ $t('Edit') }} 
            </Button>
            <Button class="bg-red-500 border-none" @click="onDeletecityLedger"> <i class="pi pi-trash me-2" />
               {{ $t('Delete') }} </Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, getDoc, inject, useDialog, onMounted, deleteDoc, useConfirm, onUnmounted } from '@/plugin'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import ComCityLedgerTransaction from '@/views/city_ledger/components/ComCityLedgerTransaction.vue';
const dialogRef = inject("dialogRef")
const gv = inject('$gv');
const dialog = useDialog()
const data = ref()
const loading = ref(false)
const confirm = useConfirm()
function onEditcityLedger() {
    dialog.open(ComAddCityLedgerAccount, {
        data: {
            name: data.value.name,
        },
        props: {
            header: `Edit Ledger Account`,
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
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
                loading.value = false
            }
        }
    });
}
function onDeletecityLedger() {
    confirm.require({
        message: 'Are you sure you want to delete city ledger account?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            deleteDoc('City Ledger', data.value.name)
                .then((r) => {
                    // loadData()
                    window.postMessage({action:"CityLedgerAccount"},"*")
                    dialogRef.value.close(r)
                }).catch((err) => {
                    loading.value = false
                })
        },
    });
}

function loadData(show_loading = true) {
    loading.value = show_loading
    getDoc('City Ledger', dialogRef.value.data.name)
        .then((r) => {
            data.value = r
            loading.value = false
        }).catch((err) => {
            loading.value = false
        })
}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="ComCityLedgerDetail"){
            setTimeout(()=>{
                loadData(false)
            },1000*3)
            
        }
    };
}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    loadData() 
    window.addEventListener('message', actionRefreshData, false);
})
onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})
</script>