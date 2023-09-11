<template lang="">
    <ComHeader isRefresh @onRefresh="onRefresh()">
        <template #start>
            <div class="font-bold">{{ property.name }}</div>
            <div class="txt-st__det" v-if="property.property_code">ID: {{ property.property_code }}, {{ property.province }}</div>
        </template>
        <template #center>
            <Button label="Today" class="w-48 btn-date__t border-noround-right border-none"
                :class="selected_date == data.working_date ? 'active' : ''" @click="onShowTodayData()" />
            <Button label="Tomorrow" class="w-48 btn-date__t border-noround border-x-none border-none"
                :class="selected_date == tomorrow ? 'active' : ''" @click="onShowTommorowData()" />
            <Calendar v-model="date" class="w-48 das-calendar"  panelClass="no-btn-clear" @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar />
        </template>
        <template #end>
            <div class="flex gap-2 justify-content-end">
                <NewFITReservationButton/>
                <NewGITReservationButton/>
                
            </div>
        </template>
    </ComHeader>
    <div class="grid">
        <div class="col-2">
            <ComSystemDateKPI :data="data"></ComSystemDateKPI>
        </div>
        <div class="col">
            <div class="bg-white h-full border-round-lg">
                <ComPanel title="Occupancy">
                    <div class="grid">
                        <div class="col-6 flex align-items-center justify-content-center mt-3">
                            <ComChartDoughnut :total_room="data?.total_room"  show-percentage="Occupied" :showPercentageInteger="true" :is-legend="false" :data="chartOccupancy"
                                v-if="chartOccupancy.length > 0" />
                            <Skeleton v-else shape="circle" size="18rem"></Skeleton>

                        </div>
                        <div class="col-5">
                            <ComChartStatus @onClick="onViewRoomOccupy" :value="data.total_room_occupy" title="Occupied" class="btn-green-edoor" ></ComChartStatus>
                            <ComChartStatus @onClick="onViewVacantRoom" :value="data.total_room_vacant" title="Vacant" class="bg-warning-edoor">
                            </ComChartStatus>
                            <ComChartStatus @onClick="onViewRoomList" :value="data.total_room" title="Total rooms" class="btn-sec-edoor">
                            </ComChartStatus>
                            <div class="grid mt-3 text-center">
                                <ComShowCancelOcc @onClick="onViewCancelReservation" title="Cancelled" :value="data.total_cancelled"></ComShowCancelOcc>
                                <ComShowCancelOcc  @onClick="onViewNoShowReservation" title="No-show" :value="data.total_no_show"></ComShowCancelOcc>
                            </div>
                        </div>
                    </div>
                </ComPanel>
            </div>
        </div>
        <div class="col">
            <div class="bg-white h-full border-round-lg">
                <ComPanel title="Summary">
                    <div class="grid grid-cols-4 pt-3 px-2 pb-0 text-white">
                        <ComKPI @onClick="viewSummary('Arrival')" :value="data.arrival" title="Arrival" class="primary-btn-edoor cursor-pointer border-round-lg"> </ComKPI>
                        <ComKPI @onClick="viewSummary('Check-In Remaining')" :value="data.arrival_remaining" title="Check-in Remaining"
                            class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>
                        <ComKPI  @onClick="viewSummary('Departure')" :value="data.departure" title="Departure" class="primary-btn-edoor border-round-lg cursor-pointer">
                        </ComKPI>
                        <ComKPI @onClick="viewSummary('Check-out remaining')" :value="data.departure_remaining" title="Check-out Remaining"
                            class="primary-btn-edoor border-round-lg cursor-pointer">
                        </ComKPI>
                        <ComKPI @onClick="viewSummary('GIT Arrival')" :value="data.git_reservation_arrival + '/' +  data.git_stay_arrival" title="GIT Arrival" class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>

                        <ComKPI @onClick="viewSummary('Stay Over')" :value="data.stay_over" title="Stay Over" class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>
                        
                        <ComKPI @onClick="viewSummary('Unassign Room')" :value="data.unassign_room" title="Unassign Room" class="bg-og-edoor border-round-lg cursor-pointer"> </ComKPI>
                        <ComKPI @onClick="viewSummary('Pickup and Drop Off')" :value="data.pick_up + '/' + data.drop_off" title="Pickup/Drop off" class="bg-warning-edoor border-round-lg cursor-pointer"> </ComKPI>
                        
                    </div>
                </ComPanel>
            </div>
        </div>
        <div class="col-2">
            <ComPanel title="Room Status" class="h-full">
                <ComHousekeepingStatus />
            </ComPanel>
        </div>
    </div>

    <div class="px-3 py-3 bg-white mt-2 border-round-xl tab-reserv-no">
        <TabView class="tabview-custom" lazy>
            <TabPanel>
                <template #header>
                    <span>Arrival Remaining</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.arrival_remaining }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <iframe @load="onIframeLoaded('iframeArrival')" frameborder="0" scrolling="no" id="iframeArrival" width="100%" :src="arrivalUrl" ></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Departure Remaining</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.departure_remaining }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <iframe @load="onIframeLoaded('iframeDeparture')" id="iframeDeparture" width="100%" :src="departureUrl"></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Stay Over</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.stay_over }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <iframe @load="onIframeLoaded('iframeInhouse')" id="iframeInhouse" width="100%" :src="inhouseUrl"></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Upcoming note</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.upcoming_note }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <iframe @load="onIframeLoaded('iframeNote')" id="iframeNote"  width="100%" :src="upCommingNoteUrl"></iframe>
                </div>
            </TabPanel>
        </TabView>
    </div>
    <div class="mt-3">
        <ComPanel :title="'Monthly Occupancy (' + moment(working_day.date_working_day).format('MMM/YYYY') +')'">
            <MTDOccupancyChart />
        </ComPanel>
    </div>
</template>

<script setup>
import ComKPI from './components/ComKPI.vue';
import ComSystemDateKPI from './components/ComSystemDateKPI.vue';
import ComChartStatus from './components/ComChartStatus.vue';
import ComShowCancelOcc from './components/ComShowCancelOcc.vue';

import { inject, ref, onUnmounted , onMounted} from '@/plugin'

import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import iconEdoorAddGroupBooking from '../../assets/svg/icon-add-group-booking.svg'
import { useToast } from "primevue/usetoast";
import { useDialog } from 'primevue/usedialog';
import ComDashboardRowStatus from './components/ComDashboardRowStatus.vue';
import MTDOccupancyChart from './components/MTDOccupancyChart.vue';
import ComHousekeepingStatus from './components/ComHousekeepingStatus.vue';
import ComRoomStatusDoughnut from './components/ComRoomStatusDoughnut.vue';
import ComChartDoughnut from '../../components/chart/ComChartDoughnut.vue';
import ComIFrameModal from '@/components/ComIFrameModal.vue';
import ComReservationStayList from '@/views/frontdesk/components/ComReservationStayList.vue'
 
import io from 'socket.io-client';


const toast = useToast();
const socket = inject("$socket");
const moment = inject("$moment")
const gv = inject("$gv")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
 

function test(){
    io("http://192.168.10.19:9000").emit("RefresheDoorDashboard","xxx")
   alert(123)
}

socket.on("RefresheDoorDashboard", (arg) => {
    alert(11111)
    if(arg ==property.name){
        getData(false)
        toast.add({ severity: 'info', summary: 'Info', detail: "Dashboard is updated " + arg, life: 3000 })
    }    
    
})

 
const dialog = useDialog();

const api = inject('$frappe')
const data = ref({})
const date = ref(null)
const selected_date = ref(null)
const arrivalUrl = ref("");
const departureUrl = ref("");
const inhouseUrl = ref("");
const upCommingNoteUrl = ref("");
const chartOccupancy = ref([])
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const tomorrow = ref('')
const checked = ref(false);

function getArrivalUrl() {

    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&doctype=Business Branch&format="+ gv.getCustomPrintFormat("eDoor Dashboard Arrival Guest") +"&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0&action=view_arrival_remaining"
    url = url + "&date=" + selected_date.value

    return url;
}

function onViewData(doctype, report_name, title ,extra_params,filter_options ){
   
   const dialogRef = dialog.open(ComIFrameModal, {

       data: {
           "doctype": doctype,
           name: JSON.parse(localStorage.getItem("edoor_property")).name,
           report_name: report_name,
           view:"ui",
           extra_params:extra_params,
           filter_options:filter_options,
           fullheight: true
       },
       props: {
           header:title,
           style: {
               width: '90vw',
           },
           position:"top",
           modal: true,
           maximizable: true,
           closeOnEscape: false
       }
      
   });
}

function onRefresh(loading = true){ 
    getData(loading)
}

function onViewRoomOccupy(){
    onViewData(
        'Business%20Branch',
        "eDoor%20Room%20Occupy%20List",
        'Room Occupy',
        [{key:'date', value:selected_date}],
        ['keyword','business_source','room_type','reservation_status']
    )
}

function onViewVacantRoom(){
    onViewData(
        'Business%20Branch',
        "eDoor%20Vacant%20Room",
        'Vacant Room',
        [{key:'date', value:selected_date}],
        ['keyword','building','floor','room_type','housekeeping_status']
    )
   
}

function onViewRoomList(){
 
    onViewData(
        'Business%20Branch',
        "eDoor%20Room%20List",
        'Room List',
        [],
        ['keyword','building','floor','room_type_group','room_type','housekeeping_status']
    )
    
}


function onViewCancelReservation(){
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: "eDoor%20Cancel%20Reservation%20List",
            view:"ui",
            extra_params:[{key:"date", value:selected_date.value}]
        },
        props: {
            header:"Cancelled Reservation List",
            style: {
                width: '90vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
       
    });
}


function onViewNoShowReservation(){
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: "eDoor%20No%20Show%20Reservation%20List",
            view:"ui",
            extra_params:[{key:"date", value:selected_date.value}]
        },
        props: {
            header:"No Show Reservation List",
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


function getDepartureUrl() {
    
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&format=" + gv.getCustomPrintFormat("eDoor Dashboard Departure Guest") +  "&no_letterhead=1&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui&action=view_departure_remaining"
   
    

    url = url + "&date=" + selected_date.value
 
    return url;

}

function getInhouseGuestUrl() {
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&format=" + gv.getCustomPrintFormat("eDoor Dashboard Stay Over Guest") +  "&no_letterhead=0&letterhead=No%20Letter%20Head&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
    url = url + "&date=" + selected_date.value
    return url;

}

function getUpCommingNoteUrl() {
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&working_date=" + selected_date.value + "&format="
    + gv.getCustomPrintFormat("eDoor Up Coming Note") +  
 "&no_letterhead=0&letterhead=No%20Letter%20Head&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
    url = url + "&date=" + selected_date.value
    return url;

}

function onShowTodayData() {

    selected_date.value = data.value.working_date
    date.value = moment(data.value.working_date).format("DD-MM-YYYY")
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    upCommingNoteUrl.value = getUpCommingNoteUrl();
    getData()

    // this.classList.add("active");
}


function onShowTommorowData() {
    const today = moment(data.value.working_date);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = moment(tomorrow.value).format("YYYY-MM-DD")
    selected_date.value = tomorrow.value 
    date.value = moment(tomorrow.value).format("DD-MM-YYYY") 
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    upCommingNoteUrl.value = getUpCommingNoteUrl();
    getData()
}

function onDateSelect(event) {
    const today = moment(data.value.working_date);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = moment(tomorrow.value).format("YYYY-MM-DD")
    selected_date.value = moment(event).format("YYYY-MM-DD")
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    upCommingNoteUrl.value = getUpCommingNoteUrl();
    getData();
}

getData();


function getData(loading=true) { 
    gv.loading = loading;
    const call = api.call();
    if (!selected_date.value){
        const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))?.date_working_day
        selected_date.value = moment(edoor_working_day).format("YYYY-MM-DD")
    }
    if(!date.value){
        date.value = moment(selected_date.value).format("DD-MM-YYYY")
    }
    call.get('edoor.api.frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: selected_date.value
    })
        .then((result) => {

            data.value = result.message
            chartOccupancy.value = []
            const documentStyle = getComputedStyle(document.body);
            chartOccupancy.value.push({ label: 'Occupied', value: data.value.total_room_occupy, color: documentStyle.getPropertyValue('--bg-btn-green-color') })
            chartOccupancy.value.push({ label: 'Vacant', value: data.value.total_room_vacant, color: documentStyle.getPropertyValue('--bg-warning-color') })
            
           
            if (!selected_date.value) {
                date.value = moment(data.value.working_date).format("DD-MM-YYYY")
                tomorrow.value = moment(data.value.working_date).add(1,"days").format("YYYY-MM-DD")
                selected_date.value = data.value.working_date;
          
            }
            arrivalUrl.value = getArrivalUrl();
                departureUrl.value = getDepartureUrl();
                inhouseUrl.value = getInhouseGuestUrl();
                upCommingNoteUrl.value = getUpCommingNoteUrl();

            gv.loading = false;

        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Waring', detail: error.exception ? error.exception.split(":")[1] : '', life: 3000 })
            gv.loading = false;

        });
}
 
function onIframeLoaded(id){
    const iframe = document.getElementById(id);
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
    // iframe.width = iframe.contentWindow.document.body.scrollWidth;

    // const iframe = document.getElementById("iframe");
    var contentWidth = iframe.contentWindow.document.body.scrollWidth;
    var windowWidth = window.innerWidth;
    
    console.log(windowWidth)
    
    if (windowWidth >= 1920){
        iframe.style.minWidth = 100 + '%'
    }
    else{
        iframe.style.width = contentWidth + 'px';
    }
    iframe.height = iframe.contentWindow.document.body.scrollHeight;
}

const viewSummary = (name) => { 
 
        const filters = [
            ['property','=',property.name]
        ]
        if(name == "Arrival"){
            onViewData(
                'Business%20Branch',
                "eDoor%20Dashboard%20Arrival%20Guest",
                'Arrival Guest',
                [{key:'action', value:"view_arrival"},{key:"date", value:selected_date.value}],
                ['keyword','building','floor','room_type','reservation_status']
            )
        }else if(name=="Check-In Remaining") {
            onViewData(
                'Business%20Branch',
                "eDoor%20Dashboard%20Arrival%20Guest",
                'Check-in Remaining',
                [{key:'action', value:"view_arrival_remaining"},{key:"date", value:selected_date.value}],
                ['keyword','building','floor','room_type']
            )
        }
        else if(name == "Departure"){
            onViewData(
                'Business%20Branch',
                "eDoor%20Dashboard%20Departure%20Guest",
                'Departure',
                [{key:'action', value:"view_departure"},{key:"date", value:selected_date.value}],
                ['keyword','building','floor','room_type','reservation_status','business_source']
            )
        }
        else if(name == "Check-out remaining"){
            onViewData(
                'Business%20Branch',
                "eDoor%20Dashboard%20Departure%20Guest",
                'Check-out Remaining',
                [{key:'action', value:"view_departure_remaining"},{key:"date", value:selected_date.value}],
                ['keyword','building','floor','room_type','reservation_status','business_source']
            )
        }
        else if(name == "Unassign Room"){
 
             onViewData(
                'Business%20Branch',
                "eDoor%20Unassign%20Room%20Reservation%20List",
                'Unassign Room Reservation List',
                [{key:"date", value:selected_date.value}],
                ['keyword','room_type','reservation_status','business_source']
            )
        }
        else if(name == "Pickup and Drop Off"){
            onViewData(
                'Business%20Branch',
                "eDoor%20Pickup%20and%20Drop%20Off%20Reservation%20List",
                'Pickup & Drop Off',
                [{key:'action', value:"view_departure_remaining"},{key:"date", value:selected_date.value}],
                ['keyword','room_type','reservation_status','business_source',"transportation_mode",'transportation_company']
            )
             
        }
        else if(name == "GIT Arrival"){
            onViewData(
                'Business%20Branch',
                "eDoor%20GIT%20Arrival%20Guest",
                'GIT Arrival',
                [{key:"date", value:selected_date.value}],
                ['keyword','room_type','reservation_status','business_source']
            )
        }
        else if(name == "Stay Over"){
           onViewData(
                'Business%20Branch',
                "eDoor%20Dashboard%20Stay%20Over%20Guest",
                'Stay Over',
                [{key:"date", value:selected_date.value}],
                ['keyword','room_type','reservation_status','business_source']
            )
        }
         
}

onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
})

 

</script>