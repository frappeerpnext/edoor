<template>
    <div class="flex justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio mb-3">
        <div>
            <Button v-for="(d, index) in setting?.account_group.filter(r => r.show_in_shortcut_menu == 1)" :key="index"
                @click="onAddFolioTransaction(d)" class="conten-btn mr-1">Post {{ d.account_name }}</Button>

            <Button class="conten-btn" icon="pi pi-chevron-down" iconPos="right" type="button" label="Folio Options"
                @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu" :popup="true">
                <template #end>
                    <button v-for="(d, index) in setting?.account_group.filter(r => r.show_in_shortcut_menu == 0)"
                        :key="index" @click="onAddFolioTransaction(d)"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i :class="d.icon" />
                        <span class="ml-2 ">Post {{ d.account_name }}</span>
                    </button>
                    <button v-if="!rs.selectedFolio.is_master" @click="MarkasMasterFolio"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-verified" />
                        <span class="ml-2"> Mark as Master Folio</span>
                    </button>

                    <button @click="toggle"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-arrow-right-arrow-left" />
                        <span class="ml-2">Transfer Items</span>
                    </button>

                    <button @click="closeFolio" v-if="rs.selectedFolio?.status == 'Open'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-ban" />
                        <span class="ml-2">Close Folio</span>
                    </button>
                    <button @click="EditFolio(true)"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-file-edit" />
                        <span class="ml-2">Edit Folio </span>
                    </button>

                    <button @click="openFolio" v-if="rs.selectedFolio?.status == 'Closed'"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-check-circle" />
                        <span class="ml-2">Open Folio</span>
                    </button>

                    <button @click="openNote = true"
                        class="w-full p-link flex align-items-center py-2 px-3 text-color hover:surface-200 border-noround">
                        <i class="pi pi-times-circle" />
                        <span class="ml-2">Delete Folio</span>
                    </button>

                </template>
            </Menu>
        </div>
        <div>
            <SplitButton class="spl__btn_cs sp" label="Print" icon="pi pi-print" :model="print_menus" />
        </div>
    </div>
    <ComDialogNote :header="`Delete Folio - ${rs.selectedFolio.name}`" :visible="openNote" :loading="loading"
        @onOk="deleteFilio" @onClose="onCloseNote" />
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast, deleteApi } from '@/plugin';
import ComNote from '@/components/form/ComNote.vue';
import Menu from 'primevue/menu';

import ComNewReservationStayFolio from './ComNewReservationStayFolio.vue';
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
const socket = inject("$socket")
const dialog = useDialog();
const confirm = useConfirm();
const frappe = inject('$frappe');
const call = frappe.call();
const db = frappe.db();
const toast = useToast();
const rs = inject("$reservation_stay")
const gv = inject("$gv")
const openNote = ref(false)
const loading = ref(false)

const setting = JSON.parse(localStorage.getItem("edoor_setting"))

const folio_menu = ref();


const toggle = (event) => {
    folio_menu.value.toggle(event);
}


const print_menus = ref([])
//Folio Summary Report
print_menus.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {

        dialog.open(ComPrintReservationStay, {
            data: {
                doctype: "Reservation%20Stay",
                reservation_stay: rs.reservationStay.name,
                folio_number: rs.selectedFolio.name,
                report_name: "eDoor%20Reservation%20Stay%20Folio%20Summary%20Report",
                view: "print"
            },
            props: {
                header: "Folio Summary Report",
                style: {
                    width: '80vw',
                },
                modal: true,
                maximizable: true,
                position: top
            },
        });
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
                reservation_stay: rs.reservationStay.name,
                folio_number: rs.selectedFolio.name,
                report_name: "eDoor%20Reservation%20Stay%20Folio%20Detail%20Report",
                view: "print"
            },
            props: {
                header: "Folio Summary Report",
                style: {
                    width: '80vw',
                },
                modal: true,
                maximizable: true,
                position: top
            },
        });
    }


})



function onAddFolioTransaction(account_code) {
    if (rs.selectedFolio.status == "Open") {
        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                folio_number: rs.selectedFolio.name,
                account_group: account_code.name,
                balance: rs.totalDebit - rs.totalCredit
            },
            props: {
                header: 'Post ' + account_code.account_name + ' to Folio ' + rs.selectedFolio.name,
                style: {
                    width: '50vw',
                },

                modal: true,
                position: "top"
            },
            onClose: (options) => {
                const data = options.data;

                if (data) {

                    rs.onLoadReservationFolios()
                    rs.onLoadFolioTransaction(rs.selectedFolio)
                    rs.getChargeSummary(rs.reservationStay.name)
                    setTimeout(function () {

                        rs.getReservationStay(rs.reservationStay.name);
                        //send websocket to update reservation detail
                        socket.emit("RefreshReservationDetail", rs.reservation.name)
                    }, 2000)
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

function showPrintPreview(data) {

    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            doctype: "Folio Transaction",
            name: data.name,
            report_name: data.print_format,
            show_letter_head:true
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

function EditFolio(is_edit) {
    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            reservation_stay: rs.reservationStay,
            is_edit: is_edit
        },
        props: {
            header: 'Edit Folio  ' + rs.selectedFolio.name,
            style: {
                width: '50vw',
            },
            modal: true
        },
        onClose: (options) => {
            let data = options.data;
            if (data != undefined) {
                rs.onLoadReservationFolios(data.name)
                socket.emit("RefreshReservationDetail", rs.reservation.name)
            }
        }
    })
}
function MarkasMasterFolio() {
    confirm.require({
        target: event.currentTarget,
        header: 'Mark Folio ' + rs.selectedFolio.name + ' as Master Folio',
        message: 'Do you want to Mark this Folio ' + rs.selectedFolio.name + ' as Master Folio?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptLabel: 'Ok',
        acceptIcon: 'pi pi-check-circle',

        accept: () => {
            db.updateDoc('Reservation Folio', rs.selectedFolio.name, {
                is_master: 1,
            })
                .then((doc) => {
                    rs.folios.forEach(r => r.is_master = false);
                    rs.selectedFolio.is_master = doc.is_master;
                    toast.add({
                        severity: 'success', summary: 'Mark Folio as Master Folio',
                        detail: 'Mark Folio as Master Folio Successfully', life: 3000
                    });
                })
        },
    })
}
function openFolio() {
    confirm.require({
        target: event.currentTarget,
        header: 'Open Folio ' + rs.selectedFolio.name,
        message: 'Are you sure you want to Open Folio ' + rs.selectedFolio.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            db.updateDoc('Reservation Folio', rs.selectedFolio.name, {
                status: 'Open',
            })
                .then((doc) => {
                    rs.selectedFolio.status = doc.status;
                    toast.add({ severity: 'success', summary: 'Open Folio', detail: 'Open Folio successfully', life: 3000 });

                })
        },

    })
}
function onCloseNote() {
    openNote.value = false
}
function closeFolio() {
    confirm.require({
        target: event.currentTarget,
        header: 'Close Folio ' + rs.selectedFolio.name,
        message: 'Are you sure you want to Close Folio ' + rs.selectedFolio.name + '?',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        rejectClass: 'hidden',
        accept: () => {
            db.updateDoc('Reservation Folio', rs.selectedFolio.name, {
                status: 'Closed',
            })
                .then((doc) => {
                    rs.selectedFolio.status = doc.status;
                    toast.add({ severity: 'success', summary: 'Close Folio', detail: 'Close Folio successfully', life: 3000 });

                })
        },

    });
}
function deleteFilio(note) {
    if (!rs.selectedFolio.name) {
        gv.toast('warn', 'Please select a Folio.')
    }
    loading.value = true
    deleteApi('utils.delete_doc', { doctype: "Reservation Folio", name: rs.selectedFolio.name, note: note }, "Delete Folio Successfully")
        .then((result) => {
            rs.onLoadReservationFolios().then(() => {
                if (rs.folios.length > 0) {
                    // default select
                    let defaultSelectFolio = ref(rs.folios.find(r => r.is_master == true))
                    if (!defaultSelectFolio.value) {
                        defaultSelectFolio.value = rs.folios[0]
                    }
                    rs.onLoadFolioTransaction(defaultSelectFolio.value)
                    socket.emit("RefreshReservationDetail", rs.reservation.name)
                }
                loading.value = false;
                openNote.value = false
            })
        }).catch((error) => {
            loading.value = false;
        })

}
</script>