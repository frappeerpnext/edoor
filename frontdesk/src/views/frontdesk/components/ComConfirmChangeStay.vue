<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="mb-3 flex">
                <span @click="onViewReservationDetail(doc?.reservation)">
            <ComTagReservation title="RS#:" :value="doc?.reservation" class="link_line_action w-auto"></ComTagReservation>
                </span>
            <span class="con" @click="onViewReservationStayDetail(doc?.name)">
                <ComTagReservation title="RES STAY#:" :value="doc?.name" class="link_line_action w-auto"></ComTagReservation>
            </span>
            <div v-tippy ="'Split Room'" class="flex justify-center items-center px-2 rounded-lg me-2 bg-card-info p-1px" v-if="doc?.stays?.length >= 2" >
                <ComIcon  icon="iconSplit" style="height:15px;" ></ComIcon>   
            </div>
            <span class="px-2 rounded-lg me-2 text-white p-1px" :style="{ background: doc?.status_color }">{{doc?.reservation_status }}</span>
        </div>
        <div class="grid">
            <div class="col-12">
                <table>
                    <tr>
                        <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">Reservation Stay Detail</th>
                    </tr>
                    <ComStayInfoNoBox  label="Guest name"  >
                        <div class="inline -ml-3">
                            <span  @click="onViewGuestDetail(doc?.guest)" class="link_line_action">{{  doc?.guest_name }}</span>
                        </div>
                    </ComStayInfoNoBox>   
                    <ComStayInfoNoBox  label="Business Source" :value="doc?.business_source" /> 
                    <ComStayInfoNoBox  label="Reservation Type" :value="doc?.reservation_type">
                        <span v-tippy ="'Res Color'" v-if="doc?.reservation_color" :style="{background:doc?.reservation_color}" class="px-3 rounded-lg font-semibold" >&nbsp;</span>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox v-if="doc?.reservation_type == 'GIT'" label="Group">
                        <div class="flex font-semibold text-right -ml-3">
                            <sapn v-if="doc?.group_code" v-tippy ="'Group Code'">{{ doc?.group_code }}</sapn><span v-if="doc?.group_code && doc?.group_name">/</span> <span v-if="doc?.group_name" v-tippy ="'group_name'">{{ doc?.group_name }}</span>
                        </div>
                    </ComStayInfoNoBox> 
                    <ComStayInfoNoBox  label="Pax">
                        <div class="inline -ml-3 font-semibold">
                            <sapn v-tippy ="'Adult'" >{{ doc?.adult }}</sapn> / <span v-tippy ="'Child'" >{{ doc?.child }}</span>
                        </div>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox v-if="doc?.stays.length>1"  label="Rooms">
                        <div v-if="doc && doc?.stays">
                            <div class="-ml-3"> 
                                <span v-for="(i, index) in doc?.stays" :key="index">
                                    <div class="inline" v-if="index < 3">
                                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                        <span v-tippy ="i.room_type">{{i.room_type_alias}}</span>
                                        <span v-if="i.room_number">/{{ i.room_number }}  
                                        </span>
                                        </div>
                                    </div>
                                </span>
                                <div v-if="doc?.stays.length>3" v-tippy ="{ value: `<div class='tooltip-room-stay'> ${doc?.stays.stays.slice(3).map(obj => obj.room_types + '/' + (obj.room_number || '')  ).join('\n')}</div>` 
                                    ,escape: true, class: 'max-w-30rem' }" class="rounded-xl px-2 bg-purple-cs w-auto inline">
                                    {{ doc?.stays.length - 3 }} Mores
                                </div> 
                            </div>
                        </div>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox v-if="doc?.stays.length>1" label="Arrival" :value="gv.dateFormat(doc?.arrival_date) " />
                    <ComStayInfoNoBox v-if="doc?.stays.length>1" label="Departure" :value="gv.dateFormat(doc?.departure_date)" />
                    <ComStayInfoNoBox v-if="doc?.stays.length>1" label="Nights" :value="doc?.room_nights" />
                </table>
            </div>
            <div class="col-6">
                <table>
                    <tr>
                        <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">Old Stay Detail</th>
                    </tr>
                    <ComStayInfoNoBox  label="Rooms">
                            <div v-if="doc && doc?.stays">
                                    <div class="-ml-3"> 
                                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                                <span v-tippy ="data?.extendedProps?.room_type">{{data?.extendedProps?.room_type_alias}}</span>
                                                <span v-if="data?.extendedProps?.room_number"> / {{ data?.extendedProps?.room_number }}  
                                                </span>
                                        </div>
                                    </div>
                                </div>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox  label="Arrival">
                        <div class="inline -ml-3 font-semibold">
                        <sapn>{{gv.dateFormat(oldEvent?.start) }}</sapn>
                        </div>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox  label="Departure">
                        <div class="inline -ml-3 font-semibold">
                            <sapn>{{ gv.dateFormat(oldEvent?.end) }}</sapn>
                        </div>
                    </ComStayInfoNoBox>
                    <ComStayInfoNoBox  label="Nights" :value="moment(oldEvent?.end).diff(oldEvent?.start, 'days')" /> 
                </table>
            </div>
        <div class="col-6">
        <table>
            <tr>
                <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">New Stay Detail</th>
            </tr>
            <ComStayInfoNoBox  label="Rooms">
                <div class="inline -ml-3 ">
                    <template  v-if="new_data" >
                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline" >
                        <sapn   v-tippy ="new_data?.extendedProps?.room_type" >{{ new_data?.extendedProps?.room_type_alias }}</sapn> / <span>{{ new_data?.title }}</span>
                        </div>
                        <span class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-yellow-400 ">
                            <span style="font-weight: 700 !important;">Move</span>
                        </span>    
                    </template>
                    <template v-else>
                        <div v-if="doc && doc?.stays">
                            <div class=""> 
                                <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                    <span v-tippy ="data?.extendedProps?.room_type">{{data?.extendedProps?.room_type_alias}}</span>
                                    <span v-if="data?.extendedProps?.room_number"> / {{ data?.extendedProps?.room_number }}  </span>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Arrival">
                <div class="inline -ml-3 font-semibold">
                <sapn>{{gv.dateFormat(data?.start) }}</sapn>
                <span v-if="gv.dateFormat(oldEvent?.start) != gv.dateFormat(data?.start) " class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-green-500">New</span>
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox titleClass="" label="Departure">
                <div class="inline -ml-3 font-semibold">
                    <sapn>{{ gv.dateFormat(data?.end) }}</sapn>
                    <span v-if="gv.dateFormat(doc?.departure_date) != gv.dateFormat(data?.end) " class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-green-500">New</span>
                </div>
            </ComStayInfoNoBox>   
            <ComStayInfoNoBox titleClass="" label="Nights">
                <div class="inline -ml-3 font-semibold">
                <sapn> {{ moment(data?.end).diff(data?.start, 'days') }}  </sapn>
                <span v-if="moment(data?.end).diff(data?.start, 'days') != moment(oldEvent?.end).diff(oldEvent?.start, 'days') " class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-green-500">New</span>
                </div>
            </ComStayInfoNoBox>   
        </table>  
        </div>
        <div class="col-12">
            <div class="line-height-1 text-right mt-3 flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
                <div>
                    <span class="italic">Created by: </span>
                    <span class="text-500 font-italic"> {{ doc?.owner }} - {{ gv.datetimeFormat(doc?.creation) }} </span>
                    <span class="italic ms-2"> Last Modified: </span>
                    <span  class="text-500 font-italic"> {{ doc?.modified_by }} - {{ gv.datetimeFormat(doc?.modified) }} </span>
                </div>
            </div>
        </div>
    </div> 
        <hr class="my-4" />
        <div class="flex justify-end gap-3 mt-3">
            <div class="flex align-items-center" v-if="show_keep_rate">
                <RadioButton v-model="generate_rate_type" inputId="regenerate_using_keep_old_rate" name="regenerate" value="keep_current_rate" />
                <label for="regenerate_using_keep_old_rate" class="ml-2 cursor-pointer">Keep current room rate</label>
            </div>
            <div v-else class="flex align-items-center">
                <RadioButton v-model="generate_rate_type" inputId="regenerate_using_last_rate" name="regenerate" value="stay_rate" />
                <label for="regenerate_using_last_rate" class="ml-2 cursor-pointer">Generate New Stay Rate from  First/Last Stay Rate</label>
            </div>

            <div class="flex align-items-center">
                <RadioButton v-model="generate_rate_type" inputId="regenerate_rate_use_rate_plan" name="regenerate" value="rate_plan" />
                <label for="regenerate_rate_use_rate_plan" class="ml-2 cursor-pointer">Generate New Stay Rate using Rate Plan</label>
            </div>
        </div>
        <label>Note</label><br />
        <Textarea v-model="note" rows="3" placeholder="Note" cols="30" class="w-full border-round-xl" />
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, getDoc,postApi } from "@/plugin"
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
const dialogRef = inject("dialogRef");
const data = ref({})
const new_data = ref({})
const oldEvent = ref({})
const show_keep_rate = ref(false)
const doc = ref()
const isSaving =ref(false)
const generate_rate_type = ref("stay_rate")
const note = ref("")
const moment = inject("$moment")
const gv = inject('$gv');

function onViewReservationStayDetail(rs) {
    window.postMessage('view_reservation_stay_detail|' + rs, '*')
}

function onViewReservationDetail(rs) {
    window.postMessage('view_reservation_detail|' + rs, '*')
}

function onViewGuestDetail(gs){
    window.postMessage('view_guest_detail|' + gs,'*')
}

function onSave(){
    isSaving.value = true
    postApi("reservation.change_stay", 
        {
            data:{
                room_id: new_data.value?new_data.value.id: data.value.extendedProps.room_id ,
                property: window.property_name,
                room_type_id:new_data.value?new_data.value.parentId:data.value.extendedProps.room_type_id,
                start_date:moment(data.value.start).format("YYYY-MM-DD"),
                end_date:moment(data.value.end).format("YYYY-MM-DD"),
                parent:data.value.extendedProps.reservation_stay,
                generate_rate_type: generate_rate_type.value,
                note:note.value,
                name:data.value.id,
                ignore_check_room_occupy:1,
                is_move: show_keep_rate.value
            }
        }
    ).then((result)=>{
        isSaving.value = false
        //we delay wait data to update complete
        setTimeout(function(){
            window.socket.emit("Frontdesk", window.property_name);
        }, 1000)
        
        dialogRef.value.close(result);
    }).catch((err)=>{
        isSaving.value = false
    })
}
onMounted(() => {
    data.value = dialogRef.value.data.event;
    new_data.value = dialogRef.value.data.new_event;
    show_keep_rate.value = dialogRef.value.data.show_keep_rate;
    oldEvent.value =  dialogRef.value.data?.old_event;
    if(show_keep_rate.value==1){
        generate_rate_type.value = "keep_current_rate"
    }
    getDoc("Reservation Stay", data.value._def.extendedProps.reservation_stay).then((r) => {
        doc.value = r
    });
});
</script>