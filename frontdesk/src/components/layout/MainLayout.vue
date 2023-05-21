<template>
    <div class="wrap-page">
        <ProgressBar class="absolute top-0 right-0 left-0 z-50" v-if="gv.loading" mode="indeterminate" style="height: 6px">
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
                        <ComHeaderBarItemButton title="Guest Database" @onClick="onLink('guest-database')">
                            <template #icon>
                                <img :src="iconEdoorGuestDatabase">
                            </template>
                            <template #defualt>
                                <p title="Guest Database">Guest Database</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="House Keeping" icon="pi-users" @onClick="onRoute('Housekeeping')">
                            <template #icon>
                                <img :src="iconEdoorHouseKeeping">
                            </template>
                            <template #defualt>
                                <p title="House Keeping">House Keeping</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Guest Ledger" @onClick="onLink('guest-ledger')">
                            <template #icon>
                                <img :src="iconGuestLedger">
                            </template>
                            <template #defualt>
                                <p title="Guest Ledger">Guest Ledger</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="City Ledger" @onClick="onLink('city-ledger')">
                            <template #icon>
                                <img :src="iconEdoorCityLedger">
                            </template>
                            <template #defualt>
                                <p title="City Ledger">City Ledger</p>
                            </template>
                        </ComHeaderBarItemButton>
                        <ComHeaderBarItemButton title="Reports" @onClick="onLink('reports')">
                            <template #icon>
                                <img :src="iconEdoorReport">
                            </template>
                            <template #defualt>
                                <p title="Reports">Reports</p>
                            </template>
                        </ComHeaderBarItemButton>

                        <ComHeaderBarItemButtonMore />
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
                                    aria-label="Setting" class="p-link text-white" @click="onSearch" aria-haspopup="true"
                                    aria-controls="overlay_menu" />
                            </div>
                            <div>
                                <Button icon="pi pi-cog btn-setting-top" text rounded severity="secondary"
                                    aria-label="Setting" class="p-link text-white" @click="toggle" aria-haspopup="true"
                                    aria-controls="overlay_menu" />
                            </div>
                            <Menu ref="show" id="overlay_menu" :popup="true" style="min-width: 180px;">
                                <template #end>
                                    <button @click="changeProperty"
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround"
                                        v-if="user.property.length > 1">
                                        <i class="pi pi-user" />
                                        <span class="ml-2">Change property</span>
                                    </button>
                                    <button @click="onRefresh"
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-refresh" />
                                        <span class="ml-2">Refresh</span>
                                    </button>
                                    <button @click="onLogout"
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        <i class="pi pi-sign-out !text-red-500" />
                                        <span class="ml-2  !text-red-500">Log Out</span>
                                    </button>
                                </template>
                            </Menu>
                        </div>
                        <div class="guest-user__pro flex items-center h-full justify-center white-space-nowrap overflow-hidden text-overflow-ellipsis"
                            style="width:180px">
                            <ComAvatar :image="user.photo">
                                <div class="font-lg font-bold text-white">{{ user.name }}</div>
                                <div class="text-ms text-white">{{ user.role }}</div>
                            </ComAvatar>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div>
            <div class="wrap-page-content px-2">
                <router-view />
            </div>
            <ComFooter />
        </div>

    </div>
</template>

<script setup>
import { ref, inject, useToast, useRouter } from '@/plugin'
import ComAvatar from '../form/ComAvatar.vue';
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


const dialog = useDialog();


const router = useRouter()
const frappe = inject('$frappe')
const gv = inject('$gv')
const auth = frappe.auth()
const user = ref(JSON.parse(localStorage.getItem('edoor_user')))
const show = ref()
const toast = useToast()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting?.backend_port;
const toggle = (event) => {
    show.value.toggle(event);
};

function onUserProfile() {
    alert()
}
function onRefresh() {

    window.location.reload();
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

function onRoute(route) {
    router.push({ name: route })
}

function onLink(url) {
    location.replace('http://192.168.10.114:1216/app/edoor-frontdesk/' + url)
    //location.replace(serverUrl + '/' + url)
}

function onLogout() {
    auth.logout().then(() => {
        // development mode
        location.replace('http://192.168.10.114:1216/app/edoor-frontdesk')
        // location.replace(serverUrl)
    }).catch((error) => toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 }));
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
            modal: true
        },
    });
}


console.log(document.getElementsByClassName('header-bar').offsetHeight);
</script>
