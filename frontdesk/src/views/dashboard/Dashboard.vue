<template> 
    <ComHeader isRefresh @onRefresh="onRefresh()">
        <template #start>
            <div class="flex justify-content-between align-content-center">
                <div class="col">
            <div class="text-2xl text-overflow-ellipsis">{{ property.name }}</div>
            <div class="txt-st__det" v-if="property.property_code">ID: {{ property.property_code }}, {{ property.province }}
            </div>
</div>
            <div class="col pt-3" v-if="isMobile">
                <ComNewReservationMobileButton/>
            </div>
        </div>
        </template>
        <template #center>
            <Button :label="$t('Today')" class="w-8rem md:w-12rem btn-date__t border-noround-right border-none"
                :class="selected_date == data.working_date ? 'active' : ''" @click="onShowTodayData()" />
            <Button :label="$t('Tomorrow')" class="w-8rem md:w-12rem btn-date__t border-noround border-x-none border-none"
                :class="selected_date == tomorrow ? 'active' : ''" @click="onShowTommorowData()" />
                <Calendar v-model="date" :selectOtherMonths="true" class="w-48 das-calendar" panelClass="no-btn-clear"
                @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar />

              
        </template>
        <template #end>
            <div v-if="!isMobile" class="flex gap-2 justify-content-end">
                <NewFITReservationButton />
                <NewGITReservationButton />
 
            </div>
        </template>
    </ComHeader>
    <div class="grid">
        <div class="col-12 md:col-6 lg:col-2">
            <ComSystemDateKPI :data="data"></ComSystemDateKPI>
        </div>
        <div class="col-12 md:col-6 lg:col">
            <div class="bg-white h-full border-round-lg">
                <ComPanel :title="$t('Occupancy')">
                    <div class="grid">
                        <div class="col-12 md:col-6 flex align-items-center justify-content-center mt-3">

                            <ComChartDoughnut :percentage="data?.occupancy" show-percentage="Occupied"
                                :showPercentageInteger="false" :is-legend="false" :data="chartOccupancy"
                                v-if="chartOccupancy.length > 0" />
                            <Skeleton v-else shape="circle" size="18rem"></Skeleton>
                        </div>
                        <div class="col-12 md:col-5">
                            <ComChartStatus @onClick="onViewRoomOccupy" :value="data.total_room_occupy" :title="$t('Occupied')"
                                class="btn-green-edoor"></ComChartStatus>

                            <ComChartStatus @onClick="onViewVacantRoom" :value="data.total_room_vacant" :title="$t('Vacant')"
                                class="bg-warning-edoor">


                            </ComChartStatus>
                            <ComChartStatus @onClick="onViewRoomList" :value="data.total_room" :title="$t('Total Rooms')"
                                class="btn-sec-edoor">
                            </ComChartStatus>
                            <tippy
                                :content="$t('Today') + ' ' + $t('No-Show') + ' ' + data.today_no_show + ' & ' + $t('No-Show With Reserved Room') + ' ' + data.total_no_show">
                                <ComChartStatus @onClick="onViewNoShowReservation"
                                    :value="!gv.loading ? (data?.today_no_show + ' / ' + data?.total_no_show) : ''"
                                    :title="$t('No-Show')" :style="{ backgroundColor: statusColor.no_show }">
                                </ComChartStatus>
                            </tippy>
                            <tippy
                                :content="$t('Today') + ' ' + $t('Cancelled') + ' ' + data.today_cancelled + ' & ' + $t('Cancelled') + ' ' + data.total_cancelled">
                                <ComChartStatus @onClick="onViewCancelReservation"
                                    :value="!gv.loading ? (data.today_cancelled + ' / ' + data.total_cancelled) : ''"
                                    :title="$t('Cancelled')" :style="{ backgroundColor: statusColor.cancelled }">
                                </ComChartStatus>
                            </tippy>
                            <ComChartStatus v-tippy="$t('Today') + ' ' + $t('Void') + ' ' + data.today_void + ' & ' + $t('Void') + data.total_void"
                                @onClick="onViewVoidReservation"
                                :value="!gv.loading ? (data.today_void + ' / ' + data.total_void) : ''" :title="$t('Void')"
                                :style="{ backgroundColor: statusColor.void }">
                            </ComChartStatus>
                        </div>
                    </div>
                </ComPanel>
            </div>
        </div>
        <div class="col-12  md:col-6 lg:col">
            <div class="bg-white h-full border-round-lg">
                <ComPanel :title="$t('Summary')">
                    <div class="grid grid-cols-4 pt-3 px-2 pb-0 text-white">

                        <ComKPI v-tippy="((data?.arrival || 0) - (data?.arrival_remaining || 0)) + ' ' + $t('Checked-in') + ' & ' +  $t('Total Arrival') + ' ' + (data?.arrival|| 0) " @onClick="viewSummary('Arrival')" :value="!gv.loading ? ( (  ((data.arrival || 0) -(data.arrival_remaining || 0)) + '/' + data?.arrival ||0)) :''" :title="$t('Arrival')"
                            class="primary-btn-edoor cursor-pointer border-round-lg"> </ComKPI>
                        <ComKPI @onClick="viewSummary('Stay Over')" :value="data.stay_over" :title="$t('Stay Over')"
                            class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>
                        <ComKPI v-tippy="((data?.departure ||0) - (data?.departure_remaining ||0)) + ' ' + $t('Checked-out') + ' & '+ $t('Total Departure') + ' ' + (data?.departure ||0)   " @onClick="viewSummary('Departure')" :value="!gv.loading ? ( (data.departure - data?.departure_remaining)  +'/'+  data?.departure ||0) : ''" :title="$t('Departure')"
                            class="primary-btn-edoor border-round-lg cursor-pointer">
                        </ComKPI>
                        <ComKPI @onClick="viewSummary('Daily Reservation')" v-tippy=" $t('Total Reservation') + ' ' + data.daily_reservation + ' & ' + $t('Total Reservation Stay') + ' ' +  data?.daily_reservation_stay" :value="!gv.loading ? data.daily_reservation + '/' + data?.daily_reservation_stay : ''"
                            :title="$t('Daily Reservation')" class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>
                        
                            <ComKPI
                            v-tippy="$t('FIT (Free Independent Traveler) Total') + ' ' + data.fit_reservation_arrival + ' & ' + $t('Total Stay') + ' '  + data.fit_stay_arrival"
                            @onClick="viewSummary('FIT Arrival')"
                            :value="!gv.loading ? (data.fit_reservation_arrival + '/' + data.fit_stay_arrival) : ''"
                            :title="$t('FIT Arrival')" class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>

                        <ComKPI
                            v-tippy="$t('GIT (Group Inclusive Tour) Total') + ' ' + data.git_reservation_arrival + ' & ' +$t('Total Stay') + ' ' + data.git_stay_arrival"
                            @onClick="viewSummary('GIT Arrival')"
                            :value="!gv.loading ? (data.git_reservation_arrival + '/' + data.git_stay_arrival) : ''"
                            :title="$t('GIT Arrival')" class="primary-btn-edoor border-round-lg cursor-pointer"> </ComKPI>
                        <ComKPI v-tippy="$t('Today') + ' ' + (data?.unassign_room || 0) + ' ' + $t('Unassign Room') + ' & ' + $t('Total Unassign Room') + ' ' + (data?.total_unassign_room || 0)"
 @onClick="viewSummary('Unassign Room')" :value="!gv.loading ? ( data.unassign_room + '/' + data.total_unassign_room ) : ''" :title="$t('Unassign Room')"
                            class="bg-og-edoor border-round-lg cursor-pointer"> </ComKPI>
                        <ComKPI @onClick="viewSummary('Pickup and Drop Off')"
                            :value="!gv.loading ? (data.pick_up + '/' + data.drop_off) : ''" :title="$t('Pickup') + '/' + $t('Drop Off')"
                            class="bg-warning-edoor border-round-lg cursor-pointer"> </ComKPI>

                    </div>
                </ComPanel>
            </div>
        </div>
        <div class="col-12 md:col-6 lg:col-2">
            <ComPanel title="Room Status" class="h-full">
                <ComHousekeepingStatus />
            </ComPanel>
        </div>
    </div>
    <div class="my-3">
        <ComPanel :title="$t('Monthly Occupancy') + ' (' + moment(working_day.date_working_day).format('MMM/YYYY') + ')'">
            <OccupancyChart />
        </ComPanel>
    </div>
    <div class="px-3 py-3 bg-white mt-2 border-round-xl tab-reserv-no">
        <TabView class="tabview-custom" lazy>
            <TabPanel>
                <template #header>
                    <span class="white-space-nowrap">{{ $t('Arrival Remaining') }}  </span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.arrival_remaining
                    }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                        <div v-html="arrival_remaining_html" class="view_table_style min_table_ui_height "></div>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="white-space-nowrap" >{{ $t('Departure Remaining') }}</span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.departure_remaining
                    }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <div v-html="departure_remaining_html" class="view_table_style min_table_ui_height"></div>
                    
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="white-space-nowrap" > {{ $t('Stay Over') }} </span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.stay_over }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <div v-html="stay_over_html" class="view_table_style min_table_ui_height"></div>
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="white-space-nowrap" > {{ $t('Upcoming note') }} </span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.upcoming_note }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <div v-html="upcoming_note_html" class="view_table_style min_table_ui_height"></div>
                        
                </div>
            </TabPanel>
            <TabPanel>
                <template #header>
                    <span class="white-space-nowrap" > {{ $t('Desk Folio') }} </span>
                    <span class="py-1 px-2 text-white ml-2 bg-amount__guest border-round">{{ data.desk_folio }}</span>
                </template>
                <div class="mt-2 view-table-iframe" v-if="!gv.loading">
                    <div v-html="desk_folio_html" class="view_table_style min_table_ui_height"></div>
                </div>
            </TabPanel>
        </TabView>
    </div>
    <div id="myChart"></div>
</template>

<script setup>
import { inject, ref, onUnmounted, onMounted, computed } from '@/plugin'
import { useToast } from "primevue/usetoast";
import { useDialog } from 'primevue/usedialog';
import ComKPI from './components/ComKPI.vue';
import ComSystemDateKPI from './components/ComSystemDateKPI.vue';
import ComChartStatus from './components/ComChartStatus.vue';
import ComShowCancelOcc from './components/ComShowCancelOcc.vue';
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ComNewReservationMobileButton from "@/views/dashboard/components/ComNewReservationMobileButton.vue"
import OccupancyChart from './components/OccupancyChart.vue';
import ComHousekeepingStatus from './components/ComHousekeepingStatus.vue';
import ComChartDoughnut from '../../components/chart/ComChartDoughnut.vue';
import ComIFrameModal from '@/components/ComIFrameModal.vue';
const isMobile = ref(window.isMobile) 
const toast = useToast();
const moment = inject("$moment")
const gv = inject("$gv")
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const dialog = useDialog();
const api = inject('$frappe')
const data = ref({})
const date = ref(null)
const selected_date = ref(null)
const arrivalUrl = ref("");
const departureUrl = ref("");
const inhouseUrl = ref("");
const deskFolioUrl = ref("")
const upCommingNoteUrl = ref("");
const chartOccupancy = ref([])
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const serverUrl = window.location.protocol=="http:"?"http://" + window.location.hostname + ":" + window.setting.backend_port:"https://" + window.location.hostname;
const tomorrow = ref('')
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const statusColor = computed(() => {
    if (setting.reservation_status) {
        return {
            cancelled: setting.reservation_status.find((r) => r.reservation_status == 'Cancelled') ? setting.reservation_status.find((r) => r.reservation_status == 'Cancelled').color || '#ed6396' : '#ed6396',
            no_show: setting.reservation_status.find((r) => r.reservation_status == 'No Show') ? setting.reservation_status.find((r) => r.reservation_status == 'No Show').color || '#828205' : '#828205',
            void: setting.reservation_status.find((r) => r.reservation_status == 'Void') ? setting.reservation_status.find((r) => r.reservation_status == 'Void').color || '#ff0000' : '#ff0000'
        }
    }

})
const frappe = inject("$frappe")
const call = frappe.call()
const param = ref({})
const arrival_remaining_html = ref()
const departure_remaining_html = ref()
const stay_over_html = ref()
const upcoming_note_html = ref()
const desk_folio_html = ref()
const getframeui = (format, action, html) =>  {
    param.value.doc = decodeURIComponent("Business Branch")
    param.value.name = decodeURIComponent(property.name)
    param.value.format = decodeURIComponent(gv.getCustomPrintFormat(format))
    param.value._lang = localStorage.getItem("lang") || "en"
    param.value.letterhead = decodeURIComponent("No Letterhead")
    param.value.no_letterhead = 1
    param.value.show_toolbar = 0
    param.value.can_view_rate = window.can_view_rate
    param.value.view = "ui"
    param.value.date = selected_date.value
    param.value.settings = decodeURIComponent("%7B%7D")
    param.value.refresh = (Math.random() * 16)
    if(action)(
      param.value.action = action  
    )
    call.get("epos_restaurant_2023.www.printview.get_html_and_style", param.value).then(result => {
        html.value = result.message.html
        gv.loading = loading;    
        }).catch(err => {
            
        })
        
}

function onViewData(doctype, report_name, title, extra_params, filter_options) {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": doctype,
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: report_name,
            view: "ui",
            extra_params: extra_params,
            filter_options: filter_options,
            fullheight: true
        },
        props: {
            header: $t(title),
            style: {
                width: '90vw',
            },
            position: "top",
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

const onRefresh = debouncer(() => {
    getData()
}, 500);


function onViewRoomOccupy() {
    onViewData(
        'Business%20Branch',
        // "eDoor%20Room%20Occupy%20List",
        gv.getCustomPrintFormat("eDoor Room Occupy List"),
        'Room Occupy',
        [{ key: 'date', value: selected_date }],
        ['keyword', 'business_source', 'room_type', 'reservation_status']
    )
}

function onViewVacantRoom() {
    onViewData(
        'Business%20Branch',
        // "eDoor%20Vacant%20Room",
        gv.getCustomPrintFormat("eDoor Vacant Room"),
        'Vacant Room',
        [{ key: 'date', value: selected_date }],
        ['keyword', 'building', 'floor', 'room_type', 'housekeeping_status']
    )
}

function onViewRoomList() {
    onViewData(
        'Business%20Branch',
        // "eDoor%20Room%20List",
        gv.getCustomPrintFormat("eDoor Room List"),
        'Room List',
        [],
        ['keyword', 'building', 'floor', 'room_type_group', 'room_type', 'housekeeping_status']
    )
}


function onViewCancelReservation() {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: gv.getCustomPrintFormat("eDoor Cancel Reservation List"),
            view: "ui",
            extra_params: [{ key: "date", value: selected_date.value }]
        },
        props: {
            header: "Cancelled Reservation List",
            style: {
                width: '90vw',
            },
            position: "top",
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


function onViewNoShowReservation() {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: gv.getCustomPrintFormat("eDoor No Show Reservation List"),
            view: "ui",
            extra_params: [{ key: "date", value: selected_date.value }]
        },
        props: {
            header: "No Show Reservation List",
            style: {
                width: '80vw',
            },
            position: "top",
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

function onViewVoidReservation() {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: gv.getCustomPrintFormat("eDoor Void Reservation List"),
            view: "ui",
            extra_params: [{ key: "date", value: selected_date.value }]
        },
        props: {
            header: "Void Reservation List",
            style: {
                width: '80vw',
            },
            position: "top",
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

function onShowTodayData() {
    selected_date.value = data.value.working_date
    date.value = moment(data.value.working_date).format("DD-MM-YYYY")
    onRefreshIframe();
    getData()
    // this.classList.add("active");
}


function onShowTommorowData() {
    const today = moment(data.value.working_date);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = moment(tomorrow.value).format("YYYY-MM-DD")
    selected_date.value = tomorrow.value
    date.value = moment(tomorrow.value).format("DD-MM-YYYY")
    onRefreshIframe()
    getData()
}

function onDateSelect(event) {
    const today = moment(data.value.working_date);
    tomorrow.value = today.add(1, 'days');
    tomorrow.value = moment(tomorrow.value).format("YYYY-MM-DD")
    selected_date.value = moment(event).format("YYYY-MM-DD")
    onRefreshIframe();
    getData();
}

getData();

function getData(loading = true) {
    gv.loading = loading;
    const call = api.call();
    if (!selected_date.value) {
        const edoor_working_day = JSON.parse(localStorage.getItem('edoor_working_day'))?.date_working_day
        selected_date.value = moment(edoor_working_day).format("YYYY-MM-DD")
    }
    if (!date.value) {
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
                tomorrow.value = moment(data.value.working_date).add(1, "days").format("YYYY-MM-DD")
                selected_date.value = data.value.working_date;
            }
            onRefreshIframe()
            gv.loading = false;
        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: 'Waring', detail: error.exception ? error.exception.split(":")[1] : '', life: 3000 })
            gv.loading = false;

        });
}

function onRefreshIframe() {
    getframeui("eDoor Dashboard Arrival Guest","view_arrival_remaining",arrival_remaining_html)
    getframeui("eDoor Dashboard Departure Guest","view_departure_remaining",departure_remaining_html)
    getframeui("eDoor Dashboard Stay Over Guest",false,stay_over_html)
    getframeui("eDoor Up Coming Note",false,upcoming_note_html)
    getframeui("eDoor Desk Folio",false,desk_folio_html)
}

const viewSummary = (name) => {
    const filters = [
        ['property', '=', property.name]
    ]
    if (name == "Arrival") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Arrival Guest"),
            'Arrival Guest',
            [{ key: 'action', value: "view_arrival" }, { key: "date", value: selected_date.value }],
            ['keyword', 'building', 'floor', 'room_type', 'reservation_status']
        )
    } else if (name == "Check-In Remaining") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Arrival Guest"),
            'Check-in Remaining',
            [{ key: 'action', value: "view_arrival_remaining" }, { key: "date", value: selected_date.value }],
            ['keyword', 'building', 'floor', 'room_type']
        )
    }
    else if (name == "Departure") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Departure%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Departure Guest"),
            'Departure',
            [{ key: 'action', value: "view_departure" }, { key: "date", value: selected_date.value }],
            ['keyword', 'building', 'floor', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "Check-out remaining") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Departure%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Departure Guest"),
            'Check-out Remaining',
            [{ key: 'action', value: "view_departure_remaining" }, { key: "date", value: selected_date.value }],
            ['keyword', 'building', 'floor', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "Unassign Room") {

        onViewData(
            'Business%20Branch',
            // "eDoor%20Unassign%20Room%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Unassign Room Reservation List"),
            'Unassign Room Reservation List',
            [{ key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "Pickup and Drop Off") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Pickup%20and%20Drop%20Off%20Reservation%20List",
            gv.getCustomPrintFormat("eDoor Pickup and Drop Off Reservation List"),
            'Pickup & Drop Off',
            [{ key: 'action', value: "view_departure_remaining" }, { key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source', "transportation_mode", 'transportation_company']
        )

    }
    else if (name == "GIT Arrival") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20GIT%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor GIT Arrival Guest"),
            'GIT Arrival',
            [{ key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "FIT Arrival") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20GIT%20Arrival%20Guest",
            gv.getCustomPrintFormat("eDoor FIT Arrival Guest"),
            'FIT Arrival',
            [{ key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "Stay Over") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Stay%20Over%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Stay Over Guest"),
            'Stay Over',
            [{ key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source']
        )
    }
    else if (name == "Daily Reservation") {
        onViewData(
            'Business%20Branch',
            // "eDoor%20Dashboard%20Stay%20Over%20Guest",
            gv.getCustomPrintFormat("eDoor Dashboard Daily Reservation"),
            'Daily Reservation For '+ moment(selected_date.value).format("DD-MM-YYYY"),
            [{ key: "date", value: selected_date.value }],
            ['keyword', 'room_type', 'reservation_status', 'business_source']
        )
    }
}

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
} 
const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="Dashboard"){
            setTimeout(()=>{
                getData(false)
                onRefreshIframe()
            },e.data.delay || 1000*10)
        }
    };
}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', actionRefreshData, false); 
})

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
    
})

</script>