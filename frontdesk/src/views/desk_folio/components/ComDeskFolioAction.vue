<template>
    <div class="flex pb-1 md:pb-0 overflow-auto justify-content-between align-items-center md:flex-wrap wp-btn-post-in-stay-folio mb-2">
        <div class="flex">
            <template
                v-for="(d, index) in accountGroups"
                :key="index">
                <Button @click="onAddFolioTransaction(d)" class="conten-btn mr-1 white-space-nowrap">
                    Post {{ d.account_name }}
                </Button>
            </template>

            <Button class=" conten-btn white-space-nowrap" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
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
        <div class="flex ms-2 md:ms-0">
            <SplitButton @click="viewFolioSummaryReport" class="spl__btn_cs sp" label="Print" icon="pi pi-print"
                :model="print_menus" />
                <Button   @click="onRefresh()" icon="pi pi-refresh" class="content_btn_b btn-size2 ml-2"></Button>    
        </div>
    </div>

</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc,watch } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';

import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComAddDeskFolio from "@/views/desk_folio/components/ComAddDeskFolio.vue";
 
const props = defineProps({
    folio:Object,
})

const emit = defineEmits(["onClose"])
const accountGroups = ref(window.setting.account_group.filter(r=>r.show_in_desk_folio==1))
const selectedFolio = ref(props.folio)
const dialog = useDialog();
const confirm = useConfirm();
const toast = useToast();
const gv = inject("$gv")
const setting =window.setting
const folio_menu = ref();


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
            doctype: "Desk%20Folio",
            name: selectedFolio.value.name,
            report_name: gv.getCustomPrintFormat("eDoor Desk Folio Invoice Summary"),
            show_letter_head: true,
            filter_options:['invoice_style']
        },
        props: {
            header: "Desk Folio Invoice Summary",
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
    label: "Desk Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {

        viewFolioSummaryReport()
    }
})


//folio detail report
print_menus.value.push({
    label: "Desk Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                doctype: "Desk%20Folio",
                name: selectedFolio.value.name,
                report_name: gv.getCustomPrintFormat("eDoor Desk Folio Invoice Detail"),
                show_letter_head: true,
                filter_options:["show_summary",'invoice_style']
            },
            props: {
                header: "Desk Folio Invoice Detail",
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
    if(props.newDoc){
        props.newDoc.account_group =account_code.name
    }
    if (account_code.is_city_ledger_account==1){
        if(selectedFolio.value.allow_post_to_city_ledger==0){
            toast.add({ severity: 'warn', summary: "", detail: "This reservation is not allow to post charge to city ledger.", life: 5000 })
            return
        }
    }
   
 
     
    if (selectedFolio.value.status == "Open") {
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                    new_doc: {
                        transaction_type: "Desk Folio",
                        transaction_number: selectedFolio.value.name,
                        property: window.property_name,
                        account_group: account_code.name
                    },
                    balance: selectedFolio.value.balance,
                    account_code_filter:{is_desk_folio_account:1}
            },
            props: {
                header: 'Post ' + account_code.account_name + ' to Folio ' + props.folio.name,
                style: {
                    width: '750px',
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

function reloadData(){ 
    window.postMessage({action:"ComDeskFolioDetail"},"*")
    window.postMessage({action:"DeskFolio"},"*")
}
 
const onRefresh = debouncer(() => {
    window.postMessage({action:"ComDeskFolioDetail"},"*")
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
 
    const dialogRef = dialog.open(ComAddDeskFolio, {

        data: {
            name:selectedFolio.value.name,
        },
        props: {
            header: 'Edit Desk Folio' + selectedFolio.value.name,
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
                window.postMessage({action:"ComDeskFolioDetail"},"*")
                window.postMessage({action:"DeskFolio"},"*")
            }
        }
    })
}

function openFolio() {
    
        confirm.require({
        header: 'Open Desk Folio ' + selectedFolio.value.name,
        message: 'Are you sure you want to open this desk folio ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Desk Folio', selectedFolio.value.name, {
                status: 'Open',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status; 
                    window.postMessage({action:"ComDeskFolioDetail"},"*")
                    window.postMessage({action:"DesFkolio"},"*")
                })
        },

    })
    
}


function closeFolio() {
    confirm.require({
        header: 'Close Desk Folio ' + selectedFolio.value.name,
        message: 'Are you sure you want to close this desk folio' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Desk Folio', selectedFolio.value.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status; 
                    window.postMessage({action:"ComDeskFolioDetail"},"*")
                    window.postMessage({action:"DeskFolio"},"*")
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
            data: { doctype: "Desk Folio", name: selectedFolio.value.name },
        },
        props: {
            header: "Delete Desk Folio" + " " + selectedFolio.value.name,
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
                window.postMessage({action:"DeskFolio"},"*") 
                emit("onClose") 
            }
        }
    });




}

</script>
 