<template>
    
    <div class="overflow-x-auto overflow-y-hidden lg:overflow-y-hidden">
        <div class="flex gap-1 justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio -mt-3 -mb-2 overflow-x-auto lg:overflow-x-hidden w-max lg:w-full">
            <slot name="button"></slot>
            <div>
                <template
                    v-for="(d, index) in accountGroups?.filter(r => r.show_in_shortcut_menu == 1)"
                    :key="index">
                    <Button @click="onAddFolioTransaction(d)" class="conten-btn mr-1"
                        v-if="showAccountGroup(d)">
             {{ $t('Post ' + d.account_name)  }}
                    </Button>
                </template>

                <Button class="conten-btn" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
                    @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
                <Menu ref="folio_menu" id="folio_menu" :popup="true">
                    <template #end>
                        <template
                            v-for="(d, index) in accountGroups?.filter(r => r.show_in_shortcut_menu == 0)"
                            :key="index">
                            <button
                            v-if="showAccountGroup(d)"
                                @click="onAddFolioTransaction(d)"
                                class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                                <i :class="d.icon" />
                                <span class="ml-2 ">{{ $t('Post ' + d.account_name) }}</span>
                            </button>
                        </template>
                        <button v-if="!selectedFolio.is_master" @click="MarkasMasterFolio"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-verified" />
                            <span class="ml-2"> {{ $t('Mark as Master Folio') }} </span>
                        </button>

                        <button @click="onTransferFolioItem"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-arrow-right-arrow-left" />
                            <span class="ml-2"> {{ $t('Transfer Items') }} </span>
                        </button>
                        
                        <button v-if="!selectedFolio?.tax_invoice_number" @click="generateTaxInvoice(`${isMobile ? 'top' : 'center'}`)" 
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-file" />
                            <span class="ml-2">{{$t('Generate Tax Invoice')}}</span>
                        </button>
                        <button @click="closeFolio(`${isMobile ? 'top' : 'center'}`)" v-if="selectedFolio?.status == 'Open'"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-ban" />
                            <span class="ml-2">{{$t('Close Folio')}}</span>
                        </button>
                        <button @click="EditFolio(true)"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-file-edit" />
                            <span class="ml-2">{{ $t('Edit Folio') }}  </span>
                        </button>

                        <button @click="openFolio" v-if="selectedFolio?.status == 'Closed'"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-check-circle" />
                            <span class="ml-2"> {{ $t('Open Folio') }} </span>
                        </button>

                        <button @click="deleteFilio"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-times-circle" />
                            <span class="ml-2"> {{ $t('Delete Folio') }} </span>
                        </button>
                        <button v-if="displayViewFolio == 0" @click="savedisplayView(1)"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-eye" />
                            <span class="ml-2"> {{ $t('Show Package Package') }} </span>
                        </button>
                        <button v-if="displayViewFolio == 1" @click="savedisplayView(0)"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-eye" />
                            <span class="ml-2"> {{ $t('Hide Breakdown Package') }} </span>
                        </button>
                        <button @click="onAuditTrail"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i class="pi pi-history" />
                            <span class="ml-2"> {{ $t('Audit Trail') }} </span>
                        </button>

                    </template>
                </Menu>
            </div>
            <div class="flex items-center">
                <span>
                    <SplitButton @click="viewFolioSummaryReport" class="spl__btn_cs sp p-3" :label="$t('Print')" icon="pi pi-print"
                        :model="print_menus" />    
                    <Button @click="onRefresh()" v-tippy="$t('Refresh')" icon="pi pi-refresh" style="font-size: .98rem !important;" class="content_btn_b ml-2 m-3 p-2" :loading="loading"></Button>
                </span>
            </div>
            
        </div>
        <Message  v-if="selectedFolio?.tax_invoice_number"  severity="info">
                    <div class="flex justify-content-between align-items-center w-full">
                        <div>
                             This Folio has Generate {{selectedFolio.tax_invoice_type}} - {{ selectedFolio?.tax_invoice_number }}
                        </div>
                        <div class="ms-5">
                            <Button class="conten-btn" style="background: transparent;" @click="viewfoliotaxinvoicedetail">
<i class="pi pi-print me-2" />
                            Print Tax Invoice
                            </Button>   
                        </div>
                    </div>
                  
                </Message>
    </div>
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc,watch,onMounted,getDocList,getDoc } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';

import ComNewReservationStayFolio from '@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue';
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransfer from "@/views/reservation/components/reservation_stay_folio/ComFolioTransfer.vue";
import ComGenerateTaxInvoice from "@/views/reservation/components/ComGenerateTaxInvoice.vue";
import ComAuditTrail from '@/components/layout/components/ComAuditTrail.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const displayViewFolio = ref('');

const props = defineProps({
    doctype:String,
    folio:Object,
    newDoc:Object,
    accountCodeFilter:Object,
    accountGroups:Object,
    loading:Boolean,
    parentComponent: String
    
})

const isMobile = ref(window.isMobile)
const emit = defineEmits(['onAuditTrail', "onRefresh"])
const selectedFolio = ref(props.folio)
const transaction = ref([])

const dialog = useDialog();
const confirm = useConfirm();
const toast = useToast();
const gv = inject("$gv")
const rs = inject("$reservation_stay")
const setting =window.setting
const folio_menu = ref();

function showAccountGroup(account_code){
    if (selectedFolio.value.allow_post_to_city_ledger==0){
        if((account_code.is_city_ledger_account || 0) == 1){
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
    
    const print_format = window.setting.default_folio_print_format?window.setting.default_folio_print_format :"eDoor Reservation Stay Folio Summary Report";
    let filter =  [ ["reservation_stay", "=", props.folio.reservation_stay]]
    
    if (props.parentComponent=="Reservation"){
        filter = [ ["reservation", "=", props.folio.reservation]]
    }
    getDocList("Reservation Folio", {
            filters: [ ["reservation_stay", "=", props.folio.reservation_stay]],
            limit:100,
            fields:["name","reservation_stay"]
        }).then((docs) => {


            
    dialog.open(ComPrintReservationStay, {
        data: {
            doctype: "Reservation%20Stay",
            reservation_stay: selectedFolio.value.reservation_stay,
            folio: selectedFolio.value,
            folios: docs,
            report_name:gv.getCustomPrintFormat("eDoor Reservation Stay Folio Summary Report"),
            view: "print"
        },
        props: {
            header: $t("Folio Summary Report"),
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
function viewfoliotaxinvoicedetail() {
    getDoc("Tax Invoice", selectedFolio.value.tax_invoice_number).then(r=>{
        dialog.open(ComIFrameModal, {
        data: {
            doctype: "Tax Invoice",
            name: selectedFolio.value.tax_invoice_number,
            report_name: r.default_print_format?gv.getCustomPrintFormat(r.default_print_format) :  gv.getCustomPrintFormat("Invoice"),
            letterhead: r.default_letterhead || "Tax Letterhead",
            filter_options:["show_vattin"]
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
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });
    })
    

}

function getTaxInvoice(){
    if(selectedFolio.value.tax_invoice_number){
        getDoc("Tax Invoice", selectedFolio.value.tax_invoice_number).then(r=>{
            selectedFolio.value.tax_invoice_type = r.tax_invoice_type
        })
    }
    
}
//Folio Summary Report
print_menus.value.push({
    label: $t("Folio Summary Report"),
    icon: 'pi pi-print',
    command: () => {

        viewFolioSummaryReport()
    }
})




//folio detail report

print_menus.value.push({
    label: $t("Folio Detail Report"),
    icon: 'pi pi-print',
    command: () => { getDocList("Reservation Folio", {
            filters: [ ["reservation_stay", "=", props.reservation_stay]],
            limit:100,
            fields:["name","reservation_stay"]
        }).then((docs) => {

        dialog.open(ComPrintReservationStay, {
            data: {
                doctype: "Reservation%20Stay",
                reservation_stay: selectedFolio.value.reservation_stay,
               folio: selectedFolio.value,
            folios: docs,
                report_name:gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"),
                view: "print"
            },
            props: {
                header: $t("Folio Detail Report"),
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


})

if (selectedFolio?.value?.tax_invoice_number) {
    print_menus.value.push({
    label: $t("Print Tax Invoice"),
    icon: 'pi pi-print',
    command: () => {
        viewfoliotaxinvoicedetail()
    }
})  
}

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
                    new_doc: props.newDoc?props.newDoc:{
                        transaction_type: "Reservation Folio",
                        transaction_number: selectedFolio.value.name,
                        reservation: selectedFolio.value.reservation,
                        reservation_stay: selectedFolio.value.reservation_stay,
                        property: window.property_name,
                        account_group: account_code.name,
                        guest:selectedFolio.value.guest,
                        business_source:selectedFolio.value.business_source,
                    },
                    balance: selectedFolio.value.balance,
                    business_source: selectedFolio.value.business_source,
                    account_code_filter:props.accountCodeFilter,
                    show_room:true,
                    show_source_reservation_stay:true
            },
            props: {
                header: $t('Post ' + account_code.account_name + ' to Folio') + ' ' + props.folio.name,
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

function reloadData(){
 
    window.postMessage({action:"load_reservation_folio_list",reservation:selectedFolio.value.reservation},"*")
    
    // window.postMessage({action:"load_folio_transaction",name:selectedFolio.value.name},"*")

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


function generateTaxInvoice() {
 
 const dialogRef = dialog.open(ComGenerateTaxInvoice, {

     data: {
         property: window.property_name,
         name:selectedFolio.value.name,
         document_type:"Reservation Folio"
     },
     props: {
         header: "Generate Tax Invoice",
         style: {
             width: '30vw',
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
       
             selectedFolio.value.tax_invoice_number = data.message.name
             selectedFolio.value.tax_invoice_type = data.message.tax_invoice_type


         }
     }
 })
}

function EditFolio() {
 
    const dialogRef = dialog.open(ComNewReservationStayFolio, {

        data: {
            property: window.property_name,
            name:selectedFolio.value.name,
            reservation_stay: selectedFolio.value.reservation_stay,
            guest: selectedFolio.value.guest,
            note: selectedFolio.value.note,
            show_in_pos_transfer:selectedFolio.value.show_in_pos_transfer
        },
        props: {
            header: $t('Edit Folio') + ' ' + selectedFolio.value.name,
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
          
                window.postMessage({action:"load_reservation_folio_list"},"*")
                window.postMessage({action:"load_reservation_stay_folio_list"},"*")
                window.postMessage({action:"ReservationDetail"},"*")

            }
        }
    })
}

function MarkasMasterFolio() {
    if (selectedFolio.value.status == "Open") {
        confirm.require({
            header: 'Mark Folio ' + selectedFolio.value.name + ' as Master Folio',
            message: 'Do you want to Mark this Folio ' + selectedFolio.value.name + ' as Master Folio?',
            icon: 'pi pi-info-circle',
            acceptClass: 'border-none crfm-dialog',
            rejectClass: 'hidden',
            acceptLabel: 'Ok',
            acceptIcon: 'pi pi-check-circle',

            accept: () => {
                updateDoc('Reservation Folio', selectedFolio.value.name, {
                    is_master: 1,
                },"Mark Folio as Master Folio Successfully")
                    .then((doc) => {
                        window.postMessage({action:"load_reservation_folio_list",selected_folio_name:selectedFolio.value.name})
                        window.postMessage({action:"GuestLedger"},"*")
                        window.postMessage({action:"GuestLedgerTransaction"},"*")

                    })
            },
        })
    }
    else {
        gv.toast('warn', 'Folio closed not allow to Mark as Master Folio.')
    }

}

function openFolio() {

    if(rs.reservationStay.reservation_status=='No Show'){
        gv.toast('warn', 'No Show reservation is not allow to open folio.')
    }
    else{
        confirm.require({
        header: 'Open Folio ' + selectedFolio.value.name,
        message: 'Are you sure you want to Open Folio ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Reservation Folio', selectedFolio.value.name, {
                status: 'Open',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status;
                    window.postMessage({action:"GuestLedger"},"*")
                    window.postMessage({action:"ReservationStayList"},"*")
                    window.postMessage({action:"GuestLedgerTransaction"},"*")
                })
        },

    })
    }
    
}

const onRefresh = debouncer(() => {
   emit("onRefresh")
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

function closeFolio(position) {
    confirm.require({
        header: $t('Close Folio') + ' '  + selectedFolio.value.name,
        message: 'Are you sure you want to Close Folio ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        position: position,
        accept: () => {
            updateDoc('Reservation Folio', selectedFolio.value.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status;
                    window.postMessage({action:"ReservationStayList"},"*")
                    window.postMessage({action:"GuestLedger"},"*")
                    window.postMessage({action:"GuestLedgerTransaction"},"*")
                })
        },

    });
}

function deleteFilio() {
    if (!selectedFolio.value.name) {
        gv.toast('warn', 'Please select a Folio.')
        return
    }

    const dialogRef = dialog.open(ComDialogNote, {
        data: {
            api_url: "utils.delete_doc",
            method: "DELETE",
            confirm_message: "Are you sure you want to delete this folio?",
            data: { doctype: "Reservation Folio", name: selectedFolio.value.name },
        },
        props: {
            header: $t("Delete Folio") + " " + selectedFolio.value.name,
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
                window.postMessage({action:"load_reservation_folio_list"},"*")
                window.postMessage({action:"load_reservation_stay_folio_list"},"*")
                
            }
        }
    });




}

function onTransferFolioItem() {
    if (selectedFolio.value.status == "Open") {
    const selectedFolioTransactions = JSON.parse( sessionStorage.getItem("folo_transaction_table_state_" + selectedFolio.value.name) ).selection
    
    if (selectedFolioTransactions.length == 0) {
        toast.add({ severity: 'warn', summary: "", detail: "Please select a filio transaction to transfer", life: 3000 })
        return
    }

    const dialogRef = dialog.open(ComFolioTransfer, {
        data: { 
                reservation:selectedFolio.value.reservation,
                reservation_stay:selectedFolio.value.reservation_stay,
                folio_number: selectedFolio.value.name,
                folio_transaction:selectedFolioTransactions,
                
            },
        props: {
            header: 'Folio Transfer',
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
        onClose: (options) => {
            const data = options.data;
 
            if (data) {
                selectedFolioTransactions.value=[]
              
                reloadData()

                setTimeout(() => {   
                    window.postMessage({action:"ReservationDetail"},"*")
                }, 3000);

                
            }
        }
    })
}else {
    toast.add({ severity: 'warn', summary: "", detail: "Folio is already closed.", life: 3000 }) 
}
}



const arr = ref()

function onAuditTrail() {
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation',
            docname: rs.reservation.name,
            referenceTypes:[
                { doctype: 'Reservation Folio', label: 'Reservation Folio' },
                { doctype: 'Folio Transaction', label: 'Folio Transaction' },
                
            ],
            filter_key:"custom_reservation"

        },
        props: {
            header: $t('Audit Trail'),
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            //
        }
    });
}


function savedisplayView(value) {
    displayViewFolio.value = value  
    localStorage.setItem('displayViewFolioTransaction', value);   
    window.postMessage({action:"load_reservation_folio_list"},"*")   
    window.postMessage({action:"load_reservation_stay_folio_list"},"*")
}; 



onMounted(()=>{
    const saveDisplayViewFolioTransaction = localStorage.getItem('displayViewFolioTransaction');
    if (saveDisplayViewFolioTransaction) {
        displayViewFolio.value = saveDisplayViewFolioTransaction;
    }else{
        displayViewFolio.value = 0
    }
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
getDocList ('Custom Print Format', {
     fields: [
         'print_format',
         'icon',
         'title',
         'attach_to_doctype'
     ],
     filters: [["property", "=", window.property_name], ["attach_to_doctype", "=", props.doctype]]
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
                             report_name: gv.getCustomPrintFormat(d.print_format),
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

     getTaxInvoice()
})
</script>
 