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
                <span v-else class="step-btn">
                    {{ index + 1 }}
                </span>

                <span :class="step.step < currentStep ? 'step-label step-label-done' : 'step-label'" v-html="step.label"></span>
            </span>
        </template>
    </div>
    <Button @click="refreshReport" class="btn-refresh-in-night-audit"><i class="pi pi-refresh"></i></Button>
    <div class="wrp-night-audit-content w-full view-table-iframe">
        <iframe @load="onIframeLoaded()" id="iframe_run_night_audit" width="100%" :src="url" style="height: 37rem;"></iframe>
    </div>

    <div class="wrp-action-btn-in-night-audit pb-2">
        <hr class="mb-2" />
        <div class="flex items-center flex-row-reverse flex-wrap">
            <div class="">
                <Button class="border-none mr-2" :disabled="currentStep == 1" v-if="currentStep < 8" @click="onBack">
                    <i class="pi pi-arrow-left mr-2"></i> Back
                </Button>
                <Button class="border-none" :disabled="currentStep == steps.length" v-if="currentStep < 7" @click="onNext">
                    Next <i class="pi pi-arrow-right ml-2"></i>
                </Button>
                <Button class="border-none" v-if="currentStep == 7" @click="onFinish">Finish</Button>
                <Button class="border-none" v-if="currentStep == 8" @click="onClose">Close</Button>
            </div>
            <div class="">
                <template v-if="currentStep == 4">
                    <Checkbox inputId="verify-night-audit-data01" v-model="isConfirmRoomRate" :binary="true" />
                    <label for="verify-night-audit-data01" class="mr-3 cursor-pointer">I am verify that all room rate above is correct.</label>
                </template>
                <template v-if="currentStep == 5">
                    <Checkbox inputId="verify-night-audit-data02" v-model="isConfirmFolioPosting" :binary="true" />
                    <label for="verify-night-audit-data02" class="mr-3 cursor-pointer">I am verify that all other charges and payments has been posted to guest folio.</label>
                </template>
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref, computed, onMounted, postApi, useToast, onUnmounted, inject, useConfirm } from '@/plugin';
const toast = useToast();
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + setting.backend_port;
const url = ref("")
const socket = inject("$socket")
const confirm = useConfirm()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

const isConfirmRoomRate = ref(false)
const isConfirmFolioPosting = ref(false)

const currentStep = ref(1)
const loading = ref(false)
const steps = ref([
    { step: 1, label: "Welcome", is_selected: true },
    { step: 2, label: "Today<br>Reservation", is_selected: false },
    { step: 3, label: "Today<br>Departure", is_selected: false },
    { step: 4, label: "Posting<br>Room Charge", is_selected: false },
    { step: 5, label: "Posting<br>Folio & Deposit", is_selected: false },
    { step: 6, label: "Today<br>Shift", is_selected: false },
    { step: 7, label: "Finish<br>Create New Day", is_selected: false },
    { step: 8, label: "Thank You!", is_selected: false },
])


socket.on("RefreshNightAuditStep", (arg) => {

    if (arg == JSON.parse(localStorage.getItem("edoor_property")).name) {
        refreshReport()
        toast.add({ severity: 'info', summary: 'Info', detail: "night audit stop is updated updated if see this pls remove me", life: 3000 })

    }
})



function onNext() {

    //set selected
    if (currentStep.value < steps.value.length) {
        if (currentStep.value > 1) {
            loading.value = true
            postApi("frontdesk.validate_run_night_audit", {
                property: setting?.property?.name,
                step: currentStep.value
            }, "", false).then((result) => {
                if (currentStep.value == 4) {
                    //confrim room rate
                    if (result.message) {
                        if (isConfirmRoomRate.value == false) {
                            toast.add({ severity: 'warn', summary: "Please tick on confirm room rate check box", detail: '', life: 3000 })
                            return
                        }
                    }
                } else if (currentStep.value == 5) {
                    //confrim folio posting
                    if (result.message) {
                        if (isConfirmFolioPosting.value == false) {
                            toast.add({ severity: 'warn', summary: "Please tick on confirm folio posting check box", detail: '', life: 3000 })
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
    confirm.require({
        message: 'Are you sure you want to process run night audit?',
        header: 'Run Night Audit',
        icon: 'pi pi-exclamation-triangle',
        accept: () => {

            postApi("frontdesk.run_night_audit", {
                property: setting?.property?.name,
                working_day:working_day.name
            }, "", false).then((result) => {
                currentStep.value = 8
                refreshReport()
            })
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

    const iframe = document.getElementById("iframe_run_night_audit");

    iframe.height = iframe.contentWindow.document.body.scrollHeight;

}

const refreshReport = () => {

    url.value = serverUrl + "/printview?doctype=Business%20Branch&name=" + setting?.property?.name + "&format=eDoor%20Run%20Night%20Audit%20Step&no_letterhead=0&letterhead=No Letterhead&settings=%7B%7D&_lang=en&show_toolbar=0&view=ui&date=" + working_day.date_working_day
    url.value = url.value + "&step=" + currentStep.value

    document.getElementById("iframe_run_night_audit").contentWindow.location.replace(url.value)
}



onMounted(() => {
    refreshReport()
});

onUnmounted(() => {
    socket.off("RefreshNightAuditStep");
})

</script>