<template>
<div v-if="rs.reservationFolioList.length>0">
    <div class="flex gap-2 min-h-folio-cus w-full">
        <div class="col-fixed mt-2 res-stay-folio-btn-site-bg px-0 relative wrap-master-list-folio" style="width: 350px;">
            <ComReservationFolioList @onSelectFolio="onSelectFolio"/>
        </div>
        <div class="col px-0 pt-2 overflow-auto">
            
            <div v-if="selectedFolio">
                <div class="w-full p-2 border-1 border-round-lg mb-2 flex ">
                    <span v-if="selectedFolio.is_master" class="bg-purple-100 p-2 w-4rem  flex justify-content-center align-items-center border-round-lg"> <ComIcon style="height: 14px;" icon="iconCrown" /> </span>
                    <div class=" ms-2 white-space-nowrap flex justify-content-between flex-column">
                    <div class="font-bold flex align-items-center">{{ selectedFolio.name }}  <span :class="selectedFolio.status == 'Open' ? '' : 'closed'" class="line-height-2 folio-remark ms-2 " >{{ selectedFolio.status }}</span>  </div>

                    <div class="font-light mt-auto">{{ selectedFolio.reservation_stay }} - {{ selectedFolio.guest_name }}</div>
                 
                    </div>
                </div>
                     
                    <ComFolioAction :loading="loading" @onRefresh="onRefresh" doctype="Reservation Folio" :folio="selectedFolio" :accountGroups="accountGroups?.filter(r => r.show_in_guest_folio==1)" :accountCodeFilter="{is_guest_folio_account:1}" />
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
    import {ref,inject, onMounted,onUnmounted,getApi,provide,useConfirm,createUpdateDoc,useToast} from "@/plugin"
    import ComReservationFolioList from "@/views/reservation/components/reservation_folio/ComReservationFolioList.vue"
    import ComFolioTransactionCreditDebitStyle from "@/views/reservation/components/folios/ComFolioTransactionCreditDebitStyle.vue"
    import ComFolioTransactionSimpleStyle from "@/views/reservation/components/folios/ComFolioTransactionSimpleStyle.vue"
    import ComFolioAction from "@/views/reservation/components/folios/ComFolioAction.vue"
    const toast = useToast();
    const showCreditDebitStyle = ref(window.setting.folio_transaction_style_credit_debit)
    const accountGroups = ref(window.setting.account_group)

    const rs = inject("$reservation")
    const selectedFolio = ref()
    const loading = ref(false)
    const confirm = useConfirm();
    function onSelectFolio(f){
        selectedFolio.value=f
    }
    
    function onRefresh(){
        loadReservationFolioList()
    }

    function loadReservationFolioList(selected_name=""){
 

        loading.value = true
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
        if (rs.roomList.filter(r => r.is_master == 1 ).length == 0) {
            toast.add({ severity: 'warn', detail: "Cannot Create Folio With No Reservation Stay" ,  life: 3000 })
            return
        }
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