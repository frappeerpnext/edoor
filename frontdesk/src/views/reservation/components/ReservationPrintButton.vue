<template>
    <SplitButton label="Print" icon="pi pi-print" :model="items" />
</template>
<script setup>
import ComIFrameModal from "@/components/ComIFrameModal.vue";


import { ref, inject, useDialog, onMounted } from "@/plugin";

const dialog = useDialog();
const props = defineProps({
    reservation: String,
})
const gv = inject("$gv")
const frappe = inject("$frappe")
const db = frappe.db();
const items = ref([
{
        label: "Confirmation Voucher",
        icon: 'pi pi-check-circle',

        command: () => {

            openReport("Confirmmation Voucher",
                {
                    "doctype": "Reservation",
                    name: props.reservation ?? "",
                    report_name: gv.getCustomPrintFormat("eDoor Reservation Confirmation Voucher"),
                }
            )
        },
    },
    {
        label: "Folio Summary by Reservation",
        icon: 'pi pi-print',
        command: () => {

            openReport("Folio Summary by Reservation",
                {
                    doctype: "Reservation",
                    name: props.reservation,
                    report_name: gv.getCustomPrintFormat("eDoor Folio Transaction Summary by Reservation"),
                    show_letter_head: true,
                    filter_options: ["invoice_style", "show_room_number", "show_summary", "show_account_code"],
                })
        },
    },
    {

        label: "Reservation Detail",
        icon: 'pi pi-check-circle',
        command: () => {

            openReport("Reservation Detail", {
                "doctype": "Reservation",
                name: props.reservation ?? "",
                report_name: gv.getCustomPrintFormat("Reservation Detail"),
            },)
        },
    },
    

])

function openReport(title, data) {
    dialog.open(ComIFrameModal, {
        data: data,
        props: {
            header: title,
            style: {
                width: '80vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
        },
    });
}


onMounted(() => {
    db.getDocList('Custom Print Format', {
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
                            },
                        });
                    }
                })
            });
        })


})



</script>