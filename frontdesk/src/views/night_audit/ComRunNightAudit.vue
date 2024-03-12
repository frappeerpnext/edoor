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
                <span :class="step.step < currentStep ? 'step-label step-label-done' : 'step-label'"
                    v-html="step.label"></span>
            </span>
        </template>
    </div>
    <Button @click="LoadData" class="btn-refresh-in-night-audit"><i class="pi pi-refresh"></i></Button>
    <div v-if="currentStep == 9" style="height: 100vh;">
        <ComNightAuditReport />
    </div>
    <div v-else class="wrp-night-audit-content w-full view-table-iframe" style="overflow: auto;
    max-width: 100%;
    max-height: 70vh;">
    <div v-html="html" class="view_table_style run_night_ui_frame"></div>
       
    </div>

    <div class="wrp-action-btn-in-night-audit pb-2">
        <hr class="mb-2" />
        <div class="flex items-center flex-row-reverse flex-wrap">
            <div class="md:order-0 order-1">
                <Button class="border-none mr-2" type="button" label="Back" icon="pi pi-arrow-left" :loading="loading"
                    :disabled="currentStep == 1" v-if="currentStep < 9" @click="onBack" />
                <Button type="button" label="Next" icon="pi pi-arrow-right" class="border-none" :loading="loading"
                    iconPos="right" :disabled="currentStep == steps.length" v-if="currentStep < 8" @click="onNext" />
                <Button class="border-none" :loading="loading" v-if="currentStep == 8" @click="onFinish">Finish</Button>
                <Button class="border-none" v-if="currentStep == 9" @click="onClose">Close</Button>
            </div>
            <div class="md:order-1 order-0 flex items-center gap-2">
                <template v-if="currentStep == 5">
                    <Checkbox inputId="verify-night-audit-data01" v-model="isConfirmRoomRate" :binary="true" />
                    <label for="verify-night-audit-data01" class="mr-3 cursor-pointer">I am verifying that all room rates
                        above are correct.</label>
                </template>
                <template v-if="currentStep == 6">
                    <Checkbox inputId="verify-night-audit-data02" v-model="isConfirmFolioPosting" :binary="true" />
                    <label for="verify-night-audit-data02" class="mr-3 cursor-pointer">I am verifying that all other charges
                        and payments have been accurately posted to the guest folio.</label>
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
 
const confirm = useConfirm()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

const gv = inject("$gv")
const isConfirmRoomRate = ref(false)
const isConfirmFolioPosting = ref(false)
const dialogRef = inject("dialogRef");
const currentStep = ref(1)
const loading = ref(false)
const frappe = inject("$frappe")
const call = frappe.call()
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

const html = ref()

function onNext() {
    //set selected
    if (currentStep.value < steps.value.length) {
        if (currentStep.value > 1) {
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
                LoadData()

                loading.value = false
            }).catch((err) => {
                loading.value = false
            })
        } else {
            currentStep.value = currentStep.value + 1
            LoadData()
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
                working_day: working_day.name
            }, "", false).then((result) => {
                currentStep.value = 9
                LoadData()
                loading.value = false;
                window.socket.emit("RunNightAudit", { property: window.property_name, action: "reload_page", session_id: window.session_id })
                gv.cashier_shift = result.message.cashier_shift
                localStorage.setItem("edoor_working_day", JSON.stringify(result.message))
                window.working_day = result.message
                gv.working_day = result.message
                window.current_working_date = gv.working_day.date_working_day
                window.refresh_on_close=true
            }).catch((err) => {
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
        LoadData()
    }
}

function onClose() {
    dialogRef.value.close()
}
 
const LoadData = () => {
    let param = {
        doc:"Business Branch",
        name:setting?.property?.name,
        format:"eDoor Run Night Audit Step",
        no_letterhead:1,
        letterhead:"No Letterhead",
        _lang:localStorage.getItem("lang") || "en",
        show_toolbar:0,
        view:"ui",
        date:working_day.date_working_day,
        step:currentStep.value
    }
    loading.value = true
    call.get("epos_restaurant_2023.www.printview.get_html_and_style", param).then(result => {
        html.value = result.message.html
        loading.value = false
    }).catch(err=>{
        loading.value = false
    })
    
}

onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    LoadData()
    window.run_night_audit = 1
    window.refresh_on_close=false

    window.socket.on("ComRunNightAudit", (arg) => {
        if (arg.property == window.property_name) { 
            setTimeout(function () {
                LoadData()
            }, 3000)
        }
    })
});

onUnmounted(() => {
    window.run_night_audit = 0
    window.socket.off("ComRunNightAudit");
})
</script>

 