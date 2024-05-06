<template lang="">
    <div>
        <ComHeader>
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center justify-content-between w-full">
                        <div @click="onRefresh()" class="text-xl md:text-2xl white-space-nowrap">{{$t('Floor Plan View')}}</div> 
                        <div class="ml-8 header-title text-xl md:text-2xl white-space-nowrap" >Date here</div>
                        
                    </div>
                </div>
            </template>
<template #end>

                <div class="flex gap-2 w-full justify-content-between md:justify-content-end">
                   
                    <Button :badge="totalNotes" badgeClass="bg-white text-600 badge-rs" class="w-full md:w-auto bg-yellow-500 border-none" @click="showNote=!showNote">
                       
                        <ComIcon icon="iconNoteWhite" class="me-2" height="18px" />
                        <span>{{$t('Upcoming Note')}}</span>
                        <Badge
                      style="font-weight: 600 !important;" class="badge-rs bg-white text-500" :value="totalNotes"
                      severity="warning">
                     
                    </Badge>
                    
                    </Button>
<template v-if="isMobile">
    <ComNewReservationMobileButton :is_walk_in="true" />
</template>
<template v-else>
                    <ComWalkInReservation/>
                    <NewFITReservationButton/>
                    <NewGITReservationButton/>
                  
</template>
</div>
</template>
</ComHeader>
<div class="flex justify-between mb-3 filter-calen-fro sticky_search_bar" id="front_desk_search_sticky">

    <div class="flex gap-2">
        <ComSelect v-if="buildingList.length > 0 && !gv.loading" v-model="selectFilters.building" @onSelected="onBuildingSelected" :clear="false"
            :placeholder="$t('Building')" :options="buildingList || []">
        </ComSelect>
        
        <ComSelect v-if="floorList.length > 0 && !gv.loading" v-model="selectFilters.floor" @onSelected="onFloorSelected" :clear="false"
            :placeholder="$t('Floor')" :options="floorList">
        </ComSelect>
    </div>

    <div>
      fillter here 
    </div>
</div>
<div class="pb-5" style="max-width: 100%;">
    <div id="fron__desk-fixed-top">
        <div :class=" ( !isMobile && showSummary) ? 'flex gap-2' : ''">
            <div v-if="(!isMobile && showSummary)" class="relative" style="width:280px">
                <div>
                    <div class="w-full">
                        <ComPanel title="Today Guest" class="mb-3 pb-3">
                            <div>
                                <ComTodaySummary :date="working_day.date_working_day" />
                            </div>
                        </ComPanel>
                        <ComPanel title="Room Status" class="pb-3 mb-3 front-house__kep">
                            <ComHousekeepingStatus />
                        </ComPanel>

                        <ComPanel title="Reservation Status" class="pb-3">
                            <ReservationStatusLabel />
                        </ComPanel>
                        <ComPanel title="Reservation Special Color" class="pb-3 mt-3">
                            <ComReservationColorCodeDetail />
                        </ComPanel>
                    </div>
                </div>
                <div class="mt-2" style="height: 22px;"></div>
            </div>
            <div class="relative" aria-haspopup="true" aria-controls="overlay_menu"
                :class="showSummary ? 'chart-show-summary':''">

                <Sidebar v-model:visible="showNote" class="top-20 -mt-1 lg:w-5 w-full xl:w-3"
                    style="padding-bottom: 82px;" position="right">
                    <template #header>
                                <div class="flex justify-between items-center me-2">
                                    <div class="absolute left-5 line-height-1">
                                        <div class="text-sm">{{$t('Upcoming')}}</div>    
                                        <div class="text-xl">{{$t('Notes')}}</div> 
                                    </div>
                                </div>
                            </template>
                    <hr class="left-0 fixed w-full">
                    <ComNoteGlobal v-if="showNote" />
                </Sidebar>
                <div id="floor-plan-wrapper">
                    <template v-for="r in roomList" v-if="roomList.length > 0" >
                        <ComRenderRoom :room="r" :wrapper-width="wrapperWidth"/>
                    </template>
               
                
               </div>
            </div>
        </div>
    </div>
</div>
</div>
 


</template>
<script setup>
import {ref,inject,useToast} from "@/plugin"
import { i18n } from '@/i18n';
import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import ComReservationColorCodeDetail from '@/views/frontdesk/components/ComReservationColorCodeDetail.vue';
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from '@/views/frontdesk/components/ComTodaySummary.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'
import ComRenderRoom from '@/views/floor_plan_view/components/ComRenderRoom.vue'

import ComWalkInReservation from '@/views/reservation/components/ComWalkInReservation.vue';
import ComNewReservationMobileButton from "@/views/dashboard/components/ComNewReservationMobileButton.vue"
import ComDialogNote from '@/components/form/ComDialogNote.vue';
import { onMounted } from "vue";
const { t: $t } = i18n.global;
const isMobile = ref(window.isMobile)
const frappe = inject('$frappe')
const gv = inject('$gv')
const call = frappe.call();
const db = frappe.db();
const showSummary = ref(true)
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const wrapperWidth = ref(0)

const buildingList = ref([])
const floorList = ref([])
const roomList = ref([])

const selectFilters =ref({})
const toast = useToast();

onMounted(()=>{
    const wrapperWidth = ref(document.getElementById("floor-plan-wrapper").clientWidth);
})

gv.loading=true;
db.getDocList("Building",{
    filters: [['property', '=', property.name]],
}).then((res)=>{
    buildingList.value = res.map(function(building) {
        return building.name;
    });
})
db.getDocList("Floor",{
    filters: [['property', '=', property.name]],
}).then((res)=>{
    floorList.value = res.map(function(floor) {
        return floor.name;
    }); 
    gv.loading=false;
})

function onBuildingSelected(selected){
    gv.loading=true;
    db.getDocList("Floor",{
        filters: [['property', '=', property.name],['building', '=', selectFilters.value.building]],
    }).then((res)=>{
        floorList.value = res.map(function(floor) {
            return floor.name;
        }); 
        
        gv.loading=false;
    }).catch(err=>gv.loading=false)
}
function onFloorSelected(selected){
    db.getDocList("Room",{
        filters:[['property', '=', property.name],['building', '=', selectFilters.value.building],['floor', '=', selected]],
        fields:["name","room_type","room_status","status_color","room_type_color","housekeeping_status"]
    }).then((res)=>{
        roomList.value = res
    }).catch((error)=>{
        toast.add({ severity: 'error', summary: 'Error', detail: error, life: 3000 })
    })
}




</script>
<style>
    .floor-plan-wrapper{
        height: 100%;
    }
</style>