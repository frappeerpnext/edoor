<template>
    <h1>Reservation Stay Detail</h1>
    <TabView>
        <TabPanel header="General Information">
            <ComFieldset nameLegend='Stay Information'>
            <div class="grid grid-rows-4 grid-flow-col gap-4">
                <div>Name:{{ doc.reservation_stay?.name }}</div> 
                <div>Owner:{{ doc.reservation_stay?.owner }} </div>
                <div>creation:{{ doc.reservation_stay?.creation }} </div>
                <div>Modified:{{ doc.reservation_stay?.modified }}</div>
                <div>Modified:{{ doc.reservation_stay?.modified_by }}</div>
                <div>idx:{{ doc.reservation_stay?.idx }}</div>

            </div>    
                Naming Series:{{ doc.reservation_stay?.naming_series }} <br/>
                Reservation Type:{{ doc.reservation_stay?.reservation_type }} <br/>
                Property:{{ doc.reservation_stay?.property }} <br/>
                Reservation:{{ doc.reservation_stay?.reservation }} <br/>
                Arrival Date:{{ doc.reservation_stay?.arrival_date }} <br/>
                Arrival Time:{{ doc.reservation_stay?.arrival_time }} <br/>
                Departure Date:{{ doc.reservation_stay?.departure_date }} <br/>
                Departure Time:{{ doc.reservation_stay?.departure_time }} <br/>
                Room Types:{{ doc.reservation_stay?.room_types }} <br/>
                Rooms:{{ doc.reservation_stay?.rooms }} <br/>
                Guest:{{ doc.reservation_stay?.guest }} <br/>
                Guest_name:{{ doc.reservation_stay?.guest_name }} <br/>
                Adult:{{ doc.reservation_stay?.adult }} <br/>
                Child:{{ doc.reservation_stay?.child }} <br/>
                pax:{{ doc.reservation_stay?.pax }} <br/>
                Reservation Status:{{ doc.reservation_stay?.reservation_status }} <br/>
                <span :style="{background:doc.reservation_stay?.status_color}">{{ doc.reservation_stay?.reservation_status }}</span>
                Status Color:{{ doc.reservation_stay?.status_color }} <br/>
                Is active reservation:{{ doc.reservation_stay?.is_active_reservation }} <br/>
                keyword:{{ doc.reservation_stay?.keyword }} <br/>
                Rate Type:{{ doc.reservation_stay?.rate_type }} <br/>
                Room Types:{{ doc.reservation_stay?.room_types }} <br/>
                Working Day:{{ doc.reservation_stay?.working_day }} <br/>
                Working Date:{{ doc.reservation_stay?.working_date }} <br/>
                Cashier Shift:{{ doc.reservation_stay?.cashier_shift }} <br/>
                Average Daily Rate:{{ doc.reservation_stay?.adr_rate }} <br/>
                Room Nights:{{ doc.reservation_stay?.room_nights }} <br/>
                Total Room Rate:{{ doc.reservation_stay?.total_room_rate }} <br/>
                Room Charge:{{ doc.reservation_stay?.room_charge }} <br/>
                Room Discount:{{ doc.reservation_stay?.room_discount }} <br/>
                Room Discount:{{ doc.reservation_stay?.room_discount }} <br/>
                Total Room Tax:{{ doc.reservation_stay?.room_discount }} <br/>
                Total Room Charge:{{ doc.reservation_stay?.total_room_charge }} <br/>
                Extra Charge:{{ doc.reservation_stay?.extra_charge }} <br/>
                Total Room Charge:{{ doc.reservation_stay?.total_room_charge }} <br/>
                Extra Charge Discount:{{ doc.reservation_stay?.extra_charge_discount }} <br/>
                Extra Charge Tax:{{ doc.reservation_stay?.extra_charge_tax }} <br/>
                Total Extra Charge:{{ doc.reservation_stay?.total_extra_charge }} <br/>
                Total Charge:{{ doc.reservation_stay?.total_charge }} <br/>
                Total Payment:{{ doc.reservation_stay?.total_payment }} <br/>
                Balance:{{ doc.reservation_stay?.balance }} <br/>
                Require Pickup:{{ doc.reservation_stay?.require_pickup }} <br/>
                Required Drop Off:{{ doc.reservation_stay?.required_drop_off }} <br/>
                Doctype:{{ doc.reservation_stay?.doctype }} <br/>
             
            </ComFieldset>
            <ComFieldset nameLegend='Master Guest'>
                Customer Name en:{{ doc.master_guest?.customer_name_en }} <br/>
                Customer Name kh:{{ doc.master_guest?.customer_name_kh }} <br/>
                Customer Code Name:{{ doc.master_guest?.customer_code_name }} <br/>
                Customer Group:{{ doc.master_guest?.customer_group }} <br/>
                Gender:{{ doc.master_guest?.gender }} <br/>
                Disabled:{{ doc.master_guest?.disabled }} <br/>
                Country:{{ doc.master_guest?.country }} <br/>
                Default_discount:{{ doc.master_guest?.default_discount }} <br/>
                Doctype:{{ doc.master_guest?.doctype }} <br/>
            </ComFieldset>
            <ComFieldset nameLegend='Guest'>
<!-- {{ doc.guest }} -->
                Customer Name en:{{ doc.guest?.customer_name_en }} <br/>
                Customer Name kh:{{ doc.guest?.customer_name_kh }} <br/>
                Customer Code Name:{{ doc.guest?.customer_code_name }} <br/>
                Customer Group:{{ doc.guest?.customer_group }} <br/>
                Gender:{{ doc.guest?.gender }} <br/>
                Disabled:{{ doc.guest?.disabled }} <br/>
                Country:{{ doc.guest?.country }} <br/>
                Default_discount:{{ doc.guest?.default_discount }} <br/>
                Doctype:{{ doc.guest?.doctype }} <br/>
            </ComFieldset>
            <ComFieldset nameLegend='Summary'>
            ADR:{{doc.reservation_stay?.adr_rate }} <br/> 
            Room Nights:{{ doc.reservation_stay?.room_nights }}<br/>
            Total Room Rate:{{ doc.reservation_stay?.total_room_rate }}<br/>
            Room Charge:{{ doc.reservation_stay?.room_charge }}<br/>
            Room Discount:{{ doc.reservation_stay?.room_discount }}<br/>
            Room Tax:{{ doc.reservation_stay?.total_room_tax }}<br/>
            Extra Charge:{{ doc.reservation_stay?.extra_charge }}<br/>
            Extra Charge Discount :{{ doc.reservation_stay?.extra_charge_discount }}<br/>
            Extra Charge Tax:{{ doc.reservation_stay?.extra_charge_tax }}<br/>
            Total Extra Charge:{{ doc.reservation_stay?.total_extra_charge }}<br/>
            Total Payment:{{ doc.reservation_stay?.total_payment }}<br/>
            Balance:{{ doc.reservation_stay?.balance }}<br/>
            </ComFieldset>
            <ComFieldset nameLegend='Room list'>
                {{ doc.reservation_stay?.stays }}
                <DataTable :value="doc.reservation_stay?.stays" tableStyle="min-width: 50rem">
                    <Column field="room_number" header="Room Number"></Column>
                    <Column field="start_date" header="Stay">
                    <template #body="slotProps">
                 {{ slotProps.data.start_date }} - {{ slotProps.data.end_date  }}
                </template>
            </Column>
            </DataTable>
            </ComFieldset>
            <ComFieldset nameLegend='Pickup'>
                <!-- {{ doc.reservation_stay }} -->
                Arrival Date : {{ doc.reservation_stay?.arrival_date }}<br/>
                Arrival Time :{{ doc.reservation_stay?.arrival_time }}<br/>
                Departure Date :{{ doc.reservation_stay?.departure_date }}<br/>
                Departure Time :{{ doc.reservation_stay?.departure_time }}<br/>
                Room Types :{{ doc.reservation_stay?.room_types }}<br/>
                Rooms :{{ doc.reservation_stay?.rooms }}<br/>
                Guest :{{ doc.reservation_stay?.guest }}<br/>
                Start Date :{{ doc.reservation_stay?.start_date }}<br/>
                End Date :{{ doc.reservation_stay?.end_date }}<br/>
                Guest :{{ doc.reservation_stay?.guest }}<br/>
                Room Chart:{{ doc.reservation_stay?.show_in_room_chart }}<br/>
                {{ doc.reservation_stay?.arrival_mode ?? " No arriva mode" }}
            </ComFieldset>
            <ComFieldset nameLegend=''>
                {{ doc }}
                {{ doc.reservation_stay?.stays}}
            </ComFieldset>  
        </TabPanel>
        <TabPanel header="Room Rate">
            {{ name }}
            <ComReservationStayRoomRate :reservation_stay="name"/>
        </TabPanel>
        
        <TabPanel header="Folio">

        </TabPanel>
        
        <TabPanel header="Document">

        </TabPanel>

        <TabPanel header="Document">
            
            {{ doc }}
        </TabPanel>

    </TabView>

 
    <hr>
    <Button @click="onCheckIn">Check In</Button>
    <Button @click="OnViewReservation">View Reservation</Button>
    <ReservationPrintButton/>
</template>
<script setup>
import { inject, ref, onMounted, computed, useToast } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ReservationPrintButton from "@/views/reservation/components/ReservationPrintButton.vue"
import ComReservationStayRoomRate from '@/views/reservation/components/ComReservationStayRoomRate.vue';
const frappe = inject("$frappe")
const call = frappe.call();

const confirm = useConfirm()
const toast = useToast()
const socket = inject("$socket")

const dialogRef = inject("dialogRef");
const setting = localStorage.getItem("edoor_setting")
const property = JSON.parse(localStorage.getItem("edoor_property"))

const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;

const name = ref("")
const doc = ref({})



onMounted(() => {
 
    if (!dialogRef) {
        alert("no dialog")
    } else {

        name.value = dialogRef.value.data.name;
        getReservationDetail();

    }
});

const getReservationDetail = () => {
    call.get("edoor.api.reservation.get_reservation_stay_detail", {
        name: name.value
    }).then((result) => {
        doc.value = result.message
    })
}

//check in
const onCheckIn = () => {
    confirm.require({
        message: 'Are you sure you want to Check In this reservation?',
        header: 'Check In',
        icon: 'pi pi-info-circle',
        acceptClass: 'p-button-success',
        accept: () => {
            call.post("edoor.api.reservation.check_in", {
                reservation: doc.value.reservation.name
            }).then((result) => {

                socket.emit("RefresheDoorDashboard", property.name);
                doc.value = result.message

                toast.add({ severity: 'info', summary: 'Check In', detail: 'Check in successfully', life: 3000 });

            }).catch((error) => {
                const errors = error.exception.split(":")
                toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 5000 })
            })

        }
    });
}

const OnViewReservation=()=>{

    dialogRef.value.close({action:"view_reservation_detail",reservation:doc.value.reservation.name});
}


</script>