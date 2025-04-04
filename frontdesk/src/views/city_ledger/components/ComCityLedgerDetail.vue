<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true" style="max-height: 80vh;">
        <TabView>
            <TabPanel :header=" $t('Account Information')">
                <div class="grid">
                    <div class="col-6">
                <ComCityLedgerDetailAccountInfo v-if="data" :data="data" />
                    </div>
                    <div class="col-6">
                <ComCityLedgerDetailInvoiceInfo v-if="data" :data="data" />
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
import { ref, getDoc, inject, useDialog, onMounted, deleteDoc, useConfirm, onUnmounted, useToast } from '@/plugin'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import ComCityLedgerTransaction from '@/views/city_ledger/components/ComCityLedgerTransaction.vue';
import ComCityLedgerDetailAccountInfo from '@/views/city_ledger/components/ComCityLedgerDetailAccountInfo.vue';
import ComCityLedgerDetailInvoiceInfo from './ComCityLedgerDetailInvoiceInfo.vue';


const dialogRef = inject("dialogRef")
const gv = inject('$gv');
const dialog = useDialog()
const toast = useToast();
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
    if (window.has_city_ledger_transaction.length > 0) {
        return toast.add({ severity: 'warn', summary: 'Delete City Ledger', detail: 'This City Ledger contains folio transaction(s)', life: 3000 })
    }
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