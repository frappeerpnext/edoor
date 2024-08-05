<template lang="">
    <div>
        <ComHeader :isSetting="showSetting" :isRefresh="showRefreshButton" @onRefresh="onRefresh"  @onSetting="onSetting">
            <template #start>
                <div class="flex">
                    <div class="flex align-items-center  w-full">
                        <i v-if="!isMobile" @click="onShowSummary" class="pi pi-bars text-3xl cursor-pointer me-3"></i>
                        <div class="text-xl md:text-2xl white-space-nowrap">
                            <slot name="title">
                                 {{title}}
                            </slot>

                        </div> 
                        
                        
                    </div>
                </div>
            </template>
<template #end>

                <div class="flex gap-2 w-full justify-content-between md:justify-content-end">
                
                    <Button v-if="showUpcomingNote" :badge="totalNotes" badgeClass="bg-white text-600 badge-rs" class="w-full md:w-auto bg-yellow-500 border-none" @click="showNote=!showNote">
                       
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
        <ComWalkInReservation v-if="showWalkInReservation" />            
        <NewFITReservationButton v-if="showFITReservationButton" />
        <NewGITReservationButton v-if="showGITReservationButton" />
                  
</template>
</div>
</template>
</ComHeader>
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
                        <ComPanel v-if="showSpecialColor" title="Reservation Special Color" class="pb-3 mt-3">
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

                <slot></slot>
            </div>
        </div>
    </div>
</div>
</div>
<OverlayPanel ref="showAdvanceSearch" style="max-width:70rem">
    <ComRoomChartFilterSelect headerClass="grid" bodyClass="col-12 md:col-4"></ComRoomChartFilterSelect>
</OverlayPanel>


</template>
<script setup>
import { useConfirm, h, ref, reactive, inject, onUnmounted, useToast, useDialog, onMounted, watch, getApi, getCount, provide, computed } from '@/plugin'



import NewReservation from '@/views/reservation/NewReservation.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ComConfirmChangeStay from "@/views/frontdesk/components/ComConfirmChangeStay.vue"
import NewFITReservationButton from "@/views/reservation/components/NewFITReservationButton.vue"
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import ReservationStatusLabel from '@/views/frontdesk/components/ReservationStatusLabel.vue';
import ComReservationColorCodeDetail from '@/views/frontdesk/components/ComReservationColorCodeDetail.vue';
import ComRoomChartFilter from '@/views/frontdesk/components/ComRoomChartFilter.vue'
import ComHousekeepingStatus from '@/views/dashboard/components/ComHousekeepingStatus.vue';
import ComTodaySummary from '@/views/frontdesk/components/ComTodaySummary.vue'
import ComRoomChartFilterSelect from '@/views/frontdesk/components/ComRoomChartFilterSelect.vue'
import ComNoteGlobal from '@/views/note/ComNoteGlobal.vue'
import ComWalkInReservation from '@/views/reservation/components/ComWalkInReservation.vue';
import ComNewReservationMobileButton from "@/views/dashboard/components/ComNewReservationMobileButton.vue"
import FullCalendar from '@fullcalendar/vue3'
import ComDialogNote from '@/components/form/ComDialogNote.vue';
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const props = defineProps({
    title:{
        type:String,
        default:"Page Title"
    },
    showUpcomingNote:{
        type:Boolean,
        default:true
    },
    showWalkInReservation:{
        type:Boolean,
        default:true
    },
    showFITReservationButton:{
        type:Boolean,
        default:true
    },
    showGITReservationButton:{
        type:Boolean,
        default:true
    },
    showSpecialColor:{
        type:Boolean,
        default:true
    },
    showRefreshButton:{
        type:Boolean,
        default:false
    },
    showSetting:{
        type:Boolean,
        default:false
    },


    


})
const emit = defineEmits(["onRefresh","onSetting"])

const confirm = useConfirm()


const moment = inject('$moment')



const gv = inject("$gv")
const toast = useToast();
const dialog = useDialog();
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const edoorShowFrontdeskSummary = localStorage.getItem("edoor_show_frontdesk_summary")

const showNote = ref(false)
const loading = ref(false)
const totalNotes = ref(0)
 
const isMobile = ref(window.isMobile)
const showSummary = ref(true)

let advanceFilter = ref({
    room_type: "",
    room_number: "",
    room_type_group: "",
    building: "",
    floor: ""
})
if (isMobile) {
    showSummary.value = false
}

function onRefresh (){
    emit("onRefresh")
}
function onSetting (){
    emit("onSetting")
}


provide('get_count_note', {
    getTotalNote
})

if (edoorShowFrontdeskSummary) {
    showSummary.value = edoorShowFrontdeskSummary == "1";
}

 


function onShowSummary() {
    showSummary.value = !showSummary.value
    localStorage.setItem("edoor_show_frontdesk_summary", showSummary.value ? "1" : "0")

}




function getTotalNote() {
    getCount('Comment', [["custom_note_date", ">=", working_day.date_working_day], ["custom_is_note", "=", 1], ["comment_type", "=", "Comment"], ["custom_is_audit_trail", "=", 1], ['custom_property', '=', property.name]]).then((docs) => {
        totalNotes.value = docs
    })
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
        if (e.data.action == "Frontdesk") {
            setTimeout(() => {
                
            }, 1000 * 5)

        }
    };
}


onMounted(() => {
    if (window.isMobile) {
        let elem = document.querySelectorAll(".p-dialog");
        if (elem) {
            elem = elem[elem.length - 1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    window.addEventListener('message', actionRefreshData, false);


    getTotalNote()
  


})

 


</script>
