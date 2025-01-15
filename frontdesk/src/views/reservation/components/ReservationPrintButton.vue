<template>
    <SplitButton :label="$t('Print')" icon="pi pi-print" :model="items" />
</template>
<script setup>
import ComIFrameModal from "@/components/ComIFrameModal.vue";

import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComReportServerModal  from "@/components/ComReportServerModal.vue";
import { ref, inject, useDialog, onMounted,getDocList,useToast,getApi } from "@/plugin";
 
import {i18n} from '@/i18n';
import { renderSlot } from "vue";
const { t: $t } = i18n.global;
const toast = useToast()
const dialog = useDialog();

const props = defineProps({
    reservation: String,
})
const gv = inject("$gv")
const items = ref([
    {
        label: $t("eDoor Group Registration Card"),
        icon: 'pi pi-check-circle',

        command: () => {
            if (window.setting.server_report_url) {
            OpenServerReport("/Front Desk/rptGroupGuestRegistrationCard", "Group Guest Registration Card")

        }
        else {
            openReport("eDoor Group Registration Card",
                {
                    "doctype": "Reservation",
                    name: props.reservation ?? "",
                    report_name: gv.getCustomPrintFormat("eDoor Group Registration Card"),
                    filter_options: ["show_rate"],

                    server_report_params:[
                        { 
                            name: 'reservation', values: [props.reservation] 
                        }

                    ]
                }
            )
        }
        },
    },
    {
        label: $t("Confirmation Voucher"),
        icon: 'pi pi-check-circle',

        command: () => {
            if (window.setting.server_report_url) {
            OpenServerReport("/Front Desk/rptReservationConfirmationVoucher", "Group Confirmation Voucher")
        }
        else {
            openReport("Confirmmation Voucher",
                {
                    "doctype": "Reservation",
                    name: props.reservation ?? "",
                    report_name: gv.getCustomPrintFormat("eDoor Reservation Confirmation Voucher"),
                }
            )
        }
        },
    },
    {
    label: $t("Folio Summary Report"),
    icon: 'pi pi-print',
    command: () => {
        getApi("reservation.get_guest_folio_list", {
            reservation:props.reservation
        }).then((result) => {

            if (result.message.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                if (window.setting.server_report_url) {
                    const params = [
                        { name: 'reservation', values: [props.reservation] },
                        { name: 'reservation_folio', values: [result.message[0].name] }
                    ]
                    OpenServerReport("/Front Desk/rptReservationStayFolioSummary", "Folio Summary", params)

                }
                else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:result.message[0].reservation,
                        folio: result.message[0],
                        folios: result.message,
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
            }
        })

    }
},
    
{
    label: $t("Folio Detail Report"),
    icon: 'pi pi-print',
    command: () => {
        getApi("reservation.get_guest_folio_list", {
            reservation:props.reservation
        }).then((result) => {

            if (result.message.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Detail Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                if (window.setting.server_report_url) {
                    const params = [
                    { name: 'reservation', values: [props.reservation] },
                        { name: 'reservation_folio', values: [result.message[0].name] }
                    ]
                    OpenServerReport("/Front Desk/rptReservationStayFolioDetail", "Folio Detail", params)

                }
                else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:result.message[0].reservation_stay,
                        folio: result.message[0],
                        folios: result.message,
                        report_name:  gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"),
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
                        closeOnEscape: false,
                        breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
                    },
                });
            }
            }
        })

    }
},
    {
        label: $t("Folio Summary by Reservation"),
        icon: 'pi pi-print',
        command: () => {
            if (window.setting.server_report_url) {
                    
                    OpenServerReport("/Front Desk/rptFolioSummaryByReservation", "Folio Summary by Reservation")

                }
                else {
            openReport("Folio Summary by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: ("eDoor Folio Transaction Summary by Reservation"),
                    show_letter_head: true,
                    filter_options: ["invoice_style", "show_room_number", "show_summary", "show_account_code"],
                })
                }
        },
    },
    {
        label: $t("Folio Detail by Reservation"),
        icon: 'pi pi-print',
        command: () => {
            if (window.setting.server_report_url) {
                    
                    OpenServerReport("/Front Desk/rptFolioDetailByReservation", "Folio Detail by Reservation")

                }
                else {
            openReport("Folio Detail by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: "eDoor Folio Transaction Detail by Reservation",
                    show_letter_head: true,
                    filter_options: ["invoice_style", "show_room_number", "show_summary", "show_account_code"],
                })
            }
        },
    },
    {
        label: $t("Folio List by Reservation"),
        icon: 'pi pi-print',
        command: () => {
            if (window.setting.server_report_url) {
                    
                    OpenServerReport("/Front Desk/rptFolioListByReservation", "Folio List by Reservation")

                }
                else {
            openReport("Folio List by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: "eDoor Folio List by Reservation",
                    show_letter_head: true
                })
            }
        },
    },
   
    
    {

        label: $t("Reservation Detail"),
        icon: 'pi pi-check-circle',
        command: () => {
            if (window.setting.server_report_url) {
                    
                    OpenServerReport("/Front Desk/rptReservationDetail", "Reservation Detail")

                }
                else {
            openReport("Reservation Detail", {
                "doctype": "Reservation",
                name: props.reservation ?? "",
                report_name: ("Reservation Detail"),
            },)
        }
        },
    },
])


// Generaal transaction

items.value.push({
    label: $t("General Journal Transaction"),
    icon: 'pi pi-check-circle',
    command: () => {

        dialog.open(ComReportServerModal, {
            data: {
                report_path: "/Front Desk/rptGeneralJournalTransactionForReservation",
                params:[
                        {name: 'reservation', values: [props.reservation] }
                ]
            },
            props: {
                header: $t("General Journal Transaction"),
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

         
    }
})



function openReport(title, data) {
    dialog.open(ComIFrameModal, {
        data: data,
        props: {
            header: $t(title),
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            breakpoints:{
                '960px': '100vw',
                '640px': '100vw'
            },
        },
    });
}



function OpenServerReport(report_path, title, parameters = undefined) {
   
    let params = parameters;
    if (!parameters) {
        
        params = [
            { name: 'reservation', values: [props.reservation] },
            { name: 'reservation_stay', values: [""] }
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
        filters: [["property", "=", window.property_name], ["attach_to_doctype", "=", "Reservation"]]
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


})



</script>