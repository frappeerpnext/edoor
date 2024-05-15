
<template>
    <div class="wrap-dialog iframe-modal" :class="{'full-height' : dialogRef.data.fullheight}">
        <div class="p-3 pt-2 view-table-iframe-dialog" :class="(view||'')!='ui' ? 'grid' : ''" style="height: 85vh;">
            <div :class="(view||'')!='ui' ? 'col-4 lg:col-3' : ''">
                <div class="grid">
                    <div :class="(view||'')!='ui' ? 'w-full flex flex-column gap-2' : 'col flex align-items-center gap-2'">
                        <div :class="(view||'')!='ui' ? '' : 'col'">
                            <Dropdown v-model="selected_guest" :options="guests" optionLabel="guest_name" optionValue="name"
                    placeholder="Select Guest" class="w-full " @change="refreshReport" />
                        </div>
                        <div :class="(view||'')!='ui' ? '' : 'col'">                      
                            <ComLetterHead v-model="letter_head" class="w-full"  @onSelect="onSelectLetterHead"/>
                            <!-- <ComSelect  class="ml-2" place-holder="Letter Head" v-model="letter_head" doctype="Letter Head" @change="refreshReport" /> -->
                        </div>
                        <div :class="(view||'')!='ui' ? '' : 'col'">
                            <div>
                                <Checkbox v-model="show_rate" :binary="true" :trueValue="1" :falseValue="0"
                                    @input="refreshReport" inputId="show_rate" />
                                    <label class="pl-1" for="show_rate">Show Rate</label>
                            </div> 
                        </div>
                    </div>
                    <div class="col flex justify-content-end align-items-center gap-2" v-if="(view || '') == 'ui'">
                        <!-- <div v-if="(view||'')!='ui'">
                            
                            <ComPrintButton :url="url"  @click="onPrint"/> 
                            
                        </div> -->
                        <div>
                            <Button @click="refreshReport" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                        </div>
                    </div>
                    
                </div> 
            </div>
            <div :class="(view||'')!='ui' ? 'col' : ''">
                <div class="col flex gap-2 justify-end" v-if="(view || '') != 'ui'">
                    <div v-if="(view||'')!='ui'">
                        <ComPrintButton :url="url"  @click="onPrint"/> 
                    </div>
                    <div>
                        <Button @click="refreshReport" icon="pi pi-refresh" class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div>
                </div>
                <!-- iframe -->
                <div class="widht-ifame">
                    <iframe @load="onIframeLoaded()" id="report-view" width="100%" :src="url"></iframe>
                </div>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, onMounted, inject,getApi } from "@/plugin"
import { callWithAsyncErrorHandling } from "vue";

const dialogRef = inject("dialogRef");

const gv = inject("$gv")




const serverUrl = window.location.protocol=="http:"?"http://" + window.location.hostname + ":" + window.setting.backend_port:"https://" + window.location.hostname;
const url = ref("")
const guests = ref([]);
const selected_guest = ref({})
const filter_options = ref([])
const letter_head = ref("")
const reservationStay = ref("")
const show_rate = ref([])


function onSelectLetterHead(l){
    letter_head.value = l
    refreshReport()
}

function onIframeLoaded() {
    const iframe = document.getElementById("report-view");
    iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    // iframe.height = iframe.contentWindow.document.body.scrollHeight;
    
}

const refreshReport = () => {
    if (selected_guest.value) {
        url.value = serverUrl + "/printview?doctype=Reservation%20Stay&name=" + reservationStay.value + "&format="+ gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&show_toolbar=0&letterhead="+ letter_head.value +"&settings=%7B%7D&_lang=en&show_toolbar=1&customer=" + selected_guest.value
    }
    if (show_rate.value) {
        url.value = serverUrl + "/printview?doctype=Reservation%20Stay&name=" + reservationStay.value + "&format="+ gv.getCustomPrintFormat("eDoor Guest Registration Card")+"&no_letterhead=0&show_toolbar=0&letterhead="+ letter_head.value +"&settings=%7B%7D&_lang=en&show_toolbar=1&customer=" + selected_guest.value + "&show_rate=" + show_rate.value
    }
    document.getElementById("report-view").contentWindow.location.replace(url.value)
}

function onPrint(){

    document.getElementById("report-view").contentWindow.print()

}

onMounted(() => {
    if (dialogRef) {
        const params = dialogRef.value.data
        reservationStay.value = params.reservation_stay

    getApi('reservation.get_reservation_guest', {
            reservation: params.reservation,
            reservation_stay: params.reservation_stay
        })
            .then((result) => {
                guests.value = result.message
                if (!params.name) {

                        selected_guest.value = guests.value[0].name

                } else {
                    selected_guest.name = params.name
                }
                refreshReport()
            })

    }



});
</script> 