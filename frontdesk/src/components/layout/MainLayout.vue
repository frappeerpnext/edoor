<template>
    <div class="wrap-page">
        <ProgressBar class="absolute top-0 right-0 left-0" style="z-index: 9999; height: 6px" v-if="gv.loading"
            mode="indeterminate">
        </ProgressBar>
        <div class="header-bar w-full">
            <div class="mx-auto flex items-stretch h-full">
                <div class="header-logo flex-auto h-full">
                    <div class="flex h-full wrap-pro-bar top-pro-bar-cus">

                        <ComHeaderBarItemButton title="eDoor Dashboard" current-page="Dashboard"
                            @onClick="onRoute('Dashboard')">
                            <template #icon>
                                <img :src="iconEdoorDashboard" />
                            </template>
                            <template #defualt>
                                <p>eDoor</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Frontdesk" current-page="Frontdesk" @onClick="onRoute('Frontdesk')">
                            <template #icon>
                                <img :src="iconEdoorFrontdesk">
                            </template>
                            <template #defualt>
                                <p>Frontdesk</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Reservations" current-page="ReservationList"
                            @onClick="onRoute('ReservationList')">
                            <template #icon>
                                <img :src="iconEdoorReservation">
                            </template>
                            <template #defualt>
                                <p title="Reservations">Reservations</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Guest Database" @onClick="onRoute('GuestDatabase')">
                            <template #icon>
                                <img :src="iconEdoorGuestDatabase">
                            </template>
                            <template #defualt>
                                <p title="Guest Database">Guest Database</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton current-page="Housekeeping" title="Housekeeping" icon="pi-users" @onClick="onRoute('Housekeeping')">
                            <template #icon>
                                <img :src="iconEdoorHouseKeeping">
                            </template>
                            <template #defualt>
                                <p title="Housekeeping">Housekeeping</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton current-page="Guest Ledger" title="Guest Ledger" @onClick="onLink('guest-ledger')">
                            <template #icon>
                                <img :src="iconGuestLedger">
                            </template>
                            <template #defualt>
                                <p title="Guest Ledger">Guest Ledger</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="City Ledger" @onClick="onLink('city-ledger')"
                            class="hidden xl:block">
                            <template #icon>
                                <img :src="iconEdoorCityLedger">
                            </template>
                            <template #defualt>
                                <p title="City Ledger">City Ledger</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Reports" @onClick="onLink('reports')" class="hidden xl:block">
                            <template #icon>
                                <img :src="iconEdoorReport">
                            </template>
                            <template #defualt>
                                <p title="Reports">Reports</p>
                            </template>
                        </ComHeaderBarItemButton>

                        <!-- <ComHeaderBarItemButtonMore /> -->
                    </div>
                </div>
                <div class="flex-grow">
                    <div class="mr-auto flex justify-end h-full items-center">
                        <div class="px-2 flex items-center text-white pro-timebar">
                            <ComHeaderDateTimeUpdate />
                        </div>
                        <div class="px-2 flex items-center">
                            <div>
                                <Button icon="pi pi-search btn-search-top" text rounded severity="secondary"
                                    aria-label="Search" class="p-link text-white" @click="onSearch" />
                            </div>
                            <div>
                                <Button icon="pi pi-cog btn-setting-top" text rounded severity="secondary"
                                    aria-label="Setting" class="p-link text-white" @click="toggle" aria-haspopup="true"
                                    aria-controls="overlay_menu" />
                            </div>
                            <Menu ref="show" id="overlay_menu" :popup="true" style="min-width: 180px;">
                                <template #end>
                                    <button @click="changeProperty"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround"
                                        v-if="user.property.length > 1">
                                        <i class="pi pi-building" />
                                        <span class="ml-2">Change property</span>
                                    </button>

                                    <button @click="onBlankGuestRegistration"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-file" />
                                        <span class="ml-2">Blank Guest Registration</span>
                                    </button>
                                    <!-- <button @click="onOpenCashierShift" v-if="!gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-refresh" />
                                        <span class="ml-2">Open cashier shift</span>
                                    </button> -->
                                    <button @click="onOpenCashierShift"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-refresh" />
                                        <span class="ml-2">Open cashier shift</span>
                                    </button>
                                    <button @click="onViewShiftDetail" v-if="gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-eye" />
                                        <span class="ml-2">View Shift Detail</span>
                                    </button>
                                    
                                    <button @click="onCloseCashierShift" v-if="gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-ban" />
                                        <span class="ml-2">Close cashier shift</span>
                                    </button>

                                    <button @click="onRunNightAudit"
                                        class="w-full p-link flex align-items-center p-2 pl-3 text-color hover:surface-200 border-noround">
                                        <img :src="runNightAuditSvgIcon" style="height: 15px;"/>
                                        <span class="ml-2">Run night audit</span>
                                    </button>
                                </template>
                            </Menu>
                        </div>
                        <ComAvatarUserProfile :user="user" />
                    </div>
                </div>
            </div>
        </div>
        <div>
            <div class="wrap-page-content -mb-2 px-2">
                <router-view />
            </div>
            <div v-if="route.name != 'Frontdesk'" class="mt-3" style="height: 22px;"></div>
            <ComFooter />
        </div>

    </div>
</template>

<script setup>
import { ref, inject, useToast, useRouter, useRoute } from '@/plugin'
import ComAvatar from '../form/ComAvatar.vue';
import ComAvatarUserProfile from './components/ComAvatarUserProfile.vue'
import ProgressBar from 'primevue/progressbar';
import ComHeaderDateTimeUpdate from './components/ComTimeUpdate.vue';
import ComHeaderBarItemButton from './components/ComHeaderBarItemButton.vue'
import ComHeaderBarItemButtonMore from './components/ComHeaderBarItemButtonMore.vue';
import iconGuestLedger from '../../assets/svg/icon-guest-ledger.svg'
import iconEdoorDashboard from '../../assets/svg/icon-edoor-dashboard.svg'
import iconEdoorReservation from '../../assets/svg/icon-reservation.svg'
import iconEdoorFrontdesk from '../../assets/svg/icon-frontdesk.svg'
import iconEdoorCityLedger from '../../assets/svg/icon-city-ledger.svg'
import iconEdoorGuestDatabase from '../../assets/svg/icon-guest-database.svg'
import iconEdoorHouseKeeping from '../../assets/svg/icon-house-keeping.svg'
import iconEdoorReport from '../../assets/svg/icon-report.svg'
import Search from '@/views/search/Search.vue';
import Property from '@/views/user_property/Property.vue';
import { useDialog } from 'primevue/usedialog';
import ComFooter from '../../components/layout/components/ComFooter.vue';
import OpenShift from "@/views/shift/OpenShift.vue"
import runNightAuditSvgIcon from '@/assets/svg/icon-run-night-audit.svg'

const dialog = useDialog();

const router = useRouter()
const route = useRoute()
const frappe = inject('$frappe')
const gv = inject('$gv')
const auth = frappe.auth()
const user = ref(JSON.parse(localStorage.getItem('edoor_user')))
const show = ref()
const toast = useToast()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting?.backend_port;
import ComIFrameModal from "../../components/ComIFrameModal.vue";
import ComRunNightAudit from "@/views/night_audit/ComRunNightAudit.vue";
const moment = inject("$moment")


const toggle = (event) => {
    show.value.toggle(event);
};

function onUserProfile() {
    alert()
}

function onViewShiftDetail(){
    window.postMessage('view_cashier_shift_detail|' +  gv.cashier_shift?.name , '*')
}

//change property
function changeProperty() {
    dialog.open(Property, {
        props: {
            header: 'Property List',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {
                location.reload();
            }
        }
    });
}
function onRunNightAudit() {
    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

    dialog.open(ComRunNightAudit, {
        props: {
            header: 'Run Night Audit [' +moment(working_day.date_working_day).format('DD-MM-YYYY') + ']',
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            closeOnEscape: false,
        },
        
    });
}


function onRoute(route) {
    router.push({ name: route })
}

function onLink(url) {
    alert("pls remove fix link url")
    location.replace('http://192.168.10.114:1216/app/edoor-frontdesk/' + url)
    //location.replace(serverUrl + '/' + url)
}

function onLogout() {
    auth.logout().then(() => {
        // development mode
        alert("pls remove fix link url")
        location.replace('http://192.168.10.114:1216/app/edoor-frontdesk')
        // location.replace(serverUrl)
    }).catch((error) => toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 }));
}


function onBlankGuestRegistration() {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: JSON.parse(localStorage.getItem("edoor_property")).name,
            report_name: "eDoor%20Blank%20Guest%20Registration%20Card",          
        },
        props: {
            header: "Blank Guest Registration Card",
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

function onSearch() {
    dialog.open(Search, {
        props: {
            header: 'Search',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            position: 'top',
            closeOnEscape: false
        },
    });
}

function onOpenCashierShift() {
    const dialogRef = dialog.open(OpenShift, {
        props: {
            header: 'Open Shift',
            style: {
                width: '50vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: 'top'
        },

    });
}
function onCloseCashierShift() {
    window.postMessage('close_shift', '*')
}

</script>
