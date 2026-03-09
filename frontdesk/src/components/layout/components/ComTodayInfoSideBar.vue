<template>
    
    <div v-if="!isMobile" class="flex flex-col justify-content-between align-items-center h-full">
        <div>
            <div class="flex justify-content-center align-items-center flex-col py-3 px-2 gap-4 -ms-2">
                <div  @click="onNavigate(m.router_name)" class="relative" v-for="(m, index) in sidebarItems" :key="index">
                    <tippy :content="$t(m.title)" placement="right">
                        <Button  :class="['relative p-2 side-bar-today-info', route.name == m.router_name?'menu_active_bar':'']"    severity="info">
                            <ComIcon :icon="m.icon" height="30px"/>
                        </Button>
                        <div class="absolute badge-today-info" v-if="m.badge_field">
                            <Badge  class="flex justify-content-center" :value="data?.[m.badge_field] || 0" severity="info"></Badge>
                        </div>
                    </tippy>
                </div>
            </div>
        </div>
        <div class="mb-5">
            <hr class="border-1 mb-1"/>
            <Button class="bg-transparent border-0 p-1 relative">
                <ComIcon icon="iconSetting" height="30px"/>
            </Button>
        </div>
    </div>
</template>
<script setup>
import { onMounted,useRouter,useRoute,getData,ref,onUnmounted } from '@/plugin';
import ComIcon from '../../ComIcon.vue';
const isMobile = ref(window.isMobile)  
const route = useRoute()
const router = useRouter()
const data = ref() 
 
const sidebarItems = [
    {
        title:"All Reservation",
        icon:"iconAllReservation",
        router_name:"AllReservation",
        badge_field:"total_stay"
    },
    {
        title:"Arrival Guest",
        icon:"iconArrivalGuest",
        router_name:"ArrivalGuest",
        badge_field:"total_arrival"
    },
    {
        title:"Stay Over Guest",
        icon:"iconStayOverGuest",
        router_name:"StayOverGuest",
        badge_field:"total_stay_over"
    },
    {
        title:"Departure Guest",
        icon:"iconDepartureGuest",
        router_name:"DepartureGuest",
        badge_field:"total_departure"
    },
    {
        title:"Unassign Room",
        icon:"iconUnassignRoom",
        router_name:"UnAssignRoomList",
        badge_field:"total_unassign_room"

        
    },
]

function onNavigate(route_name){
    router.push({ name: route_name }) 
}
async function loadData(){
    const res = await getData("frontdesk.get_sidebar_kpi",{
        property:window.property_name,
        date:window.current_working_date
    })

    data.value = res.data
}


const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="Dashboard"){
            await loadData()
        }
    };
}
onMounted(async ()=>{
    await loadData()
    window.addEventListener('message', actionRefreshData, false); 
})
 

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
    
})


</script>
<style scoped>
.menu_active_bar { 
    background: var(--bg-btn-color) !important;
}
.side-bar-today-info {
    background:rgb(169 170 255);
    border: 0;
}
</style>