<template>
    
    <template v-if="hasProperty">
        <main-layout v-if="$route.meta.layout!='blank_layout' && ui=='main_layout'" />
        <BlankLayout v-else />
    </template>
    <Property v-else />

    <DynamicDialog v-if="isMobile"  :pt="{
        root: { class: 'p-dialog-maximized' }
    }"/>
    <DynamicDialog v-else/>
    
    <Toast position="top-center">
        <template #message="slotProps">
            <div class="flex flex-column" style="flex: 1">
                <strong class="mb-1" v-if="slotProps.message.summary" v-html="slotProps.message.summary"></strong>
                <p v-if="slotProps.message.detail" v-html="slotProps.message.detail"></p>
            </div>
        </template>
    </Toast>
    <ConfirmDialog></ConfirmDialog>
    
</template>


<script setup>
import { ref, computed, onUnmounted, onMounted, useToast, inject, getApi,useRoute, useRouter } from "@/plugin"
import MainLayout from './components/layout/MainLayout.vue';
import BlankLayout from './components/layout/BlankLayout.vue';
import Property from '@/views/user_property/Property.vue';
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import OpenShift from "@/views/cashier_shift/OpenShift.vue"
import ComReservationStayAssignRoom from "./views/reservation/components/ComReservationStayAssignRoom.vue";
import { useDialog } from 'primevue/usedialog';
import ComEditReservationRoomRate from '@/views/reservation/components/ComEditReservationRoomRate.vue';
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import ComFolioDetail from '@/views/reservation/components/folios/ComFolioDetail.vue';

import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ComCashierShiftDetail from "./views/cashier_shift/ComCashierShiftDetail.vue";
import ComCloseShift from "./views/cashier_shift/ComCloseShift.vue";
import ComRoomBlockDetail from "./views/room_block/ComRoomBlockDetail.vue";
import ComCityLedgerDetail from "@/views/city_ledger/components/ComCityLedgerDetail.vue";
import ComBusinessSourceDetail from '@/views/business_source/components/ComBusinessSourceDetail.vue';
import ComRoomDetail from '@/views/housekeeping/components/ComRoomDetail.vue';
import ComDeskFolioDetail from "@/views/desk_folio/components/ComDeskFolioDetail.vue";
import ComDepositLedgerDetail from "@/views/deposit_ledger/components/ComDepositLedgerDetail.vue";
import ComPayableLedgerDetail from "@/views/payable_ledger/components/ComPayableLedgerDetail.vue";
import ComVendorDetail from "@/views/vendor/ComVendorDetail.vue";
import ComDailyPropertySummary from "@/views/property_summary/ComDailyPropertySummary.vue";
const urlParams = new URLSearchParams(window.location.search);
const ui = ref(urlParams.get('layout') || "main_layout")

window.isMobile = ('ontouchstart' in window || navigator.maxTouchPoints > 0);
const isMobile = ref(window.isMobile)
const gv = inject("$gv")
const moment= inject("$moment")
window.session_id = gv.generateGuid()
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

            if (data[0] == "view_guest_detail" || data[0] == "view_customer_detail"  ) {

                showGuestDetail(data[1])
            } else if (data[0] == "view_reservation_stay_detail") {
                
                showReservationStayDetail(data[1])

            } else if (data[0] == "view_reservation_detail") {
                showReservationDetail(data[1])

            } else if (data[0] == "view_edit_room_rate" || data[0] == "view_reservation_room_rate_detail") {
                onEditRoomRate(data[1])

            } else if (data[0] == "view_folio_transaction_detail") {
                showFolioTransactionDetail(data[1])
            
            } else if (data[0] == "view_folio_detail" || data[0] == "view_reservation_folio_detail") {
                showFolioDetail(data[1])
            } else if (data[0] == "view_cashier_shift_detail") {
                showCashierShiftDetail(data[1])
            } else if (data[0] == "view_cashier_shift_detail_from_run_night_audit") {
                showCashierShiftDetail(data[1], 1)
            } else if (data[0] == "close_shift") {
                openCloseShift()
          
            } else if (data[0] == "view_city_ledger_detail") {
                showCityLedgerDetail(data[1])
            
            } else if (data[0] == "view_deposit_ledger_detail") {
                showDepositLedgerDetail(data[1])
            }
            else if (data[0] == "view_business_source_detail") {
                showBusinessSourceDetail(data[1])
            }
            else if (data[0] == "assign_room") {
                onAssignRoom(data[1], data[2])
            }
            else if (data[0] == "view_room_block_detail") {
                showRoomBlockDetail(data[1])
            }
            else if (data[0] == "show_alert") {
                toast.add({ severity: 'warn', summary: data[1], detail: '', life: 3000 })
            }
            else if (data[0] == "show_error") {
                toast.add({ severity: 'error', summary: data[1], detail: '', life: 3000 })
            }
            else if (data[0] == "show_success") {
                toast.add({ severity: 'success', summary: data[1], detail: '', life: 3000 })
            }
            else if (data[0] == "view_sale_detail") {
                showSaleDetail(data[1])
            }
            else if (data[0] == "view_desk_folio_detail") {
                showDeskFolioDetail(data[1])
            }
            else if (data[0] == "view_payable_ledger_detail") {
                showPayableLedgerDetail(data[1])
            }
            else if (data[0] == "view_room_detail") {
                showRoomDetail(data[1])
            }
            else if (data[0] == "view_vendor_detail") {
                showVendorDetail(data[1])
            }
            else if (data[0] == "get_workingday") {
                getWorkingDay();
            }
        }

    }else if (e.data.extendedProps)  {
 
        if(e.data.extendedProps.type=="room_block"){
            showRoomBlockDetail(e.data.publicId)
        }
        else if(e.data.extendedProps.type=="room_type_event" || e.data.extendedProps.type=="room_inventory_room_type_summary" ){
            
            onViewDailySummary(e.data.date,e.data.resourceIds[0], e.data.extendedProps.room_type)
        }
        else if(e.data.extendedProps.type=="property_summary"   ){
            onViewDailySummary(e.data.date,null)
        }
        
        
    }else if(e.data.action){
        if(e.data.action=="view_property_data_sumary_by_date"){ 
            onViewDailySummary(e.data.date,e.data.room_type_id, e.data.room_type)
        }
    }
};

function getWorkingDay(){
    getApi("frontdesk.get_working_day",{property:window.property_name}).then(r=>{
        gv.cashier_shift = r.message.cashier_shift
        window.working_day = r.message
        localStorage.setItem("edoor_working_day",JSON.stringify(window.working_day))
        window.socket.emit("UpdateCashierShift", r.message.cashier_shift);
    });
}

onUnmounted(() => {
    window.removeEventListener('message', actionClickHandler, false);
    window.socket.off("UpdateCashierShift")
    window.socket.off("RunNightAudit")
})
onMounted(() => { 
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', actionClickHandler, false);
    window.socket.on("UpdateCashierShift", (arg) => {
        if (window.property_name == arg.business_branch) {
            if(window.session_id==arg.session_id){
                if (arg.is_closed ==1){
                    gv.cashier_shift = null
                }else {
                    gv.cashier_shift = arg
                }
            }else {
                if(arg.is_closed==1){
                    toast.add({ severity: 'warn', summary: "Close cashier shift", detail: 'This cashier shift is closed. Your browser will be reload.', life: 5000 })
                    setTimeout(function(){
                        location.reload();
                    }, 5000)
                }
                
            }
            
            
        }
    })


    window.socket.on("RunNightAudit", (arg) => {
        if (JSON.parse(localStorage.getItem("edoor_property")).name == arg.property && window.session_id!=arg.session_id) {
            window.location.reload()
        }
    })


    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
    if (!working_day?.cashier_shift?.name) {
        dialog.open(OpenShift, {
            props: {
                header: 'Open Shift',
                style: {
                    width: '50vw',
                },
                position: top,
                modal: true,
                maximizable: true,
                closeOnEscape: false,
                position: 'top',
                breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
            },

        });

    } else {
        gv.cashier_shift = working_day.cashier_shift
    }
})

function showBusinessSourceDetail(name){
    const dialogRef = dialog.open(ComBusinessSourceDetail, {
        data: {
            name: name,
        },
        props: {
            header: 'Business Source - ' + name,
            style: {
                width: '80vw',
            },
            modal: true,
            position:"top",
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
    });
}

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
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
    });
}
function showVendorDetail(name) {

const dialogRef = dialog.open(ComVendorDetail, {
    data: {
        name: name
    },
    props: {
        header: 'Vendor Detail',
        style: {
            width: '60vw',
        },
        maximizable: true,
        modal: true,
        closeOnEscape: false,
        position: "top",
        breakpoints:{
                '960px': '60vw',
                '640px': '100vw'
            },
    },

});
}
function showRoomDetail(name) {

const dialogRef = dialog.open(ComRoomDetail, {
    data: {
        name: name
    },
    props: {
        header: 'Room Detail',
        style: {
            width: '60vw',
        },
        maximizable: true,
        modal: true,
        closeOnEscape: false,
        position: "top",
        breakpoints:{
                '960px': '60vw',
                '640px': '100vw'
            },
    },

});
}


function showReservationDetail(name) {
    
    if (!window.has_reservation_detail_opened){
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
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
    });
    }else {
        window.open('/frontdesk/reservation-detail/' + name, '_blank')
    }
  
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
                position: "top",
                closeOnEscape: false,
                breakpoints:{
                    '960px': '80vw',
                    '640px': '100vw'
                },
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
                width: '80vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        
    })
}

function showReservationStayDetail(name) {
    
    if (!window.reservation_stay){
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Reservation Stay Detail',
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
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
else{
    window.open('/frontdesk/stay-detail/' + name, '_blank')
}
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
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
    });
}

function showCityLedgerDetail(name) {

    const dialogRef = dialog.open(ComCityLedgerDetail, {
        data: {
            name: name
        },
        props: {
            header: 'City Ledger - ' + name,
            style: {
                width: '80vw',
            },
            modal: true,
            position:"top",
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
    });
}

function showDepositLedgerDetail(name) {

    const dialogRef = dialog.open(ComDepositLedgerDetail, {
        data: {
            name: name
        },
        props: {
            header: 'Deposit Ledger - ' + name,
            style: {
                width: '80vw',
            },
            modal: true,
            position:"top",
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
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
            closeOnEscape: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
       
    });
}

function showCashierShiftDetail(name,is_run_night_audit=0) {
    const dialogRef = dialog.open(ComCashierShiftDetail, {
        data: {
            name: name,
            is_run_night_audit: is_run_night_audit
        },
        props: {
            header:"Cashier Shift Detail - " + name,
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: true,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
       
    });
}
function showRoomBlockDetail(name) {
    const dialogRef = dialog.open(ComRoomBlockDetail, {
        data: {
            name: name,
        },
        props: {
            header:"Room Block Detail - " + name,
            style: {
                width: '60vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '60vw',
                '640px': '100vw'
            },
        }
       
    });
}


function onViewDailySummary(date,room_type_id, title="") {
 
 
    const dialogRef = dialog.open(ComDailyPropertySummary, {

       data: {
           property: JSON.parse(localStorage.getItem("edoor_property")).name,
           date:moment(date).format("YYYY-MM-DD"),
           room_type_id: (room_type_id || '')
       },
       props: {
           header:"Summary Data on " + moment(date).format("DD-MM-YYYY") +( title==""?"":" - " + title),
           style: {
               width: '90vw',
           },
           position:"top",
           modal: true,
           maximizable: true,
           closeOnEscape: false,
           breakpoints:{
                '960px': '90vw',
                '640px': '100vw'
            },
        
       }
      
   });
}


function openCloseShift() {
    dialog.open(ComCloseShift, {
        data:{
            name: window.working_day.cashier_shift.name
        },
        props: {
            header:"Close Shift",
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
        }
       
    });
}

function showSaleDetail(name) {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
           "doctype": 'Sale',
           name: name,
           report_name: 'Sale%20Receipt'
        },
        props: {
            header:"Sale Detail" +' '+ name,
            style: {
                width: '90vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '90vw',
                '640px': '100vw'
            },
        }
   });
}

function showDeskFolioDetail(name) {
    const dialogRef = dialog.open(ComDeskFolioDetail, {
        data: {
            name: name,
        },
        props: {
            header:"Desk Folio Detail - " + name,
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
        }
       
    });
}
function showPayableLedgerDetail(name) {
    const dialogRef = dialog.open(ComPayableLedgerDetail, {
        data: {
            name: name,
        },
        props: {
            header:"Payable Ledger Detail - " + name,
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
        }
       
    });
}

</script>
<style>
.p-menu {
    width: auto;
}
</style>
