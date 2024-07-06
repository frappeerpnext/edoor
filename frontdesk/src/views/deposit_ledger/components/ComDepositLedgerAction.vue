<template>
    <div class="flex pb-1 md:pb-0 overflow-auto  justify-content-between align-items-center md:flex-wrap wp-btn-post-in-stay-folio mb-2">
        <div class="flex">

            <template v-for="(d, index) in accountGroups" :key="index">
                <Button @click="onAddFolioTransaction(d)" class="conten-btn mr-1 white white-space-nowrap">
                    {{ $t('Post ' + d.account_name) }}
                </Button>
            </template>

            <Button class="conten-btn white-space-nowrap" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
                @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu" :popup="true">
                <template #end>

                    <button @click="closeFolio" v-if="selectedFolio?.status == 'Open'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-ban" />
                        <span class="ml-2"> {{ $t('Close Folio') }} </span>
                    </button>
                    <button @click="EditFolio(true)"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-file-edit" />
                        <span class="ml-2"> {{ $t('Edit Folio') }} </span>
                    </button>

                    <button @click="openFolio" v-if="selectedFolio?.status == 'Closed'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-check-circle" />
                        <span class="ml-2">{{ $t('Open Folio') }} </span>
                    </button>

                    <button @click="onDeleteFolio"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-times-circle" />
                        <span class="ml-2">{{ $t('Delete Folio') }} </span>
                    </button>

                </template>
            </Menu>
        </div>
        <div class="flex ms-2 md:ms-0">
            <SplitButton @click="viewFolioSummaryReport" class="spl__btn_cs sp" label="Print" icon="pi pi-print"
                :model="print_menus" />
            <Button @click="onRefresh()" icon="pi pi-refresh" class="content_btn_b btn-size2 ml-2"></Button>

        </div>
    </div>
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc, watch,onMounted,getDocList } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';

 
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransfer from "@/views/reservation/components/reservation_stay_folio/ComFolioTransfer.vue";
import ComAddDepositLedger from "@/views/deposit_ledger/components/ComAddDepositLedger.vue";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    folio: Object,
})
const emit = defineEmits(["onClose"])

const accountGroups = ref(window.setting.account_group.filter(r => r.show_in_deposit_ledger == 1))
const selectedFolio = ref(props.folio)

const dialog = useDialog();
const confirm = useConfirm();
const toast = useToast();
const gv = inject("$gv")
const rs = inject("$reservation_stay")
const setting = window.setting
const folio_menu = ref();

function showAccountGroup(account_code) {
    if (selectedFolio.value.allow_post_to_city_ledger == 0) {
        if ((account_code.is_city_ledger_account || 0) == 1) {
            return false
        }
    }
    return true
}
//trach user select new folio and reload folio information

watch(() => props.folio, (newValue, oldValue) => {

    selectedFolio.value = newValue

})

const toggle = (event) => {
    folio_menu.value.toggle(event);
}

const print_menus = ref([])

function viewFolioSummaryReport() {

    dialog.open(ComIFrameModal, {
        data: {
            doctype: "Deposit%20Ledger",
            name: selectedFolio.value.name,
            report_name: gv.getCustomPrintFormat("eDoor Deposit Ledger Invoice Summary"),
            show_letter_head: true,
            filter_options:['invoice_style']
        },
        props: {
            header: "Deposit Ledger Invoice Summary",
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });


}

//Folio Summary Report
print_menus.value.push({
    label: "Deposit Ledger Summary Report",
    icon: 'pi pi-print',
    command: () => {

        viewFolioSummaryReport()
    }
})


//folio detail report
print_menus.value.push({
    label: "Deposit Ledger Detail Report",
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                doctype: "Deposit%20Ledger",
                name: selectedFolio.value.name,
                report_name: gv.getCustomPrintFormat("eDoor Deposit Ledger Invoice Detail"),
                show_letter_head: true,
                filter_options:["show_summary",'invoice_style']
            },
            props: {
                header: "Deposit Ledger Invoice Summary",
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
            },
        });
    }
})

function onAddFolioTransaction(account_code) {
    if (props.newDoc) {
        props.newDoc.account_group = account_code.name
    }
    if (account_code.is_city_ledger_account == 1) {
        if (selectedFolio.value.allow_post_to_city_ledger == 0) {
            toast.add({ severity: 'warn', summary: "", detail: "This reservation is not allow to post charge to city ledger.", life: 5000 })
            return
        }
    }

    if (selectedFolio.value.status == "Open") {
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                new_doc: {
                    transaction_type: "Deposit Ledger",
                    transaction_number: selectedFolio.value.name,
                    property: window.property_name,
                    account_group: account_code.name,
                    guest:selectedFolio.value.guest
                },
                balance: selectedFolio.value.balance,
                account_code_filter: { is_deposit_ledger_account: 1 }
            },
            props: {
                header: 'Post ' + account_code.account_name + ' to Folio ' + props.folio.name,
                style: {
                    width: '60vw',
                },

                modal: true,
                position: "top",
                closeOnEscape: false,
                breakpoints:{
                '960px': '750px',
                '640px': '100vw'
            },
            },
            onClose: (options) => {
                const data = options.data;
                if (data) {
                    reloadData()
                    if ((data.show_print_preview || 0) == 1) {
                        if (data.print_format) {
                            showPrintPreview(data)
                        }
                    }
                }
            }
        })

    } else {
        toast.add({ severity: 'warn', summary: "", detail: "Folio is already closed.", life: 3000 })
    }
}

function reloadData() {
    window.postMessage({action:"DepositLedger"},"*")
    window.postMessage({action:"ComDepositLedgerDetai"},"*")



}

const onRefresh = debouncer(() => { 
    window.postMessage({action:"ComDepositLedgerDetai"},"*")
}, 500);
function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

function showPrintPreview(data) {

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            doctype: "Folio Transaction",
            name: data.name,
            report_name: data.print_format,
            show_letter_head: true
        },
        props: {
            header: 'Print Preview',
            style: {
                width: '80vw',
            },

            modal: true,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    })
}

function EditFolio() {

    const dialogRef = dialog.open(ComAddDepositLedger, {

        data: {
            name: selectedFolio.value.name,
        },
        props: {
            header: 'Edit Deposit Ledger' + selectedFolio.value.name,
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
            let data = options.data;
            if (data != undefined) {
                window.postMessage({action:"ComDepositLedgerDetail"},"*")
                window.postMessage({action:"DepositLedger"},"*")
            }
        }
    })
}

function openFolio() {

    confirm.require({
        header: 'Open Deposit Ledger ' + selectedFolio.value.name,
        message: 'Are you sure you want to open this deposit ledger ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Deposit Ledger', selectedFolio.value.name, {
                status: 'Open',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status;
                    window.postMessage({action:"ComDepositLedgerDetail"},"*")
                    window.postMessage({action:"DepositLedger"},"*")
                })
        },

    })

}


function closeFolio() {
    confirm.require({
        header: 'Close Deposit Ledger ' + selectedFolio.value.name,
        message: 'Are you sure you want to close this deposit ledger ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Deposit Ledger', selectedFolio.value.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status;
                    window.postMessage({action:"ComDepositLedgerDetail"},"*")
                    window.postMessage({action:"DepositLedger"},"*")  
                })
        },

    });
}


function onDeleteFolio() {
    if (!selectedFolio.value.name) {
        gv.toast('warn', 'Please select a Folio.')
        return
    }

    const dialogRef = dialog.open(ComDialogNote, {
        data: {
            api_url: "utils.delete_doc",
            method: "DELETE",
            confirm_message: "Are you sure you want to delete this folio?",
            data: { doctype: "Deposit Ledger", name: selectedFolio.value.name },
        },
        props: {
            header: "Delete Deposit Ledger" + " " + selectedFolio.value.name,
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
            const data = options.data;
            if (data) { 
                window.postMessage({action:"DepositLedger"},"*")
                emit("onClose")

            }
        }
    });




}

 


onMounted(()=>{
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    getDocList('Custom Print Format', {
        fields: [
            'print_format',
            'icon',
            'title',
            'attach_to_doctype'
        ],
        filters: [["property", "=", window.property_name], ["attach_to_doctype", "=", 'Deposit Ledger']]
    })
        .then((doc) => {
            doc.forEach(d => {
                print_menus.value.push({
                    label: d.title,
                    name: d.print_format,
                    icon: d.icon ? d.icon : "pi pi-print",
                    command: (r) => {
                      
                        dialog.open(ComIFrameModal, {
                            data: {
                                doctype: d.attach_to_doctype,
                                name: props.folio.name,
                                report_name: d.print_format,
                                show_letter_head: true,
                            },
                            props: {
                                header: d.title,
                                style: {
                                    width: '80vw',
                                },
                                position: "top",
                                modal: true,
                                maximizable: true,
                                breakpoints:{
                                    '960px': '80vw',
                                    '640px': '100vw'
                                },
                            },
                        });
                    }
                })
            });
        })
})

</script>
 