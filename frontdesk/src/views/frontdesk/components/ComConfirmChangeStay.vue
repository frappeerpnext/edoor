<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="mb-3 flex">
        <ComTagReservation title="RS#:" :value="doc?.reservation" class="bg-card-info p-1px "></ComTagReservation>
        <ComTagReservation title="RES STAY#:" :value="doc?.name" class="bg-card-info p-1px "></ComTagReservation>
        <span class="px-2 rounded-lg me-2 text-white p-1px"
                                :style="{ background: doc?.status_color }">{{
                                    doc?.reservation_status }}
                                </span>
        </div>
        <table>
            <tr>
                <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">Reservation Stay Detail</th>
            </tr>
            <ComStayInfoNoBox  label="Guest name" :value="doc?.guest_name" /> 
            <ComStayInfoNoBox  label="Business Source" :value="doc?.business_source" /> 
            <ComStayInfoNoBox  label="Reservation Type" :value="doc?.reservation_type" /> 
            <ComStayInfoNoBox v-if="doc?.reservation_type == 'GIT'" label="Group">
                <div class="flex font-semibold text-right -ml-3">
                        <sapn v-if="doc?.group_code" v-tooltip.top="'Group Code'">{{ doc?.group_code }}</sapn><span v-if="doc?.group_code && doc?.group_name">/</span> <span v-if="doc?.group_name" v-tooltip.top="'group_name'">{{ doc?.group_name }}</span>
                <div :class="!(doc?.group_code && doc?.group_name) ? '' : 'ms-3'" v-tooltip.top="'Group Color'" class="rounded-lg w-4rem  border-1" v-if="doc?.group_color" :style="{background:doc?.group_color}">&nbsp;</div>
            </div>
                
            </ComStayInfoNoBox> 
            <ComStayInfoNoBox  label="Rooms">
                <div class="inline -ml-3 font-semibold rounded-xl px-2 me-1 bg-gray-edoor inline">
                <sapn v-tooltip.top="doc?.room_types" >{{ doc?.room_type_alias }}</sapn> / <span>{{ doc?.rooms }}</span>
                
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Pax">
                <div class="inline -ml-3 font-semibold">
                <sapn v-tooltip.top="'Adult'" >{{ doc?.adult }}</sapn> / <span v-tooltip.top="'Child'" >{{ doc?.child }}</span>
                
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Arrival">
                <div class="inline -ml-3 font-semibold">
                <sapn>{{gv.dateFormat(doc?.arrival_date) }}</sapn> <span>{{gv.timeFormat(doc?.arrival_time) }}</span>
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Departure">
                <div class="inline -ml-3 font-semibold">
                <sapn>{{ gv.dateFormat(doc?.departure_date) }}</sapn> <span>{{ gv.timeFormat(doc?.departure_time) }}</span>
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Nights" :value="doc?.room_nights" /> 
            
        </table>
        <div class="line-height-1 text-right mt-3 flex p-0 flex-col justify-center gap-2 w-full text-sm white-space-nowrap overflow-hidden text-overflow-ellipsis">
            <div>
                <span class="italic">Created by: </span>
                <span class="text-500 font-italic"> {{ doc?.owner }} - {{ gv.datetimeFormat(doc?.creation) }} </span>
                <span class="italic ms-2"> Last Modified: </span>
                <span  class="text-500 font-italic"> {{ doc?.modified_by }} - {{ gv.datetimeFormat(doc?.modified) }} </span>
            </div>
        </div> 
        <hr class="my-3" />
        <table>
            <tr>
                <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">New Reservation Stay Detail</th>
            </tr>
            <ComStayInfoNoBox  label="Rooms">
                <div class="inline -ml-3 font-semibold">
                <sapn v-tooltip.top="data?.extendedProps?.room_types" >{{ data?.extendedProps?.room_type_alias }}</sapn> - <span>{{ data?.extendedProps?.rooms }}</span>
                
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox  label="Arrival">
                <div class="inline -ml-3 font-semibold">
                <sapn>{{gv.datetimeFormat(data?.start) }}</sapn>
                <span v-if="gv.dateFormat(doc?.arrival_date) != gv.dateFormat(data?.start) " class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-green-500">
                New
                </span>
                </div>
            </ComStayInfoNoBox>
            <ComStayInfoNoBox titleClass="" label="Departure">
                <div class="inline -ml-3 font-semibold">
                <sapn>{{ gv.datetimeFormat(data?.end) }}</sapn>
                <span v-if="gv.dateFormat(doc?.departure_date) != gv.dateFormat(data?.end) " class="ms-2 px-2 rounded-lg me-2 text-white p-1px bg-green-500"
                                >New
                                </span>
                </div>
            </ComStayInfoNoBox>           
        </table>
        <div class="flex justify-end gap-3 mt-3">
        <div class="flex align-items-center">
            <RadioButton v-model="generate_rate_type" inputId="regenerate_using_last_rate" name="regenerate" value="use_last_rate" />
            <label for="regenerate_using_last_rate" class="ml-2 cursor-pointer">Regenerate using first and Last stay date</label>
        </div>
        <div class="flex align-items-center">
            <RadioButton v-model="generate_rate_type" inputId="regenerate_rate_use_rate_plan" name="regenerate" value="use_rate_plan" />
            <label for="regenerate_rate_use_rate_plan" class="ml-2 cursor-pointer">Generate New Rate using Rate Plan</label>
        </div>
        </div>
<hr class="my-3">
        <label>Note</label><br />
                <Textarea v-model="note" rows="3" placeholder="Note" cols="30"
                    class="w-full border-round-xl" />
       
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, getDoc,postApi } from "@/plugin"
const dialogRef = inject("dialogRef");
const data = ref({})
const doc = ref()
const isSaving =ref(false)
const generate_rate_type = ref("use_last_rate")
const note = ref("")
const moment = inject("$moment")
const socket = inject("$socket")
const gv = inject('$gv');
import ComTagReservation from '@/views/reservation/components/ComTagReservation.vue';
function onSave(){
    isSaving.value = true
    postApi("reservation.change_stay", 
        {
            data:{
                room_id: data.value.extendedProps.room_id,
                property: doc.value.property,
                room_type_id:data.value.extendedProps.room_type_id,
                start_date:moment(data.value.start).format("YYYY-MM-DD"),
                end_date:moment(data.value.end).format("YYYY-MM-DD"),
                parent:data.value.extendedProps.reservation_stay,
                generate_rate_type: generate_rate_type.value,
                note:note.value,
                name:data.value.id,
                ignore_check_room_occupy:1
            }
 }
    ).then((result)=>{
        isSaving.value = false
        dialogRef.value.close(result);
       
        socket.emit("RefresheDoorDashboard", doc.value.property);
        


    }).catch((err)=>{
        isSaving.value = false
    })
}
onMounted(() => {

    data.value = dialogRef.value.data;
    getDoc("Reservation Stay", data.value._def.extendedProps.reservation_stay).then((r) => {
        doc.value = r
    });




});
</script>