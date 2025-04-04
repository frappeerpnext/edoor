<template>
    <div
        class="flex pb-1 md:pb-0 overflow-auto justify-content-between align-items-center md:flex-wrap wp-btn-post-in-stay-folio mb-2">
        <div class="flex gap-2">
           
            <ComFolioActionButton @onClick="onAddFolioTransaction"
                :data="folio_operation" />

            <Button class=" conten-btn white-space-nowrap" icon="pi pi-chevron-down" iconPos="right" type="button"
                label="Options" @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu" :popup="true">
                <template #end>
                    <template v-for="(d, index) in folio_operation.discount_section" :key="index">
                        <button v-if="!d.sub_account" @click="onAddFolioTransaction(d)"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i :class="d.icon" />
                            <span class="ml-2 ">{{ $t(d.label) }}</span>
                        </button>
                    </template>

                    <button @click="closeCityLedgerInvoice" v-if="selectedCityLedgerInvoice?.status == 'Open'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-ban" />
                        <span class="ml-2"> {{ $t('Close City Ledger Invoice') }} </span>
                    </button>
                    <button @click="EditFolio(true)"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-file-edit" />
                        <span class="ml-2">{{ $t('Edit City Ledger Invoice') }} </span>
                    </button>

                    <button @click="openCityLedgerInvoice" v-if="selectedCityLedgerInvoice?.status == 'Closed'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-check-circle" />
                        <span class="ml-2">{{ $t('Open City Ledger Invoice') }} </span>
                    </button>
                    <button @click="onDeleteFolio"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-times-circle" />
                        <span class="ml-2"> {{ $t('Delete this Invoice') }} </span>
                    </button>

                </template>
            </Menu>
        </div>
        <div class="flex ms-2 md:ms-0">
            <Button @click="viewCityLedgerDetail" class="conten-btn sp" :label="$t('Print')" icon="pi pi-print" />
            <Button @click="onRefresh()" icon="pi pi-refresh" class="content_btn_b btn-size2 ml-2"></Button>
        </div>

    </div>
    <!-- show tax invoice info -->

    <Message v-if="selectedCityLedgerInvoice?.tax_invoice_number" severity="info">
        <div class="flex justify-content-between align-items-center w-full">
            <div>
                This Folio has Generate {{ selectedCityLedgerInvoice.tax_invoice_type }} - {{ selectedCityLedgerInvoice?.tax_invoice_number }}
            </div>
            <div class="ms-5">
                <Button class="conten-btn" style="background: transparent;" @click="viewfoliotaxinvoicedetail">
                    <i class="pi pi-print me-2" />
                    Print Tax Invoice
                </Button>
            </div>
        </div>

    </Message>
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc, watch, onMounted, getDoc,getApi } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';

import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComAddDeskFolio from "@/views/desk_folio/components/ComAddDeskFolio.vue";
import ComGenerateTaxInvoice from "@/views/reservation/components/ComGenerateTaxInvoice.vue";
import ComFolioActionButton from '@/views/reservation/components/ComFolioActionButton.vue';
import ComReportServerModal from "@/components/ComReportServerModal.vue";
import ComAddCityLedgerInvoice from "@/views/city_ledger_invoice/components/ComAddCityLedgerInvoice.vue" 
import { i18n } from '@/i18n';

const isMobile = ref(window.isMobile)
const { t: $t } = i18n.global;
const props = defineProps({
    folio: Object,
    newDoc:Object
})

const emit = defineEmits(["onClose"])
const accountGroups = ref(window.setting.account_group.filter(r => r.show_in_desk_folio == 1))
const selectedCityLedgerInvoice = ref(props.folio)
const dialog = useDialog();
const confirm = useConfirm();
const toast = useToast();
const gv = inject("$gv")
const setting = window.setting
const folio_menu = ref();

const folio_operation = ref(JSON.parse(setting.folio_operation_setting).city_ledger_Invoice);
 


watch(() => props.folio, (newValue, oldValue) => {

    selectedCityLedgerInvoice.value = newValue

})

const toggle = (event) => {
    folio_menu.value.toggle(event);
}


const print_menus = ref([])

function viewCityLedgerDetail() {
    if (window.setting.server_report_url) {

        OpenServerReport("/Front Desk/rptCityLedgerInvoiceDetail", "City Ledger Invoice Detail" , [{ name: 'city_ledger_invoice', values: [selectedCityLedgerInvoice.value.name] }])

    }
    else {
        dialog.open(ComIFrameModal, {
            data: {
                doctype: "Desk%20Folio",
                name: selectedCityLedgerInvoice.value.name,
                report_name: gv.getCustomPrintFormat("eDoor Desk Folio Invoice Summary"),
                show_letter_head: true,
                filter_options: ['invoice_style']
            },
            props: {
                header: "Desk Folio Invoice Summary",
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                breakpoints: {
                    '960px': '80vw',
                    '640px': '100vw'
                },
            },
        });
    }


}


function getTaxInvoice() {
    if (selectedCityLedgerInvoice.value.tax_invoice_number) {
        getDoc("Tax Invoice", selectedCityLedgerInvoice.value.tax_invoice_number).then(r => {
            selectedCityLedgerInvoice.value.tax_invoice_type = r.tax_invoice_type
        })
    }

}

function generateTaxInvoice() {

    const dialogRef = dialog.open(ComGenerateTaxInvoice, {

        data: {
            property: window.property_name,
            name: selectedCityLedgerInvoice.value.name,
            document_type: "Desk Folio"
        },
        props: {
            header: "Generate Tax Invoice",
            style: {
                width: '30vw',
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
            let data = options.data;
            if (data != undefined) {

                selectedCityLedgerInvoice.value.tax_invoice_number = data.message.name
                selectedCityLedgerInvoice.value.tax_invoice_type = data.message.tax_invoice_type


            }
        }
    })
}


//Folio Summary Report
print_menus.value.push({
    label: "Desk Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {

        viewCityLedgerDetail()
    }
})


//folio detail report
print_menus.value.push({
    label: "Desk Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        if (window.setting.server_report_url) {
                    
                    OpenServerReport("/Front Desk/rptDeskFolioDetail", "Desk Folio Detail Invoice")

                }
                else {
        dialog.open(ComIFrameModal, {
            data: {
                doctype: "Desk%20Folio",
                name: selectedCityLedgerInvoice.value.name,
                report_name: gv.getCustomPrintFormat("eDoor Desk Folio Invoice Detail"),
                show_letter_head: true,
                filter_options: ["show_summary", 'invoice_style']
            },
            props: {
                header: "Desk Folio Invoice Detail",
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                breakpoints: {
                    '960px': '80vw',
                    '640px': '100vw'
                },
            },
        });
    }
    }
})

if (selectedCityLedgerInvoice?.value?.tax_invoice_number) {
    print_menus.value.push({
        label: $t("Print Tax Invoice"),
        icon: 'pi pi-print',
        command: () => {
            viewfoliotaxinvoicedetail()
        }
    })
}



//General Journal
if(window.setting.server_report_url){
print_menus.value.push({
    label: "General Journal",
    icon: 'pi pi-print',
    command: () => {
        OpenServerReport("/Front Desk/rptGeneralJournalTransactionForDeskFolio","General Journal by Desk Folio")
    }
})
}


function onAddFolioTransaction(account_code) {
    if (props.newDoc) {
        props.newDoc.account_group = account_code.name
    }
    if (account_code.is_city_ledger_account == 1) {
        if (selectedCityLedgerInvoice.value.allow_post_to_city_ledger == 0) {
            toast.add({ severity: 'warn', summary: "", detail: "This reservation is not allow to post charge to city ledger.", life: 5000 })
            return
        }
    }



    if (selectedCityLedgerInvoice.value.status == "Open") {
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                new_doc: {
                    ...props.newDoc,
                    account_group: account_code.name,
                    room_id: selectedCityLedgerInvoice.value.room_id,
                    business_source: selectedCityLedgerInvoice.value.business_source,
                    guest: selectedCityLedgerInvoice.value.guest
                },
                balance: selectedCityLedgerInvoice.value.balance,
                account_code_filter: account_code.filter,
            },
            props: {
                header: account_code.label + ' to Folio ' + props.folio.name,
                style: {
                    width: '60vw',
                },

                modal: true,
                position: "top",
                closeOnEscape: false,
                breakpoints: {
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
        toast.add({ severity: 'warn', summary: "", detail: "City Ledger Invoice is already closed.", life: 3000 })
    }

}

function reloadData() {
    window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
}

const onRefresh = debouncer(() => {
    window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")

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
            breakpoints: {
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    })
}

function viewfoliotaxinvoicedetail() {
    getDoc("Tax Invoice", selectedCityLedgerInvoice.value.tax_invoice_number).then(r => {
        if(setting.server_report_url){
            // get tax invoice data first before show report
            getApi("utils.get_tax_invoice_data",{folio_number:selectedCityLedgerInvoice.value.name, document_type:"Desk Folio",generate_temp_tax_data:1}).then(result=>{
                dialog.open(ComReportServerModal, {
                data: {
                    report_path: "/Front Desk/rptDeskFolioTaxInvoice",
                    params:[
                              {name: 'desk_folio', values: [selectedCityLedgerInvoice.value.name] },
                    ]
                },
                props: {
                    header: $t("Desk Folio Tax Invoice"),
                    style: {
                        width: '80vw',
                    },
                    position: "top",
                    modal: true,
                    maximizable: true,
                    closeOnEscape: false,
                    breakpoints:{
                        '960px': '80vw',
                        '640px': '100vw'
                    },

                },
            });
   
            })
        }
        else { 
        dialog.open(ComIFrameModal, {
            data: {
                doctype: "Tax Invoice",
                name: selectedCityLedgerInvoice.value.tax_invoice_number,
                report_name: r.default_print_format ? gv.getCustomPrintFormat(r.default_print_format) : gv.getCustomPrintFormat("Invoice"),
                letterhead: r.default_letterhead || "Tax Letterhead",
                filter_options: ["show_vattin", "show_rate_type", "show_business_source"]
            },
            props: {
                header: $t("Print Tax Invoice"),
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                breakpoints: {
                    '960px': '80vw',
                    '640px': '100vw'
                },
            },
        });
        }
    })


}


function EditFolio() {
    const dialogRef = dialog.open(ComAddCityLedgerInvoice, {

        data: {
            name: selectedCityLedgerInvoice.value.name,
            method:"edit"
        },
        props: {
            header: 'Edit Desk Folio ' + selectedCityLedgerInvoice.value.name,
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
            let data = options.data;
            if (data != undefined) {
                window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
            }
        }
    })
}

function openCityLedgerInvoice() {

    confirm.require({
        header: 'Open City Ledger Invoice ' + selectedCityLedgerInvoice.value.name,
        message: 'Are you sure you want to open this City Ledger Invoice ' + selectedCityLedgerInvoice.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('City Ledger Invoice', selectedCityLedgerInvoice.value.name, {
                status: 'Open',
            })
                .then((doc) => {
                    selectedCityLedgerInvoice.value.status = doc.status;
                })
        },

    })

}


function closeCityLedgerInvoice() {
    confirm.require({
        header: 'Close City Ledger Invoice ' + selectedCityLedgerInvoice.value.name,
        message: 'Are you sure you want to close this Ledger Invoice' + selectedCityLedgerInvoice.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            if (selectedCityLedgerInvoice.value.balance == 0) {
                updateDoc('City Ledger Invoice', selectedCityLedgerInvoice.value.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    selectedCityLedgerInvoice.value.status = doc.status;
                })
            }else{
                toast.add({ severity: 'warn', summary: "", detail: "This City Ledger Invoice has a pending balance.", life: 15000 })
            }
            
        },

    });
}


function onDeleteFolio() {
    if (!selectedCityLedgerInvoice.value.name) {
        gv.toast('warn', 'Please select a Folio.')
        return
    }

    const dialogRef = dialog.open(ComDialogNote, {
        data: {
            api_url: "utils.delete_doc",
            method: "DELETE",
            confirm_message: "Are you sure you want to delete this folio?",
            data: { doctype: "City Ledger Invoice", name: selectedCityLedgerInvoice.value.name },
        },
        props: {
            header: "Delete City Ledger Invoice" + " " + selectedCityLedgerInvoice.value.name,
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: false,
            closeOnEscape: false,
            position: "top",
            breakpoints: {
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                window.postMessage({ action: "CityLedgerInvoiceDetail" }, "*")
                emit("onClose")
            }
        }
    });


}

function OpenServerReport(report_path, title, parameters = undefined) {

    let params = parameters;
    if (!parameters) {

        params = [
            { name: 'desk_folio', values: [selectedCityLedgerInvoice.value.name] },

        ]
    }
    dialog.open(ComReportServerModal, {
        data: {
            report_path: report_path,
            params: params
        },
        props: {
            header: $t(title),
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints: {
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });
}



onMounted(() => {
    
})

</script>