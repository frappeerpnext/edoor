<template>
    <div> 
        <ComReservationStayPanel class="mb-3" titleClass="text-color-teal-edoor" title="Master Guest" v-if="rs.masterGuest?.name != rs.guest?.name">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded aria-haspopup="true" aria-controls="menu_master_guest" @click="onMenuMasterGuest"/>
                <Menu ref="menuMasterGuest" id="menu_master_guest" :model="menuMasterGuestList" :popup="true" />
               
            </template>
            <template #content>
                <ComCardProfileGuest  @onClick="onViewGuestDetail(rs.masterGuest.name)" :dob="rs?.masterGuest?.date_of_birth"  :photo="rs?.masterGuest?.photo" :color-status="rs?.reservationStay?.status_color" :name="rs?.masterGuest?.customer_name_en" :phoneNumber2="rs?.masterGuest.phone_number_2" :phoneNumber1="rs?.masterGuest.phone_number" :email="rs?.masterGuest.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Stay Guests">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded  aria-controls="menu_stay_guest" @click="onMenuStayGuest"/>
                <Menu ref="menuStayGuest" id="menu_stay_guest" :model="((rs.masterGuest?.name != rs.guest?.name) ? menuStayGuestList : menuStayOneGuest)" :popup="true" />
            </template>
            <template #content> 
                <ComCardProfileGuest @onClick="onViewGuestDetail(rs.guest.name)" :dob="rs?.guest?.date_of_birth" :photo="rs?.guest?.photo" :color-status="rs?.reservationStay?.status_color" :name="rs?.guest?.customer_name_en" :phoneNumber2="rs?.guest?.phone_number_2"  :phoneNumber1="rs?.guest?.phone_number" :email="rs?.guest?.email_address" >
                    <template #footer>
                        <ComReservationStayTransportationLabel/>
                    </template>
                </ComCardProfileGuest>
                <div class="border-t mt-2" v-if="rs.reservationStay && rs.reservationStay.additional_guests && rs.reservationStay.additional_guests.length > 0">
                    <div class="py-2" v-for="(ad, index) in rs.reservationStay.additional_guests" :key="index">
                        <ComCardProfileGuest @onClick="onViewGuestDetail(ad.guest)" :dob="ad?.date_of_birth" :photo="ad?.photo" :name="ad.guest_name" :phoneNumber2="ad.phone_number_2"  :phoneNumber1="ad.phone_number_1" :email="ad.email_address" >
                            <template #end>
                                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded @click="onMenuAdditionalGuest($event,ad.name,ad.guest)"/>
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
import {ref, useDialog, inject, computed, updateDoc, useConfirm, getDoc} from '@/plugin'
import ComCardProfileGuest from './ComCardProfileGuest.vue';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationChangeGuest from './ComReservationChangeGuest.vue'
import ComReservationStayTransportationLabel from './ComReservationStayTransportationLabel.vue'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';


const rs = inject('$reservation_stay');
const gv = inject('$gv');
const dialog = useDialog()
const dialogConfirm = useConfirm()
const menuMasterGuest = ref()
const selectGuestName = ref()
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
        label: 'Add Additional Guest',
        icon:'pi pi-fw pi-user-plus',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    },
    {
        label: 'Change Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onAdvancedSearch('stay_guest')
        }
    },
    {
        label: 'Edit Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onEditGuest('stay_guest')
        }
    }
])
const menuStayOneGuest = ref([
    
    {
        label: 'Add Stay Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onAdvancedSearch('stay_guest')
        }
    },
    {
        label: 'Add Additional Guest',
        icon:'pi pi-fw pi-user-plus',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    },
    {
        label: 'Edit Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onEditGuest('stay_guest')
        }
    }

])
const menuAdditionalGuest = ref()
const menuAdditionalGuestList = ref([
    {
        label: 'Add Additional Guest',
        icon:'pi pi-fw pi-user-plus',
        command: () =>{
            onAdvancedSearch('additional_guest')
        }
    },
    {
        label: 'Edit Guest',
        icon:'pi pi-fw pi-user-edit',
        command: () =>{
            onEditGuest()
        }
    },
    {
        label: 'Delete',
        icon:'pi pi-fw  pi-trash',
        class:'delete-text-color',
        command: () =>{
            onDeleteAdditionalGuest()
        }
    }
])

const onMenuMasterGuest = (event) => {
    selectGuestName.value = rs.masterGuest.name
    menuMasterGuest.value.toggle(event);
};

const onMenuStayGuest = (event) => {
    selectGuestName.value = rs.guest.name
    menuStayGuest.value.toggle(event);
};

const onMenuAdditionalGuest = ($event, name,guest_name) => {
    selectGuestName.value = guest_name
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
                window.postMessage({action:"ReservationStayDetail"},"*")
                window.postMessage({action:"Reports"},"*")
                window.postMessage({action:"ReservationStayList"},"*")
                window.postMessage({action:"ReservationList"},"*")
            })
        }
    })
    
}

function onAdvancedSearch(guest_type) { 
    
    dialog.open(ComReservationChangeGuest, {
        props: {
            header: `${guest_type == 'master_guest' ? 'Change Master Guest' : (guest_type == 'stay_guest' ? 'Add Stay Guest' : (guest_type == 'additional_guest' ? 'Add Additional Guest' : '')) }`,
            keyword: '',
            doctype: 'Customer',
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            pt: {
                root: `${isMobile ? 'p-dialog-maximized' : ''}`
            },
        },
        data:{
            guest_type: guest_type,
            is_change_master_guest: guest_type == 'master_guest',
            is_change_stay_guest: guest_type == 'stay_guest',
            is_change_additional_guest: guest_type == 'additional_guest',
        }, 
        onClose(r) {
            if(r.data){ 
                rs.getReservationDetail(rs.reservationStay.name)
                gv.toast('success', 'Updated Successful')
            }
        }
    });
}
function onEditGuest(guest_type) { 
    if(selectGuestName.value){
        dialog.open(ComAddGuest, {
        props: {
            header: `Edit Guest`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            pt: {
                root: `${isMobile ? 'p-dialog-maximized' : ''}`
            },
        },
        data:{
            name: selectGuestName.value,
        },
        onClose: (options) => {
            if(options.data){
                if(guest_type == 'master_guest'){
                    rs.masterGuest = options.data
                }
                else if(guest_type == 'stay_guest'){
                    rs.guest = options.data
                }else{
                    getDoc('Reservation Stay', rs.reservationStay.name).then((r)=>{
                        rs.reservationStay = r
                        window.postMessage({action:"Reports"},"*")
                    })
                }
            }
            
            
        }
    });
    }
    
}
 
const onViewGuestDetail =(name)=>{
    window.postMessage('view_guest_detail|' + name, '*');
}

</script>
<style lang="">
    
</style>