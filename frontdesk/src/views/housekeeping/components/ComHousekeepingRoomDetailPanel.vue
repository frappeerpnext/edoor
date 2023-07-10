<template>
    <div>
       <div class="">
        <div class="line-height-1 absolute top-4">
        <div class="text-2xl">Detail OF</div>
        <div class="text-sm">{{hk.selectedRow?.room_type}} # {{hk.selectedRow?.room_number}}</div>
        </div>
        <hr class="mb-3">
        <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center">Room Detail</div>
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
         <SplitButton class="w-full" :buttonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" 
         :label="hk.selectedRow?.housekeeping_status"  :model="items" :color="hk.selectedRow?.status_color"  
         :menuButtonProps="{style: {backgroundColor:hk.selectedRow?.status_color}}" >
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
        <div v-if="hk && hk.reservationStay" >
            <div class="py-2 mt-1 border-1  bg-slate-200 font-medium text-center">Reservation Stay Detail</div>
        <table>
            <ComStayInfoNoBox  label="Res Stay No" :value="hk?.reservationStay?.name" /> 
            <ComStayInfoNoBox  label="Status" :value="hk?.reservationStay?.reservation_status" /> 
            <ComStayInfoNoBox  label="Guest Name" :value="hk?.reservationStay?.guest_name" />
            <ComStayInfoNoBox  label="Phone Number" :value="hk?.reservationStay?.guest_phone_number" />  
            <ComStayInfoNoBox  label="Email" :value="hk?.reservationStay?.guest_email" />  
             
            <ComStayInfoNoBox  label="PAX" :value="hk?.reservationStay?.adult + ' / ' + hk?.reservationStay?.child" /> 
            <ComStayInfoNoBox  label="Arrival Date" :value="hk?.reservationStay?.arrival_date +' - '+ hk?.reservationStay?.arrival_time" /> 
            <ComStayInfoNoBox  label="Departure Date" :value="hk?.reservationStay?.departure_date +' - '+ hk?.reservationStay?.departure_time" /> 
            <ComStayInfoNoBox  label="Night" :value="hk?.reservationStay?.room_nights" /> 
        </table>
        </div>
        <div class="mb-10">
           {{ hk.reservationStay }} 
        </div>
        
    </div>
</template>
<script setup>
import { inject, ref, useToast} from '@/plugin';
import ComHousekeepingChangeStatusButton from './ComHousekeepingChangeStatusButton.vue';
import ComBoxStayInformation from '@/views/reservation/components/ComBoxStayInformation.vue';
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
const call = frappe.call()

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
    db.updateDoc('Room', hk.selectedRow.name, {
        housekeeping_status: $event.status,
        status_color : $event.status_color,
    })

    .then((doc) =>{
        visible.value = false 
        hk.selectedRow.housekeeping_status = doc.housekeeping_status
        hk.selectedRow.status_color = doc.status_color
        console.log(doc.housekeeping_status)
        toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
        hk.loadData()
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
        toast.add({ severity: 'success', summary: "Change Status", detail: "Change housekeeping status successfully", life: 3000 })
        hk.loadData()
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
</script>