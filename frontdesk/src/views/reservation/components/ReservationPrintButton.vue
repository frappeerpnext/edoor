<template>
    <SplitButton :label="$t('Print')" icon="pi pi-print" :model="items" />
</template>
<script setup>
import ComIFrameModal from "@/components/ComIFrameModal.vue";

import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import { ref, inject, useDialog, onMounted,getDocList,useToast } from "@/plugin";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const toast = useToast()
const dialog = useDialog();

const props = defineProps({
    reservation: String,
})
const gv = inject("$gv")
const items = ref([
    {
        label: $t("Confirmation Voucher"),
        icon: 'pi pi-check-circle',

        command: () => {

            openReport("Confirmmation Voucher",
                {
                    "doctype": "Reservation",
                    name: props.reservation ?? "",
                    report_name: ("eDoor Reservation Confirmation Voucher"),
                }
            )
        },
    },
    {
    label: $t("Folio Summary Report"),
    icon: 'pi pi-print',
    command: () => {
        getDocList("Reservation Folio", {
            filters: [["reservation", "=", props.reservation]],
            limit:100,
            fields:["name","reservation_stay"]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:docs[0].reservation_stay,
                        folio: docs[0],
                        folios: docs,
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
},
    {
    label: $t("Folio Detail Report"),
    icon: 'pi pi-print',
    command: () => {
        getDocList("Reservation Folio", {
            filters: [["reservation", "=", props.reservation]],
            limit:100,
            fields:["name","reservation_stay"]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Detail Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay:docs[0].reservation_stay,
                        folio: docs[0],
                        folios: docs,
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
        })

    }
},
    {
        label: $t("Folio Summary by Reservation"),
        icon: 'pi pi-print',
        command: () => {
            openReport("Folio Summary by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: ("eDoor Folio Transaction Summary by Reservation"),
                    show_letter_head: true,
                    filter_options: ["invoice_style", "show_room_number", "show_summary", "show_account_code"],
                })
        },
    },
    {
        label: $t("Folio Detail by Reservation"),
        icon: 'pi pi-print',
        command: () => {

            openReport("Folio Detail by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: "eDoor Folio Transaction Detail by Reservation",
                    show_letter_head: true,
                    filter_options: ["invoice_style", "show_room_number", "show_summary", "show_account_code"],
                })
        },
    },
    {
        label: $t("Folio List by Reservation"),
        icon: 'pi pi-print',
        command: () => {

            openReport("Folio List by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: "eDoor Folio List by Reservation",
                    show_letter_head: true
                })
        },
    },
    {

        label: $t("Reservation Detail"),
        icon: 'pi pi-check-circle',
        command: () => {

            openReport("Reservation Detail", {
                "doctype": "Reservation",
                name: props.reservation ?? "",
                report_name: ("Reservation Detail"),
            },)
        },
    },
])

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