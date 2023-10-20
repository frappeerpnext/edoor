<template>
<div v-if="rs.reservationFolioList.length>0">
    <table style="width: 100%;">
        <tr>
            <td>
                <ComReservationFolioList @onSelectFolio="onSelectFolio"/>
            </td>
            <td>
                <div v-if="selectedFolio">
                    <ComFolioAction :folio="selectedFolio" />
                    <ComFolioTransactionCreditDebitStyle v-if="showCreditDebitStyle" :folio="selectedFolio" />
                    <ComFolioTransactionSimpleStyle v-else :folio="selectedFolio" />
                </div>
            </td>
        </tr>
    </table>
</div>
<div v-else> 
    <Button @click="onCreateMasterFolio">Create a Master Folio</Button>
    Create a  Folio to post transactions.
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