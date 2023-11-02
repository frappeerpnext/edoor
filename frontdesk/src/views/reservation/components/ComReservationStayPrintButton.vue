<template>
    <SplitButton class="border-split-none" label="Print" icon="pi pi-print" :model="items" />
</template>
<script setup>
import { useToast } from "primevue/usetoast";
import { ref, inject, useDialog, onMounted } from "@/plugin";
import ComPrintGuestRegistrationCard from "./ComPrintGuestRegistrationCard.vue";
import ComPrintReservationStay from "@/views/reservation/components/ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
const dialog = useDialog();
const gv = inject("$gv")
const toast = useToast();
const props = defineProps({
    reservation: String,
    reservation_stay: String,
    folio_number:String
})
const frappe = inject("$frappe")
const db = frappe.db();
const items = ref([])

//static print button
items.value.push({
    label: "Guest Registration Card",
    icon: 'pi pi-user-edit',
    command: () => {
        const dialogRef = dialog.open(ComPrintGuestRegistrationCard, {
            data: {
                reservation: props.reservation ?? "",
                reservation_stay: props.reservation_stay ?? "",
               
            },
            props: {
                header: "Guest Registration Card",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
            },
        });
    }
})

//Confirmattion Voucher
items.value.push({
    label: "Confirmation Voucher",
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
                // report_name:  "eDoor%20Reservation%20Stay%20Confirmation%20Voucher",
                report_name:  gv.getCustomPrintFormat("eDoor Reservation Stay Confirmation Voucher "),
            },
            props: {
                header: "Confirmation Voucher",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
            },
        });
    }
})

//Folio Summary Report
items.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {
        db.getDocList("Reservation Folio", {
            filters: [["reservation_stay", "=", props.reservation_stay]]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay: props.reservation_stay,
                        folio_number:props.folio_number,
                       // report_name: "eDoor%20Reservation%20Stay%20Folio%20Summary%20Report",
                         report_name:  gv.getCustomPrintFormat("eDoor Reservation Stay Folio Summary Report"),

                        view: "print"
                    },
                    props: {
                        header: "Folio Summary Report",
                        style: {
                            width: '80vw',
                        },
                        position:"top",
                        modal: true,
                        maximizable: true,
                        closeOnEscape: false
                    },
                });
            }
        })

    }
})

//folio detail report
items.value.push({
    label: "Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        db.getDocList("Reservation Folio", {
            filters: [ ["reservation_stay", "=", props.reservation_stay]]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        reservation_stay: props.reservation_stay,
                        folio_number:props.folio_number,
                        report_name: gv.getCustomPrintFormat("eDoor Reservation Stay Folio Detail Report"), //"eDoor%20Reservation%20Stay%20Folio%20Detail%20Report",
                    
                        view: "print"
                    },
                    props: {
                        header: "Folio Detail Report",
                        style: {
                            width: '80vw',
                        },
                        position:"top",
                        modal: true,
                        maximizable: true,
                    },
                });
            }
        })


    }
})

//reservation stay detail
items.value.push({
    label: "Reservation Stay Detail",
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
                // report_name:  "eDoor%20Reservation%20Stay%20Confirmation%20Voucher",
                report_name:  gv.getCustomPrintFormat("Reservation Stay Detail"),
            },
            props: {
                header: "Reservation Stay Detail",
                style: {
                    width: '80vw',
                },
                position:"top",
                modal: true,
                maximizable: true,
            },
        });
    }
})


onMounted(() => {

    if (props.reservation_stay) {

        db.getDocList('Print Format', {
            fields: [
                'name',
                'title'
            ],
            filters: [["show_in_reservation_stay_detail", "=", "1"]]

        })
            .then((doc) => {

                doc.forEach(d => {
                    items.value.push({
                        label: d.title,
                        name: d.name,
                        icon: 'pi pi-refresh',
                        command: (r) => {
           
                            dialog.open(ComPrintReservationStay, {
                                data: {
                                    doctype: "Reservation%20Stay",
                                    name: props.reservation_stay,
                                    report_name: r.item.name,
                                    view: "print"
                                },
                                props: {
                                    header: r.item.label,
                                    style: {
                                        width: '80vw',
                                    },
                                    position:"top",
                                    modal: true,
                                    maximizable: true,
                                },
                            });
                        }
                    })
                });
            })
            .catch((error) => {

            });


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