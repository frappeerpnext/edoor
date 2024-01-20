<template>
    <div>
        <ComReservationStayPanel class="" titleClass="text-color-teal-edoor" title="Master Guest">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded aria-haspopup="true" aria-controls="menu_master_guest" @click="onMenuMasterGuest"/>
                <Menu ref="menuMasterGuest" id="menu_master_guest" :model="menuMasterGuestList" :popup="true" />
            </template>
            <template #content> 
                <ComCardProfileGuest  @onClick="onViewGuestDetail(rs.masterGuest?.name)" :dob="rs.masterGuest.date_of_birth"  :photo="rs?.masterGuest?.photo" :color-status="rs?.reservation?.status_color" :name="rs?.masterGuest?.customer_name_en" :phoneNumber1="rs?.masterGuest.phone_number" :email="rs?.masterGuest.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
    </div>
</template>
<script setup>
import {ref, useDialog, inject, updateDoc, useConfirm} from '@/plugin'
import ComCardProfileGuest from './ComCardProfileGuest.vue';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationChangeGuest from './ComReservationChangeGuest.vue'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';

const property = JSON.parse(localStorage.getItem("edoor_property"))
const rs = inject('$reservation');
const gv = inject('$gv');
const dialog = useDialog()
const dialogConfirm = useConfirm()
const menuMasterGuest = ref()
const loading = ref(false)

const menuMasterGuestList = ref([
    {
        label: 'Change Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onAdvancedSearch('master_guest')
        }
    },
    {
        label: 'Edit Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onEditGuest('master_guest')
        }
    }
])



const menuStayGuest = ref()
const menuStayGuestList = ref([
    {
        label: 'Change Guest ',
        command: () =>{
            onAdvancedSearch('stay_guest')
        }
    },
    {
        label: 'Add Additional Guest',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    }
])
const menuAdditionalGuest = ref()
const menuAdditionalGuestList = ref([
{
        label: 'Add Additional Guest',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    },
    {
        label: 'Delete',
        command: ($event) =>{
            onDeleteAdditionalGuest()
        }
    }
])

const onMenuMasterGuest = (event) => {
    menuMasterGuest.value.toggle(event);
};

const onMenuStayGuest = (event) => {
    menuStayGuest.value.toggle(event);
};

const onMenuAdditionalGuest = ($event, name) => {
 
    menuAdditionalGuest.value.additional_guest_name = name
    menuAdditionalGuest.value.toggle($event); 
};

function onDeleteAdditionalGuest(){
    dialogConfirm.require({
        message: 'Do you want to delete this record?',
        header: 'Delete Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            const additionalGuests = rs.reservationStay.additional_guests.filter(r=>r.name != menuAdditionalGuest.value.additional_guest_name)
            const reservationStayData = JSON.parse(JSON.stringify(rs.reservationStay))
            reservationStayData.additional_guests = additionalGuests
            updateDoc('Reservation Stay', reservationStayData.name, reservationStayData, 'Deleted successful').then((doc) => {
                rs.reservationStay = doc
            })
        }
    })
    
}

function onAdvancedSearch(guest_type) { 
    
    dialog.open(ComReservationChangeGuest, {
        props: {
            header: `Select ${guest_type == 'master_guest' ? 'Master Guest' : (guest_type == 'stay_guest' ? 'Stay Guest' : (guest_type == 'additional_guest' ? 'Additional Guest' : '')) }`,
            keyword: '',
            doctype: 'Customer',
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        data:{
            guest_type: guest_type,
            is_change_master_guest: guest_type == 'master_guest',
            is_change_stay_guest: guest_type == 'stay_guest',
            is_change_additional_guest: guest_type == 'additional_guest',
        },
        onClose(r) {
            if(r.data){
                loading.value = true
                rs.LoadReservation(rs.reservation.name)
               
                window.socket.emit("ReservationList", { property:window.property_name})
                gv.toast('success', 'Updated Successful')
            }
        }
    });
}

const onViewGuestDetail =(name)=>{
    window.postMessage('view_guest_detail|' + name, '*');
}

function onEditGuest() {
        dialog.open(ComAddGuest, {
        props: {
            header: `Edit Guest`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        data:{
            name: rs.masterGuest.name,
        },
        onClose: (options) => {
            if(options.data){
                rs.masterGuest = options.data
            }
        }
    }); 
}

</script>
<style lang="">
    
</style>