<template>
    <div class="flex flex-column md:flex-row md:justify-content-between row-gap-3 py-2">
        <div class="text-start">
            <div class="font-bold">{{ property.name }}</div>
            <div class="txt-st__det">ID: {{ property.property_code }}, {{ property.province }}</div>
        </div>
        <div class="text-center">
            <Button label="Today" class="w-48 h-12 btn-date__t" :class="selected_date == data.working_date ? 'active' : ''"
                @click="onShowTodayData()" />
            <Button label="Tomorrow" class="w-48 h-12 btn-date__t" :class="selected_date == tomorrow ? 'active' : ''"
                @click="onShowTommorowData()" />
            <Calendar v-model="date" class="w-48 h-12 btn-calendar__t h-res__setting" @date-select="onDateSelect"
                dateFormat="dd-MM-yy" showIcon />
        </div>
        <div class="text-end flex justify-end">
            <div class="mr-2">
                <NewFITReservationButton />
            </div>
            <div>
                <Button label="New group booking" class="btn-date__tt btn-inner-set-icon h-12">
                    <img class="mr-2" :src="iconEdoorAddGroupBooking">New group booking
                </Button>
            </div>
        </div>
    </div>
    <div class="grid">
        <div class="col-2">
            <ComSystemDateKPI :data="data"></ComSystemDateKPI>
        </div>
        <div class="col ">
            <ComPanel title="Today's occupancy">
                <div class="grid">
                    <div class="col-6 flex align-items-center justify-content-center">
                        <ComdonutChart :value_doughnut=data.total_room_occupy :value_room_vacant=data.total_room_vacant
                            :value_total_room=data.total_room></ComdonutChart>
                    </div>
                    <div class="col-5">
                        <ComChartStatus :value="data.total_room_occupy" title="Occupied" class="btn-green-edoor">
                        </ComChartStatus>
                        <ComChartStatus :value="data.total_room_vacant" title="Vacant" class="bg-warning-edoor">
                        </ComChartStatus>
                        <ComChartStatus :value="data.total_room" title="Total rooms" class="btn-sec-edoor">
                        </ComChartStatus>
                        <div class="grid mt-3 text-center">
                            <ComShowCancelOcc title="Canceled" :value="0"></ComShowCancelOcc>
                            <ComShowCancelOcc title="No-show" :value="0"></ComShowCancelOcc>
                        </div>
                    </div>
                </div>
            </ComPanel>
        </div>
        <div class="col">
            <ComPanel title="Today's actions">
                <div class="grid grid-cols-4 pt-3 px-2 pb-0 text-white">
                    <ComKPI :value="data.arrival" title="Arrival" class="primary-btn-edoor"> </ComKPI>
                    <ComKPI :value="data.arrival_remaining" title="Check-in remaining" class="primary-btn-edoor"> </ComKPI>
                    <ComKPI :value="data.departure" title="Departure" class="primary-btn-edoor"> </ComKPI>
                    <ComKPI :value="data.departure_remaining" title="Check-out remaining" class="primary-btn-edoor">
                    </ComKPI>
                    <ComKPI :value="data.pick_up" title="Pickup" class="bg-warning-edoor"> </ComKPI>
                    <ComKPI :value="data.drop_off" title="Drop off" class="bg-og-edoor"> </ComKPI>
                    <ComKPI :value="15" title="GIT Arrival" class="primary-btn-edoor"> </ComKPI>
                    <ComKPI :value="15" title="Stayover" class="primary-btn-edoor"> </ComKPI>
                </div>
            </ComPanel>
        </div>
        <div class="col-2">
            <ComPanel title="Room Status">
                <div class="px-1">
                    <template v-for="(item, index) in data.housekeeping_status" :key="index">
                        <ComDashboardRowStatus :value="item.total" :badgeColor="item.color" :icon="item.icon">
                            <template #content>{{ item.status }}</template> >
                        </ComDashboardRowStatus>
                    </template>
                </div>
            </ComPanel>
        </div>
    </div>

    <div class="px-2 py-2 bg-white mt-2">
        <TabView class="tabview-custom">
            <TabPanel>
                <template #header>
                    <span>Arrivals</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.arrival }}</span>
                </template>
                <div class="mt-2">
                    <iframe style="height: 500px;" width="100%" :src="arrivalUrl"></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Departures</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.departure }}</span>
                </template>
                <div class="mt-2">
                    <iframe style="height: 500px;" width="100%" :src="departureUrl"></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Stayover</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.departure_remaining
                    }}</span>
                </template>
                <div class="mt-2">
                    <iframe style="height: 500px;" width="100%" :src="inhouseUrl"></iframe>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span>Upcoming note</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.departure_remaining
                    }}</span>
                </template>
                <div class="mt-2">
                    <iframe style="height: 500px;" width="100%" :src="inhouseUrl"></iframe>
                </div>
            </TabPanel>
        </TabView>
    </div>
    <div class="mt-3">
        <ComPanel title="Monthly occupancy (May/2023)">
            <MTDOccupancyChart />
        </ComPanel>
    </div>
</template>

<script setup>
import ComKPI from './components/ComKPI.vue';
import ComSystemDateKPI from './components/ComSystemDateKPI.vue';
import ComdonutChart from './components/ComDonutChart.vue';
import ComChartStatus from './components/ComChartStatus.vue';
import ComShowCancelOcc from './components/ComShowCancelOcc.vue';

import { inject, ref, onUnmounted } from '@/plugin'

import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import iconEdoorAddGroupBooking from '../../assets/svg/icon-add-group-booking.svg'
import { useToast } from "primevue/usetoast";
import { useDialog } from 'primevue/usedialog';
import ComDashboardRowStatus from './components/ComDashboardRowStatus.vue';
import MTDOccupancyChart from './components/MTDOccupancyChart.vue';
const toast = useToast();
const socket = inject("$socket");
const moment = inject("$moment")
const gv = inject("$gv")

socket.on("RefresheDoorDashboard", (arg) => {
    console.log(arg)
    toast.add({ severity: 'info', summary: 'Info', detail: "Dashboard is updated", life: 3000 })
})




const dialog = useDialog();

const api = inject('$frappe')
const data = ref({})
const date = ref(null)
const selected_date = ref(null)
const arrivalUrl = ref("");
const departureUrl = ref("");
const inhouseUrl = ref("");
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const tomorrow = ref('')
function getArrivalUrl() {
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&doctype=Business Branch&format=eDoor%20Dashboard%20Arrival%20Guest&no_letterhead=0&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en&view=ui&show_toolbar=0"
    url = url + "&working_date=" + selected_date.value
    return url;
}

function getDepartureUrl() {
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&format=eDoor%20Dashboard%20Departure%20Guest&no_letterhead=1&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
    url = url + "&working_date=" + selected_date.value
    return url;

}

function getInhouseGuestUrl() {
    let url = serverUrl + "/printview?doctype=Business%20Branch&name=" + property.name + "&format=eDoor%20Dashboard%20Stay%20Over%20Guest&no_letterhead=0&letterhead=No%20Letter%20Head&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui"
    url = url + "&working_date=" + selected_date.value
    return url;

}

function onShowTodayData() {

    selected_date.value = data.value.working_date
    date.value = moment(data.value.working_date).format("DD-MM-YYYY")
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    getData()

    // this.classList.add("active");
}


function onShowTommorowData() {
    const today = moment(data.value.working_date);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = tomorrow.value.format("YYYY-MM-DD")
    selected_date.value = tomorrow.value
    date.value = tomorrow.value.format("DD-MM-YYYY")
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    getData()
}

function onDateSelect(event) {

    selected_date.value = moment(event).format("YYYY-MM-DD")
    arrivalUrl.value = getArrivalUrl();
    departureUrl.value = getDepartureUrl();
    inhouseUrl.value = getInhouseGuestUrl();
    getData();
}

getData();


function getData() {
    gv.loading = true;
    const call = api.call();
    call.get('edoor.api.frontdesk.get_dashboard_data', {
        property: JSON.parse(localStorage.getItem("edoor_property")).name,
        date: selected_date.value
    })
        .then((result) => {

            data.value = result.message

            if (!selected_date.value) {
                date.value = moment(data.value.working_date).format("DD-MM-YYYY")
                selected_date.value = data.value.working_date;
                arrivalUrl.value = getArrivalUrl();
                departureUrl.value = getDepartureUrl();
                inhouseUrl.value = getInhouseGuestUrl();
            }

            gv.loading = false;

        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Waring', detail: error.exception.split(":")[1], life: 3000 })
            gv.loading = false;

        });
}






</script>
<style scoped></style>