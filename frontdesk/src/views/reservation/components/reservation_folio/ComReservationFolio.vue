<template>
<div v-if="rs.reservationFolioList.length>0">
    <div class="flex gap-2 w-full">
        <div class="col-3 px-0 relative" style="width: 350px;">
            <ComReservationFolioList @onSelectFolio="onSelectFolio"/>
        </div>
        <div class="col-9 px-0 pt-3">
            
            <div v-if="selectedFolio">
                <div class="w-full p-2 border-1 border-round-lg mb-3 flex">
                    <span v-if="selectedFolio.is_master" class="bg-purple-100 p-2 w-3rem  flex justify-content-center align-items-center border-round-lg"> <ComIcon style="height: 14px;" icon="iconCrown" /> </span>
                    <div class="line-height-2 ms-2">
                    <div class="font-bold flex align-items-center">{{ selectedFolio.name }}  <span :class="selectedFolio.status == 'Open' ? 'text-green-700' : 'text-orange-700'" class="line-height-2 font-italic  folio-remark font-light ms-2 " >{{ selectedFolio.status }}</span>  </div>
                    
                    <span class="font-light">{{ selectedFolio.reservation_stay }} - {{ selectedFolio.guest_name }}</span>
                    </div>
                    
                </div>
                    <ComFolioAction :folio="selectedFolio" />
                    <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="selectedFolio" />
                    <ComFolioTransactionSimpleStyle v-else :folio="selectedFolio" />
            </div>
        </div>
    </div>
</div>
<div v-else class="min-h-folio-cus flex flex-column justify-content-center"> 
    <div class="text-center mb-3">
        <Button class="conten-btn" label="Create a Master Folio" icon="pi pi-folder-open"  @click="onCreateMasterFolio"></Button>
    </div>
    <div class="text-center text-600">Create a Folio to post transactions.</div>
</div>
   
</template>
<script setup>
    import {ref,inject, onMounted,onUnmounted,getApi,provide,useConfirm,createUpdateDoc} from "@/plugin"
    import ComReservationFolioList from "@/views/reservation/components/reservation_folio/ComReservationFolioList.vue"
    import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
    import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
    import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"
    const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)
    const rs = inject("$reservation")
    const selectedFolio = ref()
    const loading = ref(false)
    const confirm = useConfirm();
    function onSelectFolio(f){
        selectedFolio.value=f
    }
    
    function loadReservationFolioList(selected_name=""){
 

        loading.value = false
        getApi('reservation.get_reservation_folio_list', {
			reservation:rs.reservation.name
		}).then((result) => {
			rs.reservationFolioList = result.message 
          
            setSelectedFolio(selected_name)
           
             loading.value = false
		}).catch(err=>{
            loading.value =false
        })
    }


    function setSelectedFolio(selected_name=""){
        
        
        if(selected_name==""){
           selected_name = selectedFolio.value?.name 
        }
        

        if(selected_name){
            const folio = rs.reservationFolioList.map(r=>r.folios).flat().find(x=>x.name==selected_name)
            if(folio){
                folio.selected = true
                selectedFolio.value = folio
                return
            } 
        }

        //set first record as selected folio
        const folio = rs.reservationFolioList[0].folios[0]
        folio.selected = true
        
        selectedFolio.value = folio
    }

    function onCreateMasterFolio(){
        loading.value = true
        confirm.require({
            message: 'Are you sure you want to create master folio?',
            header: 'Confirmation',
            icon: 'pi pi-info-circle',
            acceptLabel: 'Create',
            acceptIcon: 'pi pi-check-circle',
            acceptClass: 'border-none btn-ok_ss',
            rejectClass: 'hidden',

            accept: () => {
                const doc = {
                    property:window.property_name,
                    reservation:rs.reservation.name,
                    guest: rs.reservation.guest,
                    reservation_stay: rs.reservationStays.find(r=>r.is_master==1).name
                }
                createUpdateDoc('Reservation Folio', {data: doc})
                .then((doc) => {
                    loadReservationFolioList(doc.name)
                    loading.value = false
                    window.socket.emit("ReservationDetail", {reservation_stay:rs.reservation.name})
                }).catch(()=>{
                    loading.value = false
                })
            },
            
        });
    }
    
    const windowActionHandler = async function (e) {
        if (e.isTrusted) {
            if (e.data.action == "load_reservation_folio_list") {
                    loadReservationFolioList((e.data.selected_folio_name || ""))
            }
        }
    }


    onMounted(() => {
        loadReservationFolioList()
        window.addEventListener('message', windowActionHandler, false);

    })
   

   onUnmounted(() => {
     window.removeEventListener('message', windowActionHandler, false);
   })

</script>