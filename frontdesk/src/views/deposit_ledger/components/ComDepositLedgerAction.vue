<template>
    <div class="flex justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio mb-2">
        <div>

            <template v-for="(d, index) in accountGroups" :key="index">
                <Button @click="onAddFolioTransaction(d)" class="conten-btn mr-1">
                    Post {{ d.account_name }}
                </Button>
            </template>

            <Button class="conten-btn" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
                @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu" :popup="true">
                <template #end>

                    <button @click="closeFolio" v-if="selectedFolio?.status == 'Open'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-ban" />
                        <span class="ml-2">Close Folio</span>
                    </button>
                    <button @click="EditFolio(true)"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-file-edit" />
                        <span class="ml-2">Edit Folio </span>
                    </button>

                    <button @click="openFolio" v-if="selectedFolio?.status == 'Closed'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-check-circle" />
                        <span class="ml-2">Open Folio</span>
                    </button>

                    <button @click="onDeleteFolio"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-times-circle" />
                        <span class="ml-2">Delete Folio</span>
                    </button>

                </template>
            </Menu>
        </div>
        <div>
            <SplitButton @click="viewFolioSummaryReport" class="spl__btn_cs sp" label="Print" icon="pi pi-print"
                :model="print_menus" />
            <Button @click="onRefresh()" icon="pi pi-refresh" class="content_btn_b ml-2"></Button>

        </div>
    </div>
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc, watch } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';

 
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransfer from "@/views/reservation/components/reservation_stay_folio/ComFolioTransfer.vue";
import ComAddDepositLedger from "@/views/deposit_ledger/components/ComAddDepositLedger.vue";

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
                    width: '750px',
                },

                modal: true,
                position: "top",
                closeOnEscape: false
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
    window.socket.emit("DepositLedger", { property: window.property_name })
    window.socket.emit("ComDepositLedgerDetail", { name: selectedFolio.value.name })



}

const onRefresh = debouncer(() => {
    window.socket.emit("ComDepositLedgerDetail", { name: selectedFolio.value.name })
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
                width: '75vw',
            },

            modal: true,
            position: "top"
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
            position: 'top'
        },
        onClose: (options) => {
            let data = options.data;
            if (data != undefined) {
                window.socket.emit("ComDepositLedgerDetail", { name: data.name })
                window.socket.emit("DepositLedger", { property: window.property_name })
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
                    window.socket.emit("ComDepositLedgerDetail", { name: selectedFolio.value.name })
                    window.socket.emit("DepositLedger", { property: window.property_name })
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

                    window.socket.emit("ComDepositLedgerDetail", { name: selectedFolio.value.name })
                    window.socket.emit("DepositLedger", { property: window.property_name })
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
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                window.socket.emit("DepositLedger", { "property": window.property_name })



                emit("onClose")

            }
        }
    });




}

function onTransferFolioItem() {
    if (selectedFolio.value.status == "Open") {
        const selectedFolioTransactions = JSON.parse(sessionStorage.getItem("folo_transaction_table_state_" + selectedFolio.value.name)).selection

        if (selectedFolioTransactions.length == 0) {
            toast.add({ severity: 'warn', summary: "", detail: "Please select a filio transaction to transfer", life: 3000 })
            return
        }

        const dialogRef = dialog.open(ComFolioTransfer, {
            data: {
                reservation: selectedFolio.value.reservation,
                reservation_stay: selectedFolio.value.reservation_stay,
                folio_number: selectedFolio.value.name,
                folio_transaction: selectedFolioTransactions,

            },
            props: {
                header: 'Folio Transfer',
                style: {
                    width: '75vw',
                },

                modal: true,
                position: "top"
            },
            onClose: (options) => {
                const data = options.data;

                if (data) {
                    selectedFolioTransactions.value = []

                    reloadData()

                    setTimeout(() => {
                        window.socket.emit("ReservationDetail", selectedFolio.value.reservation)
                        window.socket.emit("Frontdesk", selectedFolio.value.reservation)
                    }, 3000);


                }
            }
        })
    } else {
        toast.add({ severity: 'warn', summary: "", detail: "Folio is already closed.", life: 3000 })
    }
}







</script>
 