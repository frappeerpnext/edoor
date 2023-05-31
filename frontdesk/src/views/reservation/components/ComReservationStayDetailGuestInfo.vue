<template>
    <div v-if="data">
        <ComReservationStayPanel class="mb-2" titleClass="text-color-teal-edoor" title="Master Guest" v-if="data.master_guest?.name != data.guest?.name">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded aria-haspopup="true" aria-controls="menu_master_guest" @click="onMenuMasterGuest"/>
                <Menu ref="menuMasterGuest" id="menu_master_guest" :model="menuMasterGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest :photo="data?.master_guest?.photo" :color-status="data?.reservation_stay?.status_color" :name="data?.master_guest?.customer_name_en" :phoneNumber2="data?.master_guest?.phone_number_2" :phoneNumber1="data?.master_guest?.phone_number_1" :email="data?.master_guest?.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Stay Guests">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded  aria-controls="menu_stay_guest" @click="onMenuStayGuest"/>
                <Menu ref="menuStayGuest" id="menu_stay_guest" :model="menuStayGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest :photo="data?.guest?.photo" :color-status="data?.reservation_stay?.status_color" :name="data?.guest?.customer_name_en" :phoneNumber2="data?.guest?.phone_number_2"  :phoneNumber1="data?.guest?.phone_number_1" :email="data?.guest?.email_address" ></ComCardProfileGuest>
                <div class="border-t mt-2" v-if="data.reservation_stay && data.reservation_stay.additional_guests && data.reservation_stay.additional_guests.length > 0">
                    <div class="py-2" v-for="(ad, index) in data.reservation_stay.additional_guests" :key="index">
                        <ComCardProfileGuest :photo="ad?.photo" :name="ad.guest_name" :phoneNumber2="ad.phone_number_2"  :phoneNumber1="ad.phone_number_1" :email="ad.email_address" >
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
import {ref, useDialog, inject, computed, useToast, useConfirm} from '@/plugin'
import ComCardProfileGuest from './ComCardProfileGuest.vue';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationChangeGuest from './ComReservationChangeGuest.vue'
const property = JSON.parse(localStorage.getItem("edoor_property"))
const props = defineProps({
    modelValue: Object
})
const emit = defineEmits(['update:modelValue'])
const dialog = useDialog()
const toast = useToast()
const dialogConfirm = useConfirm()
const frappe = inject('$frappe')
const socket = inject("$socket")
const db = frappe.db()
const menuMasterGuest = ref()
const loading = ref(false)
const data = computed({
    get(){
        return props.modelValue
    },
    set(newValue){
        return newValue
    }
})
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
            const additionalGuests = data.value.reservation_stay.additional_guests.filter(r=>r.name != menuAdditionalGuest.value.additional_guest_name)
            const reservationStayData = JSON.parse(JSON.stringify(data.value.reservation_stay))
            reservationStayData.additional_guests = additionalGuests
            db.updateDoc('Reservation Stay', reservationStayData.name, reservationStayData)
                .then((doc) => {
                    data.value.reservation_stay = doc
                    toast.add({ severity: 'success', summary: 'Deleted Successful', detail: '', life: 30000000 });
                })
                .catch((error) => {
                    toast.add({ severity: 'error', summary: 'Error', detail: JSON.stringify(error), life: 3000 });
                });
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
            reservation: props.modelValue?.reservation,
            reservation_stay: props.modelValue?.reservation_stay,
            guest_type: guest_type,
            is_change_master_guest: guest_type == 'master_guest',
            is_change_stay_guest: guest_type == 'stay_guest',
            is_change_additional_guest: guest_type == 'additional_guest',
            total_reservation_stay: props.modelValue.total_reservation_stay
        },
        onClose(r) {
            if(r.data){
                loading.value = true
                if(r.data.is_master_guest)
                    data.value.master_guest = r.data.guest
                if(r.data.is_guest_stay)
                    data.value.guest = r.data.guest
                if(r.data.reservation_stay)
                    data.value.reservation_stay = r.data.reservation_stay
                socket.emit("RefresheDoorDashboard", property.name);
                emit('update:modelValue', data.value)
                toast.add({ severity: 'success', summary: 'Updated Successful', detail: '', life: 3000 });
            }
        }
    });
}
</script>
<style lang="">
    
</style>