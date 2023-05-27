<template>
    <h1>Reservation Stay Detail</h1>
    <TabView>
        <TabPanel header="General Information">
            <div class="grid mt-5 ml-0 ms-0">
                <div class="col">
                    <ComReservationStayDetailGuestInfo v-model="doc"/>
                </div> 
                <div class="col-5">
                    <ComReservationStayPanel title="Stay Information" >
                        <template #content>
                        <div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Res. Date" :value="doc.reservation_stay?.name"  valueClass="grow"  ></ComBoxStayInformation>
                                <ComBoxStayInformation title="Int. No" :value="doc.reservation_stay?.reservation"  valueClass="grow" titleClass="w-4rem" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Book. No" :value="doc.reservation_stay?.naming_series"  valueClass="grow" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Res. No" :value="doc.reservation_stay?.naming_series"  valueClass="grow" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <!-- <ComBoxStayInformation title="Rooms" :value="doc.reservation_stay?.rooms"  valueClass="grow" >
                                    
                                </ComBoxStayInformation> -->
                                <div v-if="doc.reservation_stay?.rooms.split(',').length>3">
                                    {{ doc.reservation_stay?.rooms.split(",").slice(0,3).join(",") }} view {{ doc.reservation_stay?.rooms.split(",").length  }} more
                                </div>
                                
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Arraval" :value="moment(doc.reservation_stay?.arrival_date).format('DD-MM-yyyy')" valueClass="col-4" ></ComBoxStayInformation>
                                <ComBoxStayInformation :value="doc.reservation_stay?.arrival_time" valueClass="col" ></ComBoxStayInformation>
                                <ComBoxStayInformation :value="moment(doc.reservation_stay?.arrival_date).format('ddd')" valueClass="col" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Departure" :value="doc.reservation_stay?.departure_date" valueClass="col-4" ></ComBoxStayInformation>
                                <ComBoxStayInformation :value="doc.reservation_stay?.departure_time" valueClass="col" ></ComBoxStayInformation>
                                <ComBoxStayInformation :value="doc.reservation_stay?.arrival_time" valueClass="col" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Nights" :value="doc.reservation_stay?.room_nights"  valueClass="col-2" ></ComBoxStayInformation>
                            </div>
                            <div class="flex mt-2">
                                <ComBoxStayInformation title="Adults" :value="doc.reservation_stay?.room_nights"  valueClass="col-2" ></ComBoxStayInformation>
                                <ComBoxStayInformation title="Children" :value="doc.reservation_stay?.room_nights"  valueClass="col-2" titleClass="w-5rem" ></ComBoxStayInformation>
                            </div>
                        </div>
                        </template>
                    </ComReservationStayPanel>
                </div>
                <div class="col">
                    <ComReservationStayDetailChargeSummary :data="doc.reservation_stay"></ComReservationStayDetailChargeSummary>
                </div>
            </div>
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
                <div class="flex">
                     <div class="">
                        <!-- <Avatar image="/images/avatar/amyelsner.png" class="mr-2" size="xlarge" shape="circle" /> -->
                        <div class="flex" >
                        <Avatar icon="pi pi-user" class="mr-2" size="xlarge" shape="circle" />
                        <div><spna> {{ doc.master_guest?.customer_name_en }} | {{ doc.master_guest?.customer_name_kh }} <Tag value="Primary" rounded></Tag>   </spna>
                        <div> {{ doc.master_guest?.phoneNumber1 }}</div>
                        <div>{{ doc.master_guest?.email_address }}</div>
                        </div>
                        </div>
                     </div> 
                </div>
                {{ doc.master_guest }}
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
import { inject, ref, onMounted, computed, useToast,useRoute,useRouter } from '@/plugin'
import { useConfirm } from "primevue/useconfirm";
import ReservationPrintButton from "@/views/reservation/components/ReservationPrintButton.vue"
import ComReservationStayRoomRate from '@/views/reservation/components/ComReservationStayRoomRate.vue';
import ComCardProfileGuest from '@/views/reservation/components/ComCardProfileGuest.vue';
import ComReservationStayDetailGuestInfo from './components/ComReservationStayDetailGuestInfo.vue';
import ComReservationStayPanel from './components/ComReservationStayPanel.vue';
import ComReservationStayDetailChargeSummary from './components/ComReservationStayDetailChargeSummary.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
const route = useRoute()
const router = useRouter()

const frappe = inject("$frappe")
const call = frappe.call();
const moment = inject("$moment")
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
        if(route.params.name){ 
            name.value = route.params.name
            getReservationDetail();
        }else{
            alert("Go back to reserveatin list")
        }

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