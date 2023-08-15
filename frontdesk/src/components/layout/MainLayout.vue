<template>
    <div class="wrap-page">

        <ProgressBar class="absolute top-0 right-0 left-0" style="z-index: 9999; height: 6px" v-if="gv.loading"
            mode="indeterminate">
        </ProgressBar>
 
        <div class="header-bar w-full">
            <div class="mx-auto flex items-stretch h-full">
                <div class="header-logo flex-auto h-full"> 
                    <div class="flex h-full wrap-pro-bar top-pro-bar-cus">
                        <template v-for="(m, index) in eDoorMenu.filter(r => r.parent_edoor_menu == 'All Menus')" :key="index">
                            <ComHeaderBarItemButton
                                :data="m"
                                @onClick="onRoute">
                                <template #icon>
                                    <span v-html="m.icon"></span>
                                </template>
                                <template #defualt>
                                    <p>{{ m.menu_text }} <i style="font-size: 12px;" v-if="m.is_group" class="pi pi-angle-down"></i></p>
                                </template>
                            </ComHeaderBarItemButton>
                        </template>  
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
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround"
                                        v-if="user.property.length > 1">
                                        <img :src="iconChangeProperty" style="height: 15px;" />
                                        <span class="ml-2">Change Property</span>
                                    </button>

                                    <button @click="onBlankGuestRegistration"
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround">
                                        <img :src="iconBlankGuestRegisteration" style="height: 15px;" />
                                        <span class="ml-2">Blank Guest Registration</span>
                                    </button>
                                    <button @click="onOpenCashierShift" v-if="!gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround">
                                        <img :src="iconOpenCashierShift" style="height: 15px;" />
                                        <span class="ml-2">Open cashier shift</span>
                                    </button>
                                    <button @click="onViewShiftDetail" v-if="gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround">
                                        <img :src="iconViewShiftDetail" style="height: 15px;" />
                                        <span class="ml-2">View Shift Detail</span>
                                    </button>

                                    <button @click="onCloseCashierShift" v-if="gv.cashier_shift?.name"
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround">
                                        <img :src="iconCloseCashierShift" style="height: 15px;" />
                                        <span class="ml-2">Close Cashier Shift</span>
                                    </button>

                                    <button @click="onRunNightAudit"
                                        class="w-full p-link flex align-items-center p-2 pl-0 text-color hover:surface-200 border-noround">
                                        <img :src="runNightAuditSvgIcon" style="height: 15px;" />
                                        <span class="ml-2">Run Night Audit</span>
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
import { ref, inject, useToast, useRouter, useRoute, computed } from '@/plugin'
import { useScreen, useGrid } from 'vue-screen'
import ComAvatarUserProfile from './components/ComAvatarUserProfile.vue'
// import ComHeaderBarItemButtonMore from './components/ComHeaderBarItemButtonMore.vue';
import ProgressBar from 'primevue/progressbar';
import ComHeaderDateTimeUpdate from './components/ComTimeUpdate.vue';
import Search from '@/views/search/Search.vue';
import Property from '@/views/user_property/Property.vue';
import { useDialog } from 'primevue/usedialog';
import ComFooter from '../../components/layout/components/ComFooter.vue';
import OpenShift from "@/views/shift/OpenShift.vue"
import runNightAuditSvgIcon from '@/assets/svg/icon-run-night-audit.svg'
import iconCloseCashierShift from '@/assets/svg/icon-close-cashier-shift.svg'
import iconOpenCashierShift from '@/assets/svg/icon-open-cashier-shift.svg'
import iconViewShiftDetail from '@/assets/svg/icon-view-cashier-shift.svg'
import iconChangeProperty from '@/assets/svg/icon-change-property.svg'
import iconBlankGuestRegisteration from '@/assets/svg/icon-blank-registration.svg'
import ComHeaderBarItemButton from './components/ComHeaderBarItemButton.vue';

const dialog = useDialog();
const router = useRouter()
const route = useRoute()
const frappe = inject('$frappe')
const gv = inject('$gv')
const screen = useScreen()
const auth = frappe.auth()
const user = ref(JSON.parse(localStorage.getItem('edoor_user')))
const show = ref()
const toast = useToast()
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting?.backend_port;
import ComIFrameModal from "../../components/ComIFrameModal.vue";
import ComRunNightAudit from "@/views/night_audit/ComRunNightAudit.vue";
const moment = inject("$moment")
// const eDoorMenu = ref([])
const eDoorMenu = computed(()=>{ 
    const menu = ref(setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") != ""))
    //menu.value = menu.value.filter(r => r.parent_edoor_menu == 'All Menus')
    if(screen.width <= 1346){
        return menu.value.filter(r => r.hidden_in_sm == false)
    }else{
        return menu.value
    }
})
const currentRouteName = computed(() => route.name.replace(/"/g, ''));

const subMenus = computed(() => {
    const current_menu_id = setting.edoor_menu.find(r => r.menu_name == currentRouteName.value)
    if (current_menu_id) {
        let parent_menu_id = current_menu_id.name
 
        if (current_menu_id.is_group == 0){
            if(current_menu_id.parent_edoor_menu!="All Menus"){
                parent_menu_id =current_menu_id.parent_edoor_menu  
            }
           
        }

        return setting.edoor_menu?.filter((r) => r.parent_edoor_menu == parent_menu_id)
    }


    return []
})

const toggle = (event) => {
    show.value.toggle(event);
};


function onViewShiftDetail() {
    window.postMessage('view_cashier_shift_detail|' + gv.cashier_shift?.name, '*')
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
            modal: true,
            closeOnEscape: false,
            position: 'top'
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
            header: 'Run Night Audit [' + moment(working_day.date_working_day).format('DD-MM-YYYY') + ']',
            style: {
                width: '80vw',
            },
            position: "top",
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
            position: "top",
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
                width: '40vw',
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

// onMounted(() => {
//     eDoorMenu.value = setting?.edoor_menu.filter(r => (r.parent_edoor_menu || "") != "")
 
// })
 
</script>
