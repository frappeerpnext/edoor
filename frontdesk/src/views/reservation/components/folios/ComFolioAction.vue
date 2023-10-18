<template>
    <div class="flex justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio mb-3">
        <div>
            <template
                v-for="(d, index) in setting?.account_group.filter(r => r.show_in_shortcut_menu == 1 && r.show_in_folio_tab == 1)"
                :key="index">
                <Button @click="onAddFolioTransaction(d)" class="conten-btn mr-1"
                    v-if="(d.is_city_ledger_account || 0) == 0 || ((d.is_city_ledger_account || 0) == 1 && (folio.allow_post_to_city_ledger || 0) == 1)">Post
                    {{ d.account_name }}</Button>
            </template>

            <Button class="conten-btn" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
                @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu" :popup="true">
                <template #end>
                    <template
                        v-for="(d, index) in setting?.account_group.filter(r => r.show_in_shortcut_menu == 0 && r.show_in_folio_tab == 1)"
                        :key="index">
                        <button
                            v-if="d.is_city_ledger_account == 0 || (d.is_city_ledger_account == 1 && rs.reservationStay.allow_post_to_city_ledger == 1)"
                            @click="onAddFolioTransaction(d)"
                            class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                            <i :class="d.icon" />
                            <span class="ml-2 ">Post {{ d.account_name }}</span>
                        </button>
                    </template>
                    <button v-if="!selectedFolio.is_master" @click="MarkasMasterFolio"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-verified" />
                        <span class="ml-2"> Mark as Master Folio</span>
                    </button>

                    <button @click="onTransferFolioItem"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-arrow-right-arrow-left" />
                        <span class="ml-2">Transfer Items</span>
                    </button>

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

                    <button @click="deleteFilio"
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
        </div>
    </div>


</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, useToast, updateDoc,watch,onMounted } from '@/plugin';

import ComDialogNote from '@/components/form/ComDialogNote.vue';
import Menu from 'primevue/menu';
import ComNewReservationStayFolio from '@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue';
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
import ComFolioTransfer from "@/views/reservation/components/reservation_stay_folio/ComFolioTransfer.vue";
 
const props = defineProps({
    folio:Object
})

const selectedFolio = ref(props.folio)


const dialog = useDialog();
const confirm = useConfirm();
const toast = useToast();
const gv = inject("$gv")
const setting =window.setting
const folio_menu = ref();
const {loadReservationFolioList} = inject("reservation")

 
//trach user select new folio and reload folio information

watch(() => props.folio, (newValue, oldValue) => {
   
    selectedFolio.value = newValue
 
})

const toggle = (event) => {
    folio_menu.value.toggle(event);
}

const print_menus = ref([])

function viewFolioSummaryReport() {

    dialog.open(ComPrintReservationStay, {
        data: {
            doctype: "Reservation%20Stay",
            reservation_stay: selectedFolio.value.reservation_stay,
            folio_number: selectedFolio.value.name,
            report_name: gv.getCustomPrintFormat("eDoor Reservation Stay Folio Summary Report"),
            view: "print"
        },
        props: {
            header: "Folio Summary Report",
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false

        },
    });
}

//Folio Summary Report
print_menus.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {

        viewFolioSummaryReport()
    }
})


//folio detail report
print_menus.value.push({
    label: "Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComPrintReservationStay, {
            data: {
                doctype: "Reservation%20Stay",
                reservation_stay: selectedFolio.value.reservation_stay,
                folio_number: selectedFolio.value.name,
                report_name:gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"),
                view: "print"
            },
            props: {
                header: "Folio Summary Report",
                style: {
                    width: '80vw',
                },
                position: "top",
                modal: true,
                maximizable: true,
                closeOnEscape: false

            },
        });
    }


})

function onAddFolioTransaction(account_code) {
    if (selectedFolio.value.status == "Open") {
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                new_doc: {
                    transaction_type: "Reservation Folio",
                    transaction_number: selectedFolio.value.name,
                    reservation: selectedFolio.value.reservation,
                    reservation_stay: selectedFolio.value.reservation_stay,
                    property: window.property_name,
                    account_group: account_code.name
                },
                balance: selectedFolio.value.total_debit - selectedFolio.value.total_credit
            },
            props: {
                header: 'Post ' + account_code.account_name + ' to Folio ' + props.folio.name,
                style: {
                    width: '50vw',
                },

                modal: true,
                position: "top",
                closeOnEscape: false
            },
            onClose: (options) => {
                const data = options.data;
 
     
                if (data) {
                    reloadData()
                  

                    //will change this to use websocket

                    // rs.onLoadReservationFolios()
                    // rs.onLoadFolioTransaction(selectedFolio.value)
                    // rs.getChargeSummary(selectedFolio.value.reservation_stay)
                    // setTimeout(function () {
                    //     rs.getReservationStay(selectedFolio.value.reservation_stay);
                    // }, 2000)

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

    window.postMessage({action:"load_folio_transaction",name:selectedFolio.value.name},"*")

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
 
    const dialogRef = dialog.open(ComNewReservationStayFolio, {

        data: {
            folio:selectedFolio.value
        },
        props: {
            header: 'Edit Folio  ' + selectedFolio.value.name,
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
          
                loadReservationFolioList()
                window.socket.emit("ReservationDetail", selectedFolio.value.reservation)

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
                        loadReservationFolioList(selectedFolio.value.name)
                    })
            },
        })
    }
    else {
        gv.toast('warn', 'Folio closed not allow to Mark as Master Folio.')
    }

}

function openFolio() {
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
                    // rs.onLoadReservationFolios()
                    window.socket.emit("ReservationStayList", { property: window.property_name })
                })
        },

    })
}


function closeFolio() {
    confirm.require({
        header: 'Close Folio ' + selectedFolio.value.name,
        message: 'Are you sure you want to Close Folio ' + selectedFolio.value.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            updateDoc('Reservation Folio', selectedFolio.value.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    selectedFolio.value.status = doc.status;
                   
                    window.socket.emit("ReservationStayList", { property: window.property_name })

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
            header: "Delete Folio Number" + " " + selectedFolio.value.name,
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
                loadReservationFolioList()
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
                width: '75vw',
            },

            modal: true,
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
 
            if (data) {
                selectedFolioTransactions.value=[]
              
                reloadData()

                setTimeout(() => {                  
                    window.socket.emit("ReservationDetail", selectedFolio.value.reservation)    
                    window.socket.emit("Frontdesk", selectedFolio.value.reservation)    
                }, 3000);

                
            }
        }
    })
}else {
    toast.add({ severity: 'warn', summary: "", detail: "Folio is already closed.", life: 3000 }) 
}
}





 
 
</script>
 