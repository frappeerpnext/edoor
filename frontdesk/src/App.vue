<template>
    <main-layout v-if="hasProperty" />
    <Property v-else />
    <DynamicDialog />
    <Toast />
    <ConfirmDialog></ConfirmDialog>


</template>


<script setup>
import { ref, computed, onUnmounted,onMounted,useToast,inject} from "@/plugin"
import MainLayout from './components/layout/MainLayout.vue';
import Property from '@/views/user_property/Property.vue';
import GuestDetail from "@/views/guest/GuestDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import OpenShift from "@/views/shift/OpenShift.vue"

import { useDialog } from 'primevue/usedialog';
const socket = inject("$socket");
const gv = inject("$gv") 

socket.on("UpdateCashierShift", (arg) => {
     
    if(JSON.parse(localStorage.getItem("edoor_property")).name == arg.business_branch ){
        gv.cashier_shift = arg
        alert("New cashier shift opened.")
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


// window.addEventListener("unhandledrejection", function (error) {
     
//     let exception = error.reason.exception || error.reason.message
//     const replace_text = [
//         {text:"frappe.exceptions.ValidationError:",value:""},
//         {text:"frappe.exceptions.MandatoryError:",value:"Value required for "},
//         {text:"ValueError:",value:"Invalid data input. "},
//         {text:"frappe.exceptions.PermissionError: ",value:""},
//         {text:"_",value:" "},
//     ]
//     let message=exception
//     if(exception){
//         replace_text.forEach(t => {
//             message =message.replaceAll(t.text,t.value) 	
//         });
        
//     }
//     toast.add({ severity: 'warn', summary: '', detail: message, life: 3000 })
// });


 
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
                
            }
            else if(data[0]=="show_alert"){
                toast.add({ severity: 'warn', summary: data[1], detail: '', life: 3000 })
            }
            else if(data[0]=="show_error"){
                toast.add({ severity: 'warn', summary: data[1], detail: '', life: 3000 })
            }
            else if(data[0]=="show_success"){
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
   const working_day =JSON.parse( localStorage.getItem("edoor_working_day"))
   if (!working_day.cashier_shift?.name){
    const dialogRef = dialog.open(OpenShift, {
        props: {
            header: 'Open Shift',
            style: {
                width: '50vw',
            },
            position:top,
            modal: true,
            maximizable: true,
            closeOnEscape: false
        },
       
    });

   }else{
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
                width: '50vw',
            },
            maximizable: true,
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            position:"top"
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
            position:"top"
        }
    });
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
            position:"top"
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                if (data.action=="view_reservation_detail"){
                    showReservationDetail(data.reservation)
                }
                
            }
        }
    });
}



</script>
<style>
.p-menu {
    width: auto;
}
</style>
