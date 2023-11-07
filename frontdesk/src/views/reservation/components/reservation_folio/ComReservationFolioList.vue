<template>
    <div class="card mt-1 border-round-lg reservatin_folio_list_box">
        <!-- expandIcon="pi" collapseIcon="pi" -->
        <Accordion   :multiple="true" :activeIndex="[0]">
            <template v-for="(s, index) in rs.reservationFolioList" :key="index">
    <AccordionTab :headerClass="s.folios.some(d => d.selected) ? 'header_folio_active' : ''" >
        <template #header>
            <div  class="flex flex flex-column w-full -mr-3 ps-2 -ml-3 -mt-2 -mb-2 ">
                <div class="flex">
            <span class="flex align-items-center gap-2 w-full line-height-3">
                <div class="ml-2 w-full">
                    <div class="flex w-full gap-2 align-items-center">
                        <span class="link_line_action1 " @click="onViewReservationStayDetail(s.name); $event.stopPropagation()" >{{ s.name }}</span>
                        <div class="px-2 rounded-lg text-white font-light w-status-reservation-folio" v-tippy="s.reservation_status" :style="{backgroundColor:s.status_color}"></div>              
                        
                        <span v-tippy="'Folio'" class="px-2 bg-gray-400 rounded-lg text-white font-light" >
                            {{ s.folios.length }}
                        </span>
                        <span v-tippy="'Balance'" class="ms-auto me-2 px-2 bg-white rounded-lg  white-space-nowrap"> <CurrencyFormat :value="s.balance" /> </span>
                    </div>
                    <div class="flex gap-2 align-items-center">
                    <div  class="font-light max-width-name-text">{{ s.guest_name }} </div>
                    <spna class="font-light " >|</spna>
                    <div class="font-light  max-width-name-text" > Room: {{ s.rooms }}</div>
                    </div>
                    
                </div>
               
            </span>
            <spna class="flex align-items-center" >
            </spna>
            
            <Button @click="onAddNewFolio(s); $event.stopPropagation()" v-tippy="'Add New Folio To ' + s.name" class="py-2 px-3 ml-auto btn-add-folio w-2rem h-2rem font-bold" style="color:#4338ca;" icon="pi pi-plus" />
            </div>
            </div>
        </template>
        <div class="m-0 p-2">
           <div  v-for="(d, index) in s.folios" :key="index">
            <Button class="fofio_class_btn_child w-full flex gap-2 py-1 justify-content-between align-items-center px-3 bg-white" @click="onSelectFolio(d)" :class="[d.selected ? 'active_reservation_folio' : '', index > 0 ? 'mt-2' : '']" >
    <div class="flex align-items-center gap-3 line-height-2">
        <ComIcon v-if="d.is_master" style="height: 14px;" icon="iconCrown" />
        <div class="text-start">
            <div >
                {{ d.name }}
            </div>
            <div class="flex" >
                <div v-tippy="d.guest_name.length > 25 ? d.guest_name :''" class="text-overflow-ellipsis white-space-nowrap overflow-hidden me-2" style="max-width: 150px;">
                {{ d.guest_name }}
                </div>
                <span class="line-height-2 font-italic text-sm folio-remark me-1" :class="d.status == 'Open' ? 'text-green-700' : 'text-orange-700'" >{{ d.status }}</span>
                
            </div>
        </div>
    </div>
    <div class="text-end">
        <div><CurrencyFormat :value="d.balance" /></div>
        <div class="white-space-nowrap">{{ gv.dateFormat(d.posting_date)
                            }}</div>
        
    </div>
            </Button>
           </div>
        </div>
    </AccordionTab>
</template>
</Accordion>
    </div> 
    <div class="flex flex-column bg-white mt-3 fixed total_foliolist " style="width: 350px; bottom: 0px; z-index: 1;">
        <div class="flex justify-content-end align-items-cente border-1 border-red-100 p-2"><div class="pr-3"><label>Total Debit</label></div><div><span><span class="white-space-nowrap font-medium"> <CurrencyFormat :value="rs.reservation.total_debit" /></span></span></div></div>
        <div class="flex justify-content-end align-items-cente border-1 border-red-100 border-top-none p-2"><div class="pr-3"><label>Total Credit</label></div><div><span><span class="white-space-nowrap font-medium"><CurrencyFormat :value="rs.reservation.total_credit" /></span></span></div></div>
        <div class="flex justify-content-end align-items-center border-1 border-red-100 border-top-none p-2"><div class="pr-3"><label>Balance</label></div><div><span><span class="white-space-nowrap font-medium"><CurrencyFormat :value="rs.reservation.balance" /></span></span></div></div>
    </div>
    <div class="h-7rem relative">
   
</div>
</template>
<script setup>
import {  inject, useDialog } from '@/plugin';
import Accordion from 'primevue/accordion';
import AccordionTab from 'primevue/accordiontab';
import ComNewReservationStayFolio from '@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue';
const gv = inject('$gv');
const dialog = useDialog();
const rs = inject("$reservation")
const emit = defineEmits(["onSelectFolio"])

 

function onSelectFolio(f) {
    clearSelectedFolio()
    f.selected = true


    emit("onSelectFolio", f)
}
function clearSelectedFolio() {
    const selected = rs.reservationFolioList.map(r => r.folios).flat().find(x => x.selected == true)
    if (selected) {
        selected.selected = false
    }

}

function onAddNewFolio(stay) {
    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
                guest: stay.guest,
                reservation:stay.folios[0].reservation,
                reservation_stay: stay.name,
                property: window.property_name
        },
        props: {

            header: 'Create New Folio',
            style: {
                width: '50vw',
            },
            modal: true,
            position: 'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const data = options.data;
            if (data != undefined) {

                loadReservationFolioList(data.name)
            }
        }
    })
}

function onViewReservationStayDetail(rs){
    window.postMessage('view_reservation_stay_detail|'+rs, '*')

}
</script>