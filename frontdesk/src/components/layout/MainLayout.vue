<template>
    <div class="wrap-page relative">
        <div class="header-bar fixed w-full bg-white z-50">
            <div class="mx-auto flex items-center h-full">
                <div class="header-logo flex-auto h-full">
                    <div class="flex h-full">
                        <ComHeaderBarItemButton icon="pi-microsoft" @onClick="onRoute('Dashboard')">Dashboard</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-microsoft" @onClick="onRoute('Frontdesk')">Frontdesk</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onRoute('ReservationList')">Reservation List</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onLink('guest-database')">Guest Database</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onLink('house-keeping')">House Keeping</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onLink('guest-ledger')">Guest Ledger</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onLink('city-ledger')">City Ledger</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-users" @onClick="onLink('report')">Report</ComHeaderBarItemButton>
                        <ComHeaderBarItemButton icon="pi-bars" @onClick="onLink('report')">More</ComHeaderBarItemButton>
                    </div>
                </div>
                <div class="mr-auto flex flex-none justify-end">
                    <div class="px-2">
                        <div>
                            <Button icon="pi pi-cog" text rounded severity="secondary" aria-label="Setting" class="p-link" @click="toggle" aria-haspopup="true" aria-controls="overlay_menu"/>
                        </div>
                        <Menu ref="show" id="overlay_menu" :popup="true" style="min-width: 180px;">
                            <!-- <template #start>
                                <div class="p-2 pl-4">
                                    <div class="font-bold">{{ user.name }}</div>
                                    <div class="text-sm">{{ user.role }}</div>
                                </div>
                            </template> -->
                            <template #end>
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
                    <div class=" pr-3">
                        <ComAvatar :image="user.photo">
                            <div class="font-bold">{{ user.name }}</div>
                            <div class="text-sm">{{ user.role }}</div>
                        </ComAvatar>
                    </div>
                </div>
            </div>
        </div>
        <div class="wrap-page-content">
            <router-view />
        </div>
    </div>
</template>
<script setup>
import { ref, inject,useToast, useRouter } from '@/plugin'
import ComAvatar from '../form/ComAvatar.vue';
import ComHeaderBarItemButton from './components/ComHeaderBarItemButton.vue'
const router = useRouter()
const frappe = inject('$frappe')
const auth = frappe.auth()
const user = ref(JSON.parse(localStorage.getItem('current_user')))
const show = ref() 
const toast = useToast()
const setting = JSON.parse( localStorage.getItem("setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" +  setting?.backend_port;
const toggle = (event) => {
    show.value.toggle(event);
};
function onUserProfile(){
    alert()
}
function onRefresh(){
    // production mode
    // location.replace(serverUrl + '/app/edoor-frontdesk')
    // development mode
    location.replace('http://192.168.10.114:1216/app/edoor-frontdesk')
}

function onRoute(route){
    router.push({name: route})
}

function onLink(url){
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
</script>
<style scoped>
.header-bar {
    box-shadow: 0px 1px 2px rgba(25, 39, 52, 0.05), 0px 0px 4px rgba(25, 39, 52, 0.1);
    height: 60px;
}
.wrap-page-content {
    padding-top: 60px;
}
</style>