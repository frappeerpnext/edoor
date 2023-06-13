<template>
    <div>
        <div class="grid">
            <div class="col-12">
                <div class="w-full">
                    <div v-if="note" class="link_line_action_res_note px-3">
                        <div class="pt-2 pb-3 text-color-black" >
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">Reseravation Note</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onReseravationNote($event, 'note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">Create by:</span><span class="text-500 font-italic"> Adminstrator 09-06-2023 12:30 AM,</span>
                                    <span class="font-italic"> Last Modified:</span><span class="text-500 font-italic"> Adminstrator 09-06-2023 12:30 AM</span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ note }}</div>
                        </div>
                    </div>
                    <div v-else class="link_line_action px-3" @click="onReseravationNote($event, 'note')">
                        <div  class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">Add Reseravation Note</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 pb-0">
                <div class="w-full">
                    <div class="link_line_action_res_note px-3" v-if="housekeeping_note">
                        <div class="pt-2 pb-3 text-color-black" >
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">Housekeeping Note</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onReseravationNote($event, 'housekeeping_note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">Create by:</span><span class="text-500 font-italic"> Adminstrator 09-06-2023 12:30 AM,</span>
                                    <span class="font-italic"> Last Modified:</span><span class="text-500 font-italic"> Adminstrator 09-06-2023 12:30 AM</span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ housekeeping_note }}</div>
                        </div>
                    </div>
                    <div  v-else class="link_line_action px-3" @click="onReseravationNote($event, 'housekeeping_note')" >
                        <div class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">Add Housekeeping Note</span>
                        </div>
                    </div>
                    
                </div>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComOverlayPanelContent width="350px" :loading="saving" @onSave="onSave" @onCancel="onClose">
                <div>
                    <div v-if="dataUpdate.updating == 'note'">
                        <label for="textnote" class="text-lg font-semibold line-height-4">Reservation Note</label><br />
                        <Textarea class="w-full my-2" id="textnote" v-model="dataUpdate.note" rows="5" />
                    </div>
                    <div v-else>
                        <label for="textnote" class="text-lg font-semibold line-height-4">Housekeeping Note</label><br />
                        <Textarea class="w-full my-2" id="textnote" v-model="dataUpdate.housekeeping_note" rows="5" />
                    </div>
                </div>
                <template #footer-right>
                    <div class="flex">
                        <div class="flex align-items-center px-2">
                            <Checkbox v-model="dataUpdate.is_apply_all_stays" :binary="true" inputId="checkapplyall" />
                            <label for="checkapplyall"> Apply all stays ({{ totalStay }})</label>
                        </div>
                        <div class="flex align-items-center px-2" v-if="doctype != 'Reservation'">
                            <Checkbox v-model="dataUpdate.is_apply_reseration" :binary="true" inputId="checkmasterguest" />
                            <label for="checkmasterguest"> Apply Reservation</label>
                        </div>
                    </div>
                </template>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
import { ref, postApi, inject, onMounted } from '@/plugin'
import ComReservationStayPanel from './ComReservationStayPanel.vue';
const props = defineProps({
    doctype: String
})
const reservation = inject('$reservation')
const reservation_stay = inject('$reservation_stay')
const saving = ref(false)
const op = ref()
const housekeeping_note = ref('')
const note = ref('')
const reservationName = ref('')
const docname = ref('')
const totalStay = ref(0)
const dataUpdate = ref({
    doctype: props.doctype,
    name: '',
    reservation: '',
    is_apply_all_stays: false,
    is_apply_reseration: false,
    updating: 'note',
    note: '',
    housekeeping_note: ''
})

function onReseravationNote($event, updating) {
    dataUpdate.value.note = note.value
    dataUpdate.value.housekeeping_note = housekeeping_note.value
    dataUpdate.value.updating = updating
    dataUpdate.value.name = docname.value
    dataUpdate.value.is_apply_all_stays = false
    dataUpdate.value.is_apply_reseration = false
    op.value.toggle($event)
}
function onSave() {
    saving.value = true

    dataUpdate.value.reservation = (dataUpdate.value.is_apply_reseration || dataUpdate.value.is_apply_all_stays) ? reservationName.value : ''
    postApi('reservation.update_note', { data: dataUpdate.value })
        .then((r) => {
            saving.value = false
            if (props.doctype == 'Reservation Stay') {
                reservation_stay.reservationStay = r.message
                updateDisplayNote()
            }
            else if (props.doctype == 'Reservation') {
                reservation.reservation = r.message
                updateDisplayNote()
            }
        }).catch((err) => {
            saving.value = false
        })
}
function onClose() {
    op.value.hide()
}
onMounted(() => {
    updateDisplayNote()
})
function updateDisplayNote() {
    if (props.doctype == 'Reservation Stay') {
        note.value = reservation_stay?.reservationStay?.note || ''
        housekeeping_note.value = reservation_stay?.reservationStay?.housekeeping_note || ''
        reservationName.value = reservation_stay.reservation.name || ''
        docname.value = reservation_stay.reservationStay.name || ''
        totalStay.value = reservation_stay.total_reservation_stay || 0
    }
    else if (props.doctype == 'Reservation') {
        note.value = reservation?.reservation?.note || ''
        housekeeping_note.value = reservation?.reservation?.housekeeping_note || ''
        docname.value = reservation.reservation.name || ''
        reservationName.value = reservation.reservation.name || ''
        totalStay.value = reservation_stay.total_reservation_stay || 0
    }
    onClose()
}
</script>
<style scoped>
.text-color-black {
    color: #495057 !important;
}
.link_line_action_res_note{
  border: 1px dashed #d1d4e5;
  border-radius: 10px;
  padding: 0 5px;
  display: inline-block;
  width: 100%;
  background-color: #fdfdff;
}
</style>