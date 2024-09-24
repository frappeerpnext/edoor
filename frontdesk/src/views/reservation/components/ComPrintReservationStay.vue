<template>
    <div class="wrap-dialog iframe-modal" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="p-3 view-table-iframe-dialog grid" id="view-table-iframe-dialog" style="height: 85vh;">
          
            <div class="xl:mb-3 mb-0 overflow-auto col-12  xl:col-3 gap-2">
                <div class="flex flex-column gap-2">
                    <div>
                        <Dropdown v-model="filters.selected_folio"  :options="folios" optionLabel="name" placeholder="Select Folio" class="w-full" @change="onSelectFolio" />
                    </div>
                    <div> 
                        <ComLetterHead v-if="!loading" :letterhead="filters.letterHead"  @onSelect="onSelectLetterHead"/>
                    </div>
                   
                </div>
                <br/>
                <div class="flex flex-column gap-2">
       <template v-if="isMobile" >
<Sidebar v-model:visible="visible" header="Setting">
    <div >
                        <Checkbox v-model="filters.show_room_number" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_room_number" />
                        <label for="show_room_number" class="white-space-nowrap" >Show/Hide Room Number</label>
                    </div>
                    
                    <div>
                        <Checkbox v-model="filters.show_account_code" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_account_code" />
                        <label for="show_account_code" class="white-space-nowrap" >Show/Hide Account Code</label>
                    </div>

                    <div>
                        <Checkbox v-model="filters.show_summary" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_summary" />
                        <label for="show_summary" class="white-space-nowrap" >Show/Hide Summary</label>
                    </div>
                    <div>
                        <Checkbox v-model="filters.show_all_room_rate" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_all_room_rate" />
                        <label for="show_all_room_rate" class="white-space-nowrap" >Show All Room Rate in Furture Stay</label>
                    </div>
                    <div>
                        
                        <Checkbox  v-model="filters.breakdown_account_code" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="breakdown_account_code" />
                        <label for="breakdown_account_code" class="white-space-nowrap" >Show/Hide Package Breakdown</label>
                    </div>
</Sidebar>     
       </template>
<template v-else>
                    <div >
                        <Checkbox v-model="filters.show_room_number" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_room_number" />
                        <label for="show_room_number" class="white-space-nowrap" >Show/Hide Room Number</label>
                    </div>
                    
                    <div>
                        <Checkbox v-model="filters.show_account_code" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_account_code" />
                        <label for="show_account_code" class="white-space-nowrap" >Show/Hide Account Code</label>
                    </div>

                    <div>
                        <Checkbox v-model="filters.show_summary" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_summary" />
                        <label for="show_summary" class="white-space-nowrap" >Show/Hide Summary</label>
                    </div>
                    <div>
                        <Checkbox v-model="filters.show_all_room_rate" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="show_all_room_rate" />
                        <label for="show_all_room_rate" class="white-space-nowrap" >Show All Room Rate in Furture Stay</label>
                    </div>
                    <div>
                        <Checkbox  v-model="filters.show_package_breakdown" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" inputId="breakdown_account_code" />
                        <label for="breakdown_account_code" class="white-space-nowrap" >Show/Hide Package Breakdown</label>
                    </div>
 
                    <div v-if="filters?.selected_folio?.show_room_rate_in_guest_folio_invoice==0" style="background: #ebc174;padding: 8px;border-radius: 10px;margin: 5px 0px;">
                        <Checkbox :disabled="!canForceToViewRoomRate"  v-model="filters.force_show_room_rate" :binary="true" :trueValue="1" :falseValue="0" @change="refreshReport" 
                        inputId="force_show_room_rate" />
                        <label for="force_show_room_rate" class="white-space-nowrap" >Show Room Rate</label>
                    </div>

               
                    
</template>
                         
                </div> 
            </div> 
            <div class="widht-ifame col">
                <div>
                    <div class="col flex gap-2 justify-end">
                        <div  v-if="isMobile" >
                            <Button class="white-space-nowrap h-full content_btn_b w-3rem justify-center" @click="visible = true"><i
                        class="pi pi-cog text-xl" />
                </Button>
                    
                    </div>
                        <div v-if="(view||'')!='ui'">
                            <ComPrintButton :url="url"  @click="onPrint"/>
                        </div>
                        <div >
                            <Button @click="refreshReport" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                        </div>
                    </div>
                </div>
                <ComWarningPrintRoomRate v-if="filters?.selected_folio?.show_room_rate_in_guest_folio_invoice==0" display="toast"/>
                <iframe @load="onIframeLoaded()" id="report-view" width="100%" :src="url"></iframe>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted, inject , onUnmounted , getApi,computed} from "@/plugin"
import ComWarningPrintRoomRate from '@/views/reservation/components/ComWarningPrintRoomRate.vue';
 
const visible = ref(false);
const isMobile = ref(window.isMobile)
const dialogRef = inject("dialogRef");
const folios = ref([])

 
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
const url = ref("")
const loading = ref(true)

const reservation_stay = ref("")
const report_name = ref("")


const filters = ref({
    show_account_code:window.setting.show_account_code_in_folio_transaction,
    show_room_number:1,
    show_all_room_rate:0,
    show_summary:0,
    show_package_breakdown:0,

})

const canForceToViewRoomRate = computed(()=>{
    return window.user.roles.includes(window.setting.view_room_rate_in_guest_folio)
})
if(localStorage.getItem('displayViewFolioTransaction')){
    filters.value.show_package_breakdown = parseInt( localStorage.getItem('displayViewFolioTransaction'));  
}

function onSelectFolio(f){
    refreshReport()
}

function onSelectLetterHead(l){
    filters.value.letterHead = l
    refreshReport()

}
const refreshReport = () => {
    if(filters.value.selected_folio){

    
    url.value = serverUrl + "/printview?doctype=Reservation Stay&name=" + filters.value.selected_folio.reservation_stay + "&format=" + report_name.value + "&&settings=%7B%7D&_lang=en&letterhead=" + filters.value.letterHead + "&show_toolbar=0&show_room_number=" + filters.value.show_room_number + "&show_account_code=" + filters.value.show_account_code
    url.value = url.value + "&invoice_style=" + filters.value.invoice_style
    url.value = url.value + "&show_summary=" + filters.value.show_summary || 0
    url.value = url.value + "&show_all_room_rate=" + filters.value.show_all_room_rate || 0
    url.value = url.value + "&show_package_breakdown=" + filters.value.show_package_breakdown || 0
    url.value = url.value + "&force_show_room_rate=" + filters.value.force_show_room_rate || 0
 
    if (filters.value.selected_folio) {
        url.value = url.value + "&folio=" + filters.value.selected_folio.name
        url.value = url.value + "&reservation=" + filters.value.selected_folio.reservation
    }
    
    
    if (dialogRef.value.data.selected_folio_transactions?.length>0) {
        url.value = url.value + "&folio_transactions=" + dialogRef.value.data.selected_folio_transactions.join(",")
    }
    
 

    document.getElementById("report-view").contentWindow.location.replace(url.value)
    }

    // save state
    localStorage.setItem("print_reservation_stay_" + report_name.value.replace(" ",""), JSON.stringify(filters.value))
  
    report_name.value
}
function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    const wrapper = document.getElementById("view-table-iframe-dialog").offsetHeight - 90
    iframe.height = wrapper + 'px'

}
function onPrint(){
    if (filters.value.selected_folio) {
        document.getElementById("report-view").contentWindow.print()
    }
}

function getFolioList(){
    getApi('reservation.get_guest_folio_list', {

            reservation_stay:dialogRef.value.data.reservation_stay || "",
            reservation:dialogRef.value.data.reservation || "",

        })
            .then((result) => {
                folios.value  = result.message
            })
}

onMounted(() => {
    getFolioList()
    if (dialogRef) {
        loading.value = true
        const params = dialogRef.value.data
        reservation_stay.value = params.reservation_stay
        report_name.value = params.report_name

        let state = localStorage.getItem("print_reservation_stay_" + report_name.value.replace(" ",""))
        if (state){
            state = JSON.parse(state)
            Object.keys(state).forEach(key => {
                filters.value[key] = state[key]
            });
            filters.value.force_show_room_rate = 0
        }

        if (!params.folio) {
            filters.value.selected_folio= params.folios[0]
        } else {
            filters.value.selected_folio= params.folio
        }
      
        if (!filters.value.letterHead){
          
            filters.value.letterHead = window.setting.property.default_letter_head
        }
        loading.value = false
       
        refreshReport()

    }



});

</script> 