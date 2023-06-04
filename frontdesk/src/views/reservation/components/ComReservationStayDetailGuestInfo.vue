<template>
    <div>
        <ComReservationStayPanel class="mb-2" titleClass="text-color-teal-edoor" title="Master Guest" v-if="rs.masterGuest?.name != rs.guest?.name">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded aria-haspopup="true" aria-controls="menu_master_guest" @click="onMenuMasterGuest"/>
                <Menu ref="menuMasterGuest" id="menu_master_guest" :model="menuMasterGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest  @onClick="onViewGuestDetail(rs.masterGuest.name)"  :photo="rs?.masterGuest?.photo" :color-status="rs?.reservationStay?.status_color" :name="rs?.masterGuest?.customer_name_en" :phoneNumber2="rs?.masterGuest.phone_number_2" :phoneNumber1="rs?.masterGuest.phone_number_1" :email="rs?.masterGuest.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Stay Guests">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded  aria-controls="menu_stay_guest" @click="onMenuStayGuest"/>
                <Menu ref="menuStayGuest" id="menu_stay_guest" :model="menuStayGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest @onClick="onViewGuestDetail(rs.guest.name)" :photo="rs?.guest?.photo" :color-status="rs?.reservationStay?.status_color" :name="rs?.guest?.customer_name_en" :phoneNumber2="rs?.guest?.phone_number_2"  :phoneNumber1="rs?.guest?.phone_number_1" :email="rs?.guest?.email_address" ></ComCardProfileGuest>
                <div class="border-t mt-2" v-if="rs.reservationStay && rs.reservationStay.additional_guests && rs.reservationStay.additional_guests.length > 0">
                    <div class="py-2" v-for="(ad, index) in rs.reservationStay.additional_guests" :key="index">
                        <ComCardProfileGuest @onClick="onViewGuestDetail(ad.guest)" :photo="ad?.photo" :name="ad.guest_name" :phoneNumber2="ad.phone_number_2"  :phoneNumber1="ad.phone_number_1" :email="ad.email_address" >
                            <template #end>
                                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded @click="onMenuAdditionalGuest($event,ad.name)"/>
                            </template>
                        </ComCardProfileGuest>
                    </div>
                </div>
                <Menu ref="menuAdditionalGuest" :model="menuAdditionalGuestList" :popup="true" />
            </template>
        </ComReservationStayPanel> 
    </div>
</template>
<script setup>
import {ref, useDialog, inject, computed, toaster,updateDoc, useConfirm} from '@/plugin'
import ComCardProfileGuest from './ComCardProfileGuest.vue';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationChangeGuest from './ComReservationChangeGuest.vue'
const property = JSON.parse(localStorage.getItem("edoor_property"))


const rs = inject('$reservation_stay');



const dialog = useDialog()
const dialogConfirm = useConfirm()
const frappe = inject('$frappe')
const socket = inject("$socket")
const db = frappe.db()
const menuMasterGuest = ref()
const loading = ref(false)

const menuMasterGuestList = ref([
    {
        label: 'Change guest',
        command: () =>{
            onAdvancedSearch('master_guest')
        }
    }
])



const menuStayGuest = ref()
const menuStayGuestList = ref([
    {
        label: 'Change guest',
        command: () =>{
            onAdvancedSearch('stay_guest')
        }
    },
    {
        label: 'Add additional guest',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    }
])
const menuAdditionalGuest = ref()
const menuAdditionalGuestList = ref([
{
        label: 'Add additional guest',
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
        acceptClass: 'p-button-danger',
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
            header: `Select ${guest_type == 'master_guest' ? 'master guest' : (guest_type == 'stay_guest' ? 'stay guest' : (guest_type == 'additional_guest' ? 'Additional guest' : '')) }`,
            keyword: '',
            doctype: 'Customer',
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
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

                socket.emit("RefresheDoorDashboard", property.name);
            
                toaster('success', 'Updated Successful')
            }
        }
    });
}

const onViewGuestDetail =(name)=>{
    window.postMessage('view_guest_detail|' + name, '*');
}

</script>
<style lang="">
    
</style>