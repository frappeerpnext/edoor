<template>
    <SplitButton class="border-split-none" label="Print" icon="pi pi-print" :model="items" />
</template>
<script setup>
import { useToast } from "primevue/usetoast";
import { ref, inject, useDialog, onMounted } from "@/plugin";
import ComPrintGuestRegistrationCard from "./ComPrintGuestRegistrationCard.vue";
import ComPrintReservationStay from "./ComPrintReservationStay.vue";
import ComIFrameModal from "@/components/ComIFrameModal.vue";
const dialog = useDialog();

const toast = useToast();
const props = defineProps({
    reservation: String,
    reservation_stay: String
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
                reservation_stay: props.reservation_stay ?? ""
            },
            props: {
                header: "Guest Registration Card",
                style: {
                    width: '80vw',
                },
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
    command: () => {
        dialog.open(ComIFrameModal, {
            data: {
                "doctype": "Reservation%20Stay",
                name: props.reservation_stay,
                report_name: "eDoor%20Reservation%20Stay%20Confirmation%20Voucher",
                view: "print"
            },
            props: {
                header: "Confirmation Voucher",
                style: {
                    width: '80vw',
                },

                modal: true,
                maximizable: true,
            },
        });
    }
})

//Confirmattion Voucher
items.value.push({
    label: "Folio Summary Report",
    icon: 'pi pi-print',
    command: () => {
        db.getDocList("Reservation Folio", {
            filters: [["status", "=", "active"], ["reservation_stay", "=", props.reservation_stay]]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        name: props.reservation_stay,
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
                    },
                });
            }
        })

    }
})

//Confirmattion Voucher
items.value.push({
    label: "Folio Detail Report",
    icon: 'pi pi-print',
    command: () => {
        db.getDocList("Reservation Folio", {
            filters: [["status", "=", "active"], ["reservation_stay", "=", props.reservation_stay]]
        }).then((docs) => {

            if (docs.length == 0) {
                toast.add({ severity: 'warn', summary: 'Folio Summary Report', detail: 'There is no folio available in this reservation stay', life: 3000 });
            } else {
                dialog.open(ComPrintReservationStay, {
                    data: {
                        doctype: "Reservation%20Stay",
                        name: props.reservation_stay,
                        report_name: "eDoor%20Reservation%20Stay%20Folio%20Detail%20Report",
                        view: "print"
                    },
                    props: {
                        header: "Folio Detail Report",
                        style: {
                            width: '80vw',
                        },

                        modal: true,
                        maximizable: true,
                    },
                });
            }
        })


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

                console.log(doc)
                doc.forEach(d => {
                    items.value.push({
                        label: d.title,
                        name: d.name,
                        icon: 'pi pi-refresh',
                        command: (r) => {
                            console.log(r.item)
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