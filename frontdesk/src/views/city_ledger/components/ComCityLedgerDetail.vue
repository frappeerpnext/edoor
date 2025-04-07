<template>
    <ComDialogContent hideButtonOK @onClose="onClose" style="max-height: 80vh;" :loading="loading">
        <TabView>
            <TabPanel :header="$t('Account Information')">
                <div class="grid">
                     <div class="col-12">
                        <ComCityLedgerDetailInvoiceInfo v-if="data" :data="data" />
                    </div>
                    <div class="col-6">
                        <ComCityLedgerDetailAccountInfo v-if="data" :data="data" />
                    </div>
                    <div class="col-6">
                        <div class="p-2 bg-gray-200 border-round-lg text-center">
        <b>Issue An Invoice</b>
    </div>
                        <div>
        <ComCityLedgerDetailPaymentReceived v-if="data" :name="data?.name" />
        <ComCityLedgerDetailAging  v-if="data" :name="data?.name" />
    </div>
                    </div>
                   
                </div>
            </TabPanel>
            <TabPanel :header="$t('City Ledger Transaction')">
                <ComCityLedgerTransaction v-if="data" :name="data?.name" />
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="me-2">{{ $t('Document') }} </span>
                    <ComDocumentBadge doctype="City Ledger" :doctypes="['City Ledger']" :docname="data?.name"
                        :attacheds="[data?.name]" v-if="data?.name" />
                </template>
                <div>

                    <ComDocument v-if="data?.name" doctype="City Ledger" :doctypes="['City Ledger']"
                        :docname="data?.name" :fill="false" :attacheds="[data?.name]" />
                </div>
            </TabPanel>
        </TabView>
        <template #footer-left>


            <SplitButton label="Options" :model="cityLedgerOptions" />
            <Button class="border-none" @click="onEditcityLedger">
                <i class="pi pi-pencil me-2" /> {{ $t('Edit') }}
            </Button>
            <Button class="bg-red-500 border-none" @click="onDeletecityLedger"> <i class="pi pi-trash me-2" />
                {{ $t('Delete') }} </Button>
        </template>


    </ComDialogContent>
</template>
<script setup>
import { ref, getDoc, inject, useDialog, onMounted, deleteDoc, useConfirm, onUnmounted, useToast, updateDocument,getDocument } from '@/plugin'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import ComCityLedgerTransaction from '@/views/city_ledger/components/ComCityLedgerTransaction.vue';
import ComCityLedgerDetailAccountInfo from '@/views/city_ledger/components/ComCityLedgerDetailAccountInfo.vue';
import ComCityLedgerDetailInvoiceInfo from './ComCityLedgerDetailInvoiceInfo.vue';
import { computed } from 'vue';
import ComCityLedgerDetailPaymentReceived from '@/views/city_ledger/components/ComCityLedgerDetailPaymentReceived.vue';
import ComCityLedgerDetailAging from '@/views/city_ledger/components/ComCityLedgerDetailAging.vue';

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
            breakpoints: {
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
                    window.postMessage({ action: "CityLedgerAccount" }, "*")
                    dialogRef.value.close(r)
                }).catch((err) => {
                    loading.value = false
                })
        },
    });
}

const cityLedgerOptions = computed(()=>{
    const options = []
    if (data.value) {
        if (data.value.status == "Open") {
            options.push(
                {
                    label: "Close this City Ledger Account",
                    icon: 'pi pi-print',
                    command: async () => {
                        loading.value = true;
                       await updateDocument({
                            doctype: "City Ledger",
                            name: data.value.name,
                            data: {
                                status: "Closed"
                            }
                        })
                        loadData()

                        loading.value = false;
                    }
                }
            )
        }else {
            options.push(
                {
                    label: "Reopen this City Ledger Account",
                    icon: 'pi pi-print',
                    command: async () => {
                        loading.value = true;
                       await updateDocument({
                            doctype: "City Ledger",
                            name: data.value.name,
                            data: {
                                status: "Open"
                            }
                        })
                        loadData()
                        loading.value = false;
                    }
                }
            )
        }
    }

    return options
})
    
 

async function loadData(show_loading = true) {
    loading.value = show_loading
    let res = await getDocument('City Ledger', dialogRef.value.data.name);
    if (res.data) {
        data.value = res.data
    }

    loading.value = false


}

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if (e.data.action == "ComCityLedgerDetail") {
            setTimeout(() => {
                loadData(false)
            }, 1000 * 3)

        }
    };
}

onMounted(async () => {
    if (window.isMobile) {
        let elem = document.querySelectorAll(".p-dialog");
        if (elem) {
            elem = elem[elem.length - 1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    await loadData()
    window.addEventListener('message', actionRefreshData, false);
})

const onClose = () => {
    dialogRef.value.close()
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})
</script>