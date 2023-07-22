<template>
    <main-layout v-if="hasProperty" />
    <Property v-else />
    <DynamicDialog />
    <Toast />
    <ConfirmDialog></ConfirmDialog>
</template>


<script setup>
import { ref, computed, onUnmounted, onMounted, useToast, inject, getApi } from "@/plugin"
import MainLayout from './components/layout/MainLayout.vue';
import Property from '@/views/user_property/Property.vue';
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import OpenShift from "@/views/shift/OpenShift.vue"
import ComReservationStayAssignRoom from "./views/reservation/components/ComReservationStayAssignRoom.vue";
import { useDialog } from 'primevue/usedialog';
import ComEditReservationRoomRate from '@/views/reservation/components/ComEditReservationRoomRate.vue';
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComFolioDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioDetail.vue';

import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ComCashierShiftDetail from "./views/shift/ComCashierShiftDetail.vue";
import ComCloseShift from "./views/shift/ComCloseShift.vue";
const socket = inject("$socket");
const gv = inject("$gv")

socket.on("UpdateCashierShift", (arg) => {

    if (JSON.parse(localStorage.getItem("edoor_property")).name == arg.business_branch) {
        gv.cashier_shift = arg
 
    }
})



const toast = useToast();
const dialog = useDialog();

const hasProperty = ref(false)

if (localStorage.getItem("edoor_property") == null) {

    const user = JSON.parse(localStorage.getItem("edoor_user"))

    if (user?.property?.length == 1) {
        localStorage.setItem("edoor_property", JSON.stringify(user.property[0]))
        hasProperty.value = true
    }



} else {
    hasProperty.value = true
}



const actionClickHandler = async function (e) {
    if (e.isTrusted && typeof (e.data) == 'string') {

        const data = e.data.split("|")

        if (data.length > 0) {

            if (data[0] == "view_guest_detail") {

                showGuestDetail(data[1])
            } else if (data[0] == "view_reservation_stay_detail") {
                showReservationStayDetail(data[1])

            } else if (data[0] == "view_reservation_detail") {
                showReservationDetail(data[1])

            } else if (data[0] == "view_edit_room_rate") {
                onEditRoomRate(data[1])

            } else if (data[0] == "view_folio_transaction_detail") {
                showFolioTransactionDetail(data[1])
            
            } else if (data[0] == "view_folio_detail") {
                showFolioDetail(data[1])
            } else if (data[0] == "view_cashier_shift_detail") {
                showCashierShiftDetail(data[1])
            } else if (data[0] == "close_shift") {
                openCloseShift()
            }
            else if (data[0] == "assign_room") {
                onAssignRoom(data[1], data[2])
            }
            else if (data[0] == "show_alert") {
                toast.add({ severity: 'warn', summary: data[1], detail: '', life: 3000 })
            }
            else if (data[0] == "show_error") {
                toast.add({ severity: 'warn', summary: data[1], detail: '', life: 3000 })
            }
            else if (data[0] == "show_success") {
                toast.add({ severity: 'success', summary: data[1], detail: '', life: 3000 })
            }
        }

    }
};


window.addEventListener('message', actionClickHandler, false);



onUnmounted(() => {
    window.removeEventListener('message', actionClickHandler, false);

})
onMounted(() => {
    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
    if (!working_day.cashier_shift?.name) {
        const dialogRef = dialog.open(OpenShift, {
            props: {
                header: 'Open Shift',
                style: {
                    width: '50vw',
                },
                position: top,
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: 'top'
            },

        });

    } else {
        gv.cashier_shift = working_day.cashier_shift
    }
})


function showGuestDetail(name) {

    const dialogRef = dialog.open(GuestDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Guest Detail',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: "top"
        },

    });
}

function showReservationDetail(name) {

    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Detail',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: "top"
        }
    });
}
function onEditRoomRate(name) {

    getApi("reservation.get_room_rate_by_name_to_edit", {
        name: name
    }).then((result) => {
        const showCheckUpdateFutureStayRoomRate = result.message.future_room_rate.length > 0
        let future_room_rates = result.message.future_room_rate
        future_room_rates.push({ name: name, reservation_stay: result.message.reservation_stay.name })


        const dialogRef = dialog.open(ComEditReservationRoomRate, {
            data: {
                selected_room_rate: result.message.room_rate,
                reservation_stay: result.message.reservation_stay,
                show_check_update_future_stay_room_rate: showCheckUpdateFutureStayRoomRate,
                future_room_rates: future_room_rates

            },
            props: {
                header: 'Edit Room Rate',
                style: {
                    width: '80vw',
                },
                maximizable: true,
                modal: true,
                position: "top"
            }
        });
    })

}


function onAssignRoom(reservation_stay_name, name) {
    

    dialog.open(ComReservationStayAssignRoom, {
        data: {
            stay_room: name,
            reservation_stay_name: reservation_stay_name
        },
        props: {
            header: `Assign Room`,
            style: {
                width: '70vw',
            },

            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false
        },
        onClose: (options) => {
            if (options.data && options.data.message) {
                rs.getReservationDetail(options.data.message.name)
            }
        }
    })
}

function showReservationStayDetail(name) {

    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Stay Detail',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: "top"
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                if (data.action == "view_reservation_detail") {
                    showReservationDetail(data.reservation)
                }

            }
        }
    });
}


function showFolioTransactionDetail(name) {

    const dialogRef = dialog.open(ComFolioTransactionDetail, {
        data: {
            folio_transaction_number: name
        },
        props: {
            header: 'Folio Transaction Detail - ' + name,
            style: {
                width: '50vw',
            },
            modal: true,
            position:"top",
            closeOnEscape: false
        },
    });
}

function showFolioDetail(name) {
    const dialogRef = dialog.open(ComFolioDetail, {
        data: {
            name: name,
        },
        props: {
            header:"Folio Detail - " + name,
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: true
        }
       
    });
}

function showCashierShiftDetail(name) {
    const dialogRef = dialog.open(ComCashierShiftDetail, {
        data: {
            name: name,
        },
        props: {
            header:"Shift Detail- " + name,
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: true
        }
       
    });
}

function openCloseShift() {
    const dialogRef = dialog.open(ComCloseShift, {
        props: {
            header:"Close Shift",
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
       
    });
}



</script>
<style>
.p-menu {
    width: auto;
}
</style>
