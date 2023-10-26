<template>
    <div>
        <div class="flex min-h-folio-cus" v-if="rs.folios?.length > 0">
            <ComResevationStayFolioList @onSelectFolio="onSelectFolio"/>
            <div class="col pt-2 overflow-x-auto" v-if="selectedFolio">  
                <ComFolioAction :folio="selectedFolio" />
                <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="selectedFolio" />
                <ComFolioTransactionSimpleStyle v-else :folio="selectedFolio" />
            </div>
            <div v-else>
                <div class="p-6 text-center text-gray-500">
                    <p>Please select a folio</p>
                </div>
            </div>
        </div>
        <div v-else class="min-h-folio-cus flex flex-column justify-content-center">
            <div class="text-center mb-3">
                <Button class="conten-btn" label="Create Folio" icon="pi pi-folder-open" @click="onAddCreatNewFolio()"></Button>
            </div>
            <div class="text-center text-600">Create a Folio to post transactions.</div>
        </div> 
    </div>
</template>

<script setup>
import { inject, ref, onUnmounted ,provide,getDocList,onMounted} from '@/plugin';
import ComResevationStayFolioList from "@/views/reservation/components/reservation_stay_folio/ComResevationStayFolioList.vue"

import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"

import ComNewReservationStayFolio from "@/views/reservation/components/reservation_stay_folio/ComNewReservationStayFolio.vue"
import { useDialog } from 'primevue/usedialog';

const dialog = useDialog();
const rs = inject("$reservation_stay")
const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)
const selectedFolio = ref()
const loading = ref(false)


function onSelectFolio(f){
        selectedFolio.value=f
    }

function setSelectedFolio(selected_name=""){
        if(selected_name==""){
           selected_name = selectedFolio.value?.name 
        }
        if(selected_name){
            const folio = rs.folios.find(x=>x.name==selected_name)
            if(folio){
                folio.selected = true
                selectedFolio.value = folio
                return
            } 
        }
 
        //set first record as selected folio
        const folio = rs.folios[0]
        folio.selected = true
        selectedFolio.value = folio
        
    }
function loadReservationStayFolioList(selected_name=""){
        loading.value = true

        getDocList('Reservation Folio', {
            fields: ["name", "status", "is_master", "rooms", "note", "room_types", "guest", "guest_name", "phone_number", "email", "photo", "status", "balance", "owner","creation","reservation","reservation_stay","business_source"],
            filters: [['reservation_stay', '=', rs.reservationStay.name]],
            limit: 1000
        })
            .then((doc) => {
                rs.folios = doc
                setSelectedFolio(selected_name)
                loading.value = false
            }).catch((err) => {
                loading.value = false
            })
            

    }

    provide('reservation_stay', {
        loadReservationStayFolioList
    })

function onAddCreatNewFolio() {

    const dialogRef = dialog.open(ComNewReservationStayFolio, {
        data: {
            reservation_stay: rs.reservationStay.name,
            property: window.property_name
        },
        props: {
            header: 'Create New Folio ',
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
                rs.onLoadReservationFolios().then(() => {
                    rs.onLoadFolioTransaction(data)
                    loadReservationStayFolioList(data.name)
                })
            }
        }
    })
}

const windowActionHandler = async function (e) {
        if (e.isTrusted) {
            if (e.data.action == "load_reservation_stay_folio_list") {
                setTimeout(function () {
                    loadReservationStayFolioList()
                }, 2000)

            }

        }
    }

  
onMounted(() => {
    loadReservationStayFolioList()
    window.addEventListener('message', windowActionHandler, false);
})
onUnmounted(()=>{
    window.removeEventListener('message', windowActionHandler, false);
})
 

</script>