<template>
    <div class="wrape-step-night-audit flex justify-between aj relative mb-5">
        <span class="step-life-time"><!--NA--></span>
        <template v-for="(step, index) in steps" :key="index">
            <span v-if="step.step == currentStep" class="flex">
                <span class="step-btn current-step">{{ index + 1 }}</span>
                <span class="step-label current-step-label" v-html="step.label"></span>
            </span>
            <span v-else class="flex">
                <span v-if="step.step < currentStep" class="step-btn step-btn-done">
                    <i class="pi pi-check"></i>
                </span>
                <span v-else class="step-btn">{{ index + 1 }}</span>
                <span :class="step.step < currentStep ? 'step-label step-label-done' : 'step-label'" v-html="step.label"></span>
            </span>
        </template>
    </div>
    <Button @click="refreshReport" class="btn-refresh-in-night-audit"><i class="pi pi-refresh"></i></Button>
    <div v-if="currentStep == 9" style="height: 100vh;">
        <ComNightAuditReport/>
    </div>
    <div v-else class="wrp-night-audit-content w-full view-table-iframe">
        <iframe @load="onIframeLoaded()" id="iframe_run_night_audit" style="min-height:71vh; width: 100%; overflow-x: hidden;" :src="url" ></iframe>
    </div>

    <div class="wrp-action-btn-in-night-audit pb-2">
        <hr class="mb-2" />
        <div class="flex items-center flex-row-reverse flex-wrap">
            <div class="">
                <Button class="border-none mr-2" type="button" label="Back" icon="pi pi-arrow-left"  :loading="loading" :disabled="currentStep == 1" v-if="currentStep < 9" @click="onBack" />
                <Button type="button" label="Next" icon="pi pi-arrow-right" class="border-none" :loading="loading" iconPos="right" :disabled="currentStep == steps.length" v-if="currentStep < 8" @click="onNext" />
                <Button class="border-none" :loading="loading" v-if="currentStep == 8" @click="onFinish">Finish</Button>
                <Button class="border-none" v-if="currentStep == 9" @click="onClose">Close</Button>
            </div>
            <div class="">
                <template v-if="currentStep == 5">
                    <Checkbox inputId="verify-night-audit-data01" v-model="isConfirmRoomRate" :binary="true" />
                    <label for="verify-night-audit-data01" class="mr-3 cursor-pointer">I am verifying that all room rates above are correct.</label>
                </template>
                <template v-if="currentStep == 6">
                    <Checkbox inputId="verify-night-audit-data02" v-model="isConfirmFolioPosting" :binary="true" />
                    <label for="verify-night-audit-data02" class="mr-3 cursor-pointer">I am verifying that all other charges and payments have been accurately posted to the guest folio.</label>
                </template>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, postApi, useToast, onUnmounted, inject, useConfirm } from '@/plugin';
import ComNightAuditReport from './components/ComNightAuditReport.vue'
const toast = useToast();
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("") 
const confirm = useConfirm()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const gv = inject("$gv")
const isConfirmRoomRate = ref(false)
const isConfirmFolioPosting = ref(false)
const dialogRef = inject("dialogRef");
const currentStep = ref(9)
const loading = ref(false)

const steps = ref([
    { step: 1, label: "Welcome", is_selected: true },
    { step: 2, label: "Today<br>Arrival", is_selected: false },
    { step: 3, label: "Today<br>Departure", is_selected: false },
    { step: 4, label: "Today<br>Reservation", is_selected: false },
    { step: 5, label: "Posting<br>Room Charge", is_selected: false },
    { step: 6, label: "Today<br>Posting Transaction", is_selected: false },
    { step: 7, label: "Today<br>Shift", is_selected: false },
    { step: 8, label: "Finish<br>Create New Day", is_selected: false },
    { step: 9, label: "Thank You!", is_selected: false },
])



function onNext() {
    //set selected
    if (currentStep.value < steps.value.length) {
        if (currentStep.value > 1){   
            loading.value = true
            postApi("frontdesk.validate_run_night_audit", {
                property: setting?.property?.name,
                step: currentStep.value
            }, "", false).then((result) => {
                if (currentStep.value == 5) {
                    //confrim room rate
                    if (result.message) {
                        if (isConfirmRoomRate.value == false) {
                            toast.add({ severity: 'warn', summary: "Please tick on confirm room rate check box", detail: '', life: 3000 })
                            loading.value = false
                            return
                        }
                    }
                } else if (currentStep.value == 6) {
                    //confrim folio posting
                    if (result.message) {
                        if (isConfirmFolioPosting.value == false) {
                            toast.add({ severity: 'warn', summary: "Please tick on confirm folio posting transaction check box", detail: '', life: 3000 })
                            loading.value = false
                            return
                        }
                    }
                }
                currentStep.value = currentStep.value + 1
                refreshReport()

                loading.value = false
            }).catch((err) => {
                loading.value = false
            })
        } else {
            currentStep.value = currentStep.value + 1
            refreshReport()
        }
    }
}

function onFinish() {
    loading.value = true;
    confirm.require({
        message: 'Are you sure you want to process run night audit?',
        header: 'Run Night Audit',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            postApi("frontdesk.run_night_audit", {
                property: setting?.property?.name,
                working_day:working_day.name
            }, "", false).then((result) => { 
                currentStep.value = 9
                refreshReport()
                loading.value = false;
                window.socket.emit("RunNightAudit",{property:window.property_name, action:"reload_page",session_id:window.session_id})
                gv.cashier_shift = result.message.cashier_shift
                localStorage.setItem("edoor_working_day", JSON.stringify(result.message))
                window.working_day = result.message
                gv.working_day = result.message
                window.current_working_date = gv.working_day.date_working_day
            }).catch((err)=>{
                loading.value = false;
            }).finally(() => {
                loading.value = false; 
            });
        },
        reject: () => {
            loading.value = false; 
        },
        onHide: () => {
            loading.value = false; 
        },
    }); 
}


function onBack() {
    //set selected
    if (currentStep.value > 1) {
        loading.value = true
        currentStep.value = currentStep.value - 1
        refreshReport()
    }
}

function onClose(){
    dialogRef.value.close()
}

function onIframeLoaded() {
    loading.value = false
    const iframe = document.getElementById("iframe_run_night_audit");
    if (iframe.contentWindow.document.body.scrollWidth < iframe.offsetWidth) {
        iframe.style.overflowX = 'hidden';
    } else {
        iframe.style.overflowX = 'auto';
    }
    iframe.style.minWidth ="0px"
    iframe.style.minWidth = iframe.contentWindow.document.body.scrollWidth + 'px';
    // iframe.style.height = '0px';
    // iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
}

const refreshReport = () => {
    loading.value = true
    url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + setting?.property?.name + "&format=" +gv.getCustomPrintFormat("eDoor Run Night Audit Step")+"&no_letterhead=0&letterhead=No Letterhead&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui&date=" + working_day.date_working_day
    url.value = url.value + "&step=" + currentStep.value
    const el =  document.getElementById("iframe_run_night_audit")
    if(el){
        el.contentWindow.location.replace(url.value)
    } 
}

onMounted(() => {
    refreshReport()
    window.socket.on("ComRunNightAudit", (arg) => {
        if (arg.property == window.property_name) {
            setTimeout(function(){
                refreshReport()
            },3000) 
        }
    })
});

onUnmounted(()=>{
    window.socket.off("ComRunNightAudit");
})
</script>

 