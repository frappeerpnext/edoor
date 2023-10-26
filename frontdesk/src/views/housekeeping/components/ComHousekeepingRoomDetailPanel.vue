<template>
    <div class="pb-20">
       <div class="">
            <div class="line-height-1 absolute top-4">
                <div class="text-2xl">Detail OF</div>
                <div class="text-sm">{{hk.selectedRow?.room_type}} # {{hk.selectedRow?.room_number}}</div>
            </div>
            <hr class="mb-3">
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center">Room</div>
            <table>
                <ComStayInfoNoBox  label="Room No" :value="hk.selectedRow?.name" /> 
                <ComStayInfoNoBox  label="Room Type Id" :value="hk.selectedRow?.room_type_id" /> 
                <ComStayInfoNoBox  label="Room Number" :value="hk.selectedRow?.room_number" /> 
                <ComStayInfoNoBox  label="Status" :value="hk.selectedRow?.housekeeping_status" /> 
                <ComStayInfoNoBox  label="Housekeeper" :value="hk.selectedRow?.housekeeper" /> 
            </table>
        </div>
            <div class="grid mt-2">
                <div class="col-6"> 
                    <SplitButton :disabled="hk.selectedRow.housekeeping_status == 'Room Block'" class="w-full" :buttonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" :label="hk.selectedRow?.housekeeping_status"  :model="items" :color="hk.selectedRow?.status_color"  
                        :menuButtonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" :class="{ 'active-button': true }">
                    </SplitButton>
                </div> 
                <div class="col-6">
                    <Button class="w-full" label="Assign Housekeeper" severity="warning" @click="onAssignHousekeeper($event)" ></Button>
                    <OverlayPanel ref="opHousekeeper">
                        <ComOverlayPanelContent :loading="loading"  @onCancel="onAssignHousekeeper($event,{})" @onSave="onSaveAssignHousekeeper">
                            <ComSelect class="w-full" isFilter v-model="selected.housekeeper" placeholder="Assign Housekeeper" doctype="Housekeeper"  />
                        </ComOverlayPanelContent>
                    </OverlayPanel>        
                </div>  
            </div>
        <div v-if="hk && hk.reservationStay && Object.keys(hk.reservationStay ).length > 0" >
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center">Reservation</div>
            <table>
                <ComStayInfoNoBox label="Res No">
                    <Button @click="onViewReservationDetail(hk?.reservationStay?.reservation)" class="-ml-3 link_line_action1" text>{{ hk?.reservationStay?.reservation }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Res Stay No">
                    <Button @click="onViewReservationStayDetail(hk?.reservationStay?.name)" class="-ml-3 link_line_action1" text>{{ hk?.reservationStay?.name }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox  label="Type" :value="hk?.reservationStay?.reservation_type" />
                <ComStayInfoNoBox v-if="hk?.reservationStay?.reservation_type != 'FIT'"  label="Group">
                    <div class="w-full overflow-hidden white-space-nowrap -ml-3 text-overflow-ellipsis">
                        <div v-tippy="hk?.reservationStay?.group_code" class="inline">
                           {{ hk?.reservationStay?.group_code }} 
                        </div>
                         / 
                        <div v-tippy="hk?.reservationStay?.group_name" class="inline">
                           {{ hk?.reservationStay?.group_name }}
                        </div>
                    </div>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox  label="Status">
                    <span class="-ms-3 font-semibold" :style="{color:hk.reservationStay?.status_color}">{{ hk?.reservationStay?.reservation_status }}</span>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox label="Guest Name">
                    <Button @click="onViewCustomerDetail(hk?.reservationStay?.guest)" class="-ml-3 link_line_action1" text>{{ hk?.reservationStay?.guest }} - {{ hk?.reservationStay?.guest_name }}</Button>
                </ComStayInfoNoBox>
                <ComStayInfoNoBox  label="Nationality" :value="hk?.reservationStay?.nationality" /> 
                <!-- <ComStayInfoNoBox  label="Phone Number" :value="hk?.reservationStay?.guest_phone_number" />  
                <ComStayInfoNoBox  label="Email" :value="hk?.reservationStay?.guest_email" />   --> 
                <ComStayInfoNoBox  label="PAX" :value="hk?.reservationStay?.adult + ' / ' + hk?.reservationStay?.child" /> 
                <ComStayInfoNoBox  label="Arrival">
                    <span class="-ms-3 font-semibold">
                        {{ gv.dateFormat(hk?.reservationStay?.arrival_date) }} - {{ gv.timeFormat(hk?.reservationStay?.arrival_time)  }}
                    </span>
                </ComStayInfoNoBox> 
                <ComStayInfoNoBox  label="Departure">
                    <span class="-ms-3 font-semibold">
                        {{ gv.dateFormat(hk?.reservationStay?.departure_date) }} - {{ gv.timeFormat(hk?.reservationStay?.departure_time)  }}
                    </span>
                </ComStayInfoNoBox> 
                <ComStayInfoNoBox  label="Night" :value="hk?.reservationStay?.room_nights" /> 
            </table>
            <template  >
            <div class="py-2 mt-3 border-1  bg-slate-200 font-medium text-center">Housekeeping Charge Summary</div> 
            <table class="w-full" v-if="hk.selectedRow.summary">
                <ComStayInfoNoBox  label="TOTAL DEBIT" :value="gv.currencyFormat(hk.selectedRow.summary.debit)" />  
                <ComStayInfoNoBox  label="TOTAL CREDIT" :value="gv.currencyFormat(hk.selectedRow.summary.credit)" />  
                <ComStayInfoNoBox  label="BALANCE" :value="gv.currencyFormat(hk.selectedRow.summary.debit-hk.selectedRow.summary.credit)" />
            </table>
            </template>
        </div>
        <div v-if="hk.reservationStay?.owner || hk.reservationStay?.modified_by">
            <div class="py-2 my-3 mb-10 border-1  bg-slate-200 font-medium text-center">Note</div>
            <div class="mb-5 leading-5 text-sm ">
            <div class="mt-auto">
            <span class="italic">Created by: </span>
            <span class="text-500 font-italic">
                {{ hk.reservationStay?.owner }} {{ gv.datetimeFormat(hk.reservationStay?.creation) }}
            </span>
                </div>
                <div class="mt-auto">
                    <span class="italic"> Last Modified: </span>
                    <span class="text-500 font-italic">
                        {{ hk.reservationStay?.modified_by }} {{ gv.datetimeFormat(hk.reservationStay?.modified) }}
                    </span>
                </div>
                <div>
                    <div v-if="hk.reservationStay?.checked_in_by || hk.reservationStay?.checked_out_by">
                        <div v-if="hk.reservationStay?.checked_in_by || hk.reservationStay?.checked_in_date">
                        <span class="italic">Checked-in by: </span>
                        <span class="text-500 font-italic">
                            {{ hk.reservationStay?.checked_in_by }} {{ gv.datetimeFormat(hk.reservationStay?.checked_in_date) }}
                        </span>
                        </div>
                        <div v-if="hk.reservationStay?.checked_out_by || hk.reservationStay?.checked_out_date">
                        <span class="italic"> Checked-out by: </span>
                        <span class="text-500 font-italic">
                            {{ hk.reservationStay?.checked_out_by }} {{ gv.datetimeFormat(hk.reservationStay?.checked_out_date) }}
                        </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup>
import { inject, ref, useToast} from '@/plugin';
const hk = inject("$housekeeping")
const edoor_setting = JSON.parse(localStorage.getItem('edoor_setting'))
const housekeeping_status = ref(edoor_setting.housekeeping_status)
const visible = ref(false)
const toast = useToast();
const opHousekeeper = ref()
const selected = ref({})
const  submitLoading = ref(false)
const items = ref([])
const show = ref()
const frappe = inject("$frappe")
const db = frappe.db() 
const gv = inject('$gv');

if(housekeeping_status.value.length > 0){
    housekeeping_status.value.forEach(h => {

        items.value.push({
            label: h.status,
            command: () => {
               
                onSelected(h)
            }
        })
         
    });
}

/// change housekeeping status in slidbar
const toggle = (event) => {
    show.value.toggle(event);
};
function onSelected($event){
    if (!hk.selectedRow) {
        toast.add({ severity: 'warn', summary: "Change housekeeping status", detail: "Please select roow to change housekeeping status", life: 3000 })
    } else {

        if($event.is_room_occupy==0 && hk.selectedRow.reservation_stay){
            toast.add({ severity: 'warn', summary: "Change Status", detail: "you cannot assign room have guest to " + $event.status, life: 3000 })
            return
        }
        if($event.is_room_occupy==1 && !hk.selectedRow.reservation_stay){
            toast.add({ severity: 'warn', summary: "Change Status", detail: "you cannot assign room have guest to " + $event.status, life: 3000 })
            return
        }
        db.updateDoc('Room', hk.selectedRow.name, {
            housekeeping_status: $event.status,
            status_color : $event.status_color,
        })
        .then((doc) =>{
            visible.value = false 
            hk.selectedRow.housekeeping_status = doc.housekeeping_status
            hk.selectedRow.status_color = doc.status_color
            toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
            window.socket.emit("ComHousekeepingStatus", window.property_name)
            submitLoading.value = false
        })
        .catch((error) => {
            submitLoading.value = false
        });
    }
}
// Change housekeeper in slidbar
function onAssignHousekeeper($event){
    opHousekeeper.value.toggle($event)
}

function onSaveAssignHousekeeper($event) {
    if(!hk.selectedRow){  
    }else{
    db.updateDoc('Room', hk.selectedRow.name, {
        housekeeper:selected.value.housekeeper,
    })
    .then((doc) =>{
        hk.selectedRow.housekeeper = doc.housekeeper
        toast.add({ severity: 'success', summary: "Assign housekeeping", detail: "Assign housekeeping status successfully", life: 3000 })
        window.socket.emit("RefreshData", {property: setting.property.name,action:"refresh_hk"})
        submitLoading.value = false
        opHousekeeper.value.hide()
    })
    .catch((error) => {
        submitLoading.value = false
    }); 
    } 
}

function whatup($event){
    alert("Hello ")
}

function onViewCustomerDetail(name) {
    window.postMessage('view_guest_detail|'+name, '*')
}

function onViewReservationStayDetail(rs){
    window.postMessage('view_reservation_stay_detail|'+rs, '*')

}

function onViewReservationDetail(rs){
    window.postMessage('view_reservation_detail|'+rs, '*')
}
</script>
