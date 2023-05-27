<template>
    <div>
        <ComReservationStayPanel class="mb-2" title="Master Guest" >
            <template #btn>
                <Button icon="pi pi-ellipsis-h" style="font-size: 1.5rem" text rounded aria-haspopup="true" aria-controls="menu_master_guest" @click="onMenuMasterGuest"/>
                <Menu ref="menuMasterGuest" id="menu_master_guest" :model="menuMasterGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest :photo="data?.master_guest?.photo" :name="data?.master_guest?.customer_name_en" :phoneNumber2="data?.master_guest?.phone_number_2" :phoneNumber1="data?.master_guest?.phone_number_1" :email="data?.master_guest?.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Stay Guests">
            <template #btn>
                <Button icon="pi pi-ellipsis-h" style="font-size: 1.5rem" text rounded  aria-controls="menu_stay_guest" @click="onMenuStayGuest"/>
                <Menu ref="menuStayGuest" id="menu_stay_guest" :model="menuStayGuestList" :popup="true" />
            </template>
            <template #content>
                <ComCardProfileGuest :photo="data?.guest?.photo" :name="data?.guest?.customer_name_en" :phoneNumber2="data?.guest?.phone_number_2"  :phoneNumber1="data?.guest?.phone_number_1" :email="data?.guest?.email_address" ></ComCardProfileGuest>
            </template>
        </ComReservationStayPanel>
    </div>
</template>
<script setup>
import {ref, useDialog, inject, computed, useToast} from '@/plugin'
import ComCardProfileGuest from './ComCardProfileGuest.vue';
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import ComReservationChangeGuest from './ComReservationChangeGuest.vue'
const props = defineProps({
    modelValue: Object
})
const dialog = useDialog()
const toast = useToast()
const frappe = inject('$frappe')
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
        label: 'Change master guest',
        command: () =>{
            onAdvancedSearch('master_guest')
        }
    },
    {
        label: 'Add stay guest',
        command: () =>{
            alert()
        }
    },
    {
        label: 'Add additional guest',
        command: () =>{
            alert()
        }
    }
])
const onMenuMasterGuest = (event) => {
    menuMasterGuest.value.toggle(event);
};


const menuStayGuest = ref()
const menuStayGuestList = ref([
    {
        label: 'Change stay guest',
        command: () =>{
            alert()
        }
    },
    {
        label: 'Add additional guest',
        command: () =>{
            alert()
        }
    },
    {
        label: 'Delete guest',
        command: () =>{
            alert()
        }
    }
])
const onMenuStayGuest = (event) => {
    menuStayGuest.value.toggle(event);
};

function onAdvancedSearch(guest_type) {
    console.log(guest_type)
    dialog.open(ComReservationChangeGuest, {
        props: {
            header: 'Select Guest',
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
        onClose(r) {
            if(r.data){
                loading.value = true
                if(guest_type == 'master_guest'){
                    onUpdateGuest(r.data, guest_type)
                }
                // db.getDoc('Customer', r.data)
                // .then((doc) => {
                //     if(guest_type == 'master_guest'){
                //         console.log(doc)
                //     }
                // })
                // .catch((error) => console.error(error));
            }
        }
    });
}

function onUpdateGuest(guest_name, guest_type){
    let doctype = ''
    let name = ''
    if(guest_type == 'master_guest'){
        doctype = 'Reservation'
        name = data.value.reservation.name
    }
        
    db.updateDoc(doctype, name, {
        guest: guest_name,
    })
    .then((doc) => {
        if(guest_type == 'master_guest'){
            onUpdateMasterGuestInfo(doc)
        }
    })
    .catch((error) => console.error(error));
}

function onUpdateMasterGuestInfo(doc){
    data.value.master_guest.name = doc.guest
    data.value.master_guest.photo = doc.guest_photo
    data.value.master_guest.customer_name_en = doc.guest_name
    data.value.master_guest.phone_number_2 = doc.phone_number_2
    data.value.master_guest.phone_number_1 = doc.phone_number
    data.value.master_guest.email_address = doc.email_address
    toast.add({ severity: 'success', summary: 'Updated Successful', detail: '', life: 3000 });
}

</script>
<style lang="">
    
</style>