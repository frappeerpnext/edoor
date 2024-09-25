<template>
    <SplitButton class="border-split-none" :label="$t('Print')" icon="pi pi-print" :model="items" />
</template>
<script setup>
import { useToast } from "primevue/usetoast";
import { ref, inject, useDialog, onMounted,getApi,getDocList } from "@/plugin";
import ComPrintGuestRegistrationCard from "./ComPrintGuestRegistrationCard.vue";
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";

import {i18n} from '@/i18n';
const { t: $t } = i18n.global;

const dialog = useDialog();
const gv = inject("$gv")
const toast = useToast();

const props = defineProps({
    reservation: String,
    reservation_stay: String,
    folio_number:String
})


const items = ref([])
//static print button
items.value.push({
    label: $t("Guest Registration Card"),
    icon: 'pi pi-user-edit',
    command: () => {
        const dialogRef = dialog.open(ComPrintGuestRegistrationCard, {
            data: {
                reservation: props.reservation ?? "",
                reservation_stay: props.reservation_stay ?? "",
            },
            props: {
                header: $t("Guest Registration Card"),
                style: {
                    width: '80vw',
                },
                position:"top",
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


//Confirmattion Voucher
items.value.push({
    label: $t("Confirmation Voucher"),
    icon: 'pi pi-check-circle',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation%20Stay",
                name: props.reservation_stay,
                report_name:"eDoor Reservation Stay Confirmation Voucher",
            },
            props: {
                header: $t("Confirmation Voucher"),
                style: {
                    width: '80vw',
                },
                position:"top",
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

//Folio Summary Report
items.value.push({
    label: $t("Folio Summary Report"),
    icon: 'pi pi-print',
    command: () => {
        
        getApi("reservation.get_guest_folio_list", {
            reservation_stay:props.reservation_stay
        }).then((result) => {

            if (result.message.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:props.reservation_stay,
                        folio: result.message[0],
                        folios:result.message,
                         report_name:  gv.getCustomPrintFormat("eDoor Reservation Stay Folio Summary Report"),
                        view: "print"
                    },
                    props: {
                        header: $t("Folio Summary Report"),
                        style: {
                            width: '80vw',
                        },
                        position:"top",
                        modal: true,
                        maximizable: true,
                        closeOnEscape: false,
                        breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
                    },
                });
            }


        })      
    }
})

//folio detail report
items.value.push({
    label: $t("Folio Detail Report"),
    icon: 'pi pi-print',
    command: () => {
        getApi("reservation.get_guest_folio_list", {
            reservation_stay:props.reservation_stay,
        }).then((result) => {

            if (result.message.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:props.reservation_stay,
                        folio: result.message[0],
                        folios: result.message,
                        report_name: gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"),  
                        view: "print"
                    },
                    props: {
                        header: $t("Folio Detail Report"),
                        style: {
                            width: '80vw',
                        },
                        position:"top",
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


    }
})


//Folio transaction summary by reservation stay
items.value.push({
    label: $t("Folio Summary by Reservation Stay"),
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation%20Stay",
                name: props.reservation_stay,
                report_name:  "eDoor Folio Transaction Summary by Reservation Stay",
                filter_options:["invoice_style","show_account_code","show_room_number","show_summary","show_all_room_rate"],
            },
            props: {
                header: $t("Folio Summary by Reservation Stay"),
                style: {
                    width: '80vw',
                },
                position:"top",
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

//Folio transaction Detaiil by reservation Stay
items.value.push({
    label: $t("Folio Detail by Reservation Stay"),
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation Stay",
                name: props.reservation_stay,
                report_name:  "eDoor Folio Transaction Detail by Reservation Stay",
                filter_options:["invoice_style","show_account_code","show_room_number","show_summary","show_all_room_rate"],
            },
            props: {
                header: $t("Folio Detail by Reservation Stay"),
                style: {
                    width: '80vw',
                },
                position:"top",
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


//Folio List by reservation stay

items.value.push({
    label: $t("Folio List by Reservation Stay"),
    icon: 'pi pi-print',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation Stay",
                name: props.reservation_stay,
                report_name:  "eDoor Folio List by Reservation Stay",
            },
            props: {
                header: $t("Folio List by Reservation Stay"),
                style: {
                    width: '80vw',
                },
                position:"top",
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
 
//reservation stay detail
items.value.push({
    label: $t("Reservation Stay Detail"),
    icon: 'pi pi-check-circle',
    acceptClass: 'border-none crfm-dialog',
    rejectClass: 'hidden',
    acceptIcon: 'pi pi-check-circle',
    acceptLabel: 'Ok',
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation%20Stay",
                name: props.reservation_stay,
                report_name:  gv.getCustomPrintFormat("Reservation Stay Detail"),
            },
            props: {
                header: $t("Reservation Stay Detail"),
                style: {
                    width: '80vw',
                },
                position:"top",
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



onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    if (props.reservation_stay) {
        getDocList('Custom Print Format', {
        fields: [
            'print_format',
            'icon',
            'title',
            'attach_to_doctype'
        ],
        filters: [["property", "=", window.property_name],["visible_in_dynamic_report", "=", 1], ["attach_to_doctype", "=", "Reservation Stay"]]
    })
        .then((doc) => {
            doc.forEach(d => {
                items.value.push({
                    label: d.title,
                    name: d.print_format,
                    icon: d.icon ? d.icon : "pi pi-print",
                    command: (r) => {
                        dialog.open(ComIFrameModal, {
                            data: {
                                doctype: d.attach_to_doctype,
                                name: props.reservation,
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




    }

})
</script>
<style>
.border-split-none button {
    border: 0 !important;
}
.p-button .p-badge{
    line-height: 1.5rem;
    width: 1.5rem;
    height: 1.5rem;
    font-weight:600;
}
.p-splitbutton:not(.spl__btn_cs.sp) button.p-button.p-component.p-splitbutton-defaultbutton {
    border-right: 1px solid var(--btn-border-color) !important;
}
</style>