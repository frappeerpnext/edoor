<template>
    <div v-if="rs.reservation">
        <div class="grid">
            <div class="col-12">
                <div class="w-full">
                    <div v-if="rs.reservation.note" class="link_line_action_res_note px-3">
                        <div class="pt-2 pb-3 text-color-black">
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">Reseravation Note</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem"
                                        @click="onReseravationNote($event, 'note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">Last Modified: </span><span class="text-500 font-italic"> {{
                                        rs.reservation.note_by }} {{ gv.datetimeFormat(rs.reservation.note_modified)
    }}</span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ rs.reservation.note }}</div>
                        </div>
                    </div>
                    <div v-else class="link_line_action px-3" @click="onReseravationNote($event, 'note')">
                        <div class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">Add Reseravation Note</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 pb-0">
                <div class="w-full">
                    <div class="link_line_action_res_note px-3" v-if="rs.reservation.housekeeping_note">
                        <div class="pt-2 pb-3 text-color-black">
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">Housekeeping Note</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem"
                                        @click="onReseravationNote($event, 'housekeeping_note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">Last Modified: </span><span class="text-500 font-italic"> {{
                                        rs.reservation.housekeeping_note_by }} {{
        gv.datetimeFormat(rs.reservation.housekeeping_note_modified) }}</span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ rs.reservation.housekeeping_note }}</div>
                        </div>
                    </div>
                    <div v-else class="link_line_action px-3" @click="onReseravationNote($event, 'housekeeping_note')">
                        <div class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">Add Housekeeping Note</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComOverlayPanelContent width="100%" :loading="saving" @onSave="onSave" @onCancel="onClose">
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
                            <label for="checkapplyall"> Apply all stays ({{ rs.reservation.total_active_reservation_stay
                            }})</label>
                        </div>
                    </div>
                </template>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
import { ref, postApi, inject } from '@/plugin'
const rs = inject('$reservation')
const gv = inject('$gv')
const saving = ref(false)
const op = ref()

const dataUpdate = ref({
    doctype: "Reservation",
    name: '',
    reservation: '',
    is_apply_all_stays: false,
    is_apply_reseration: false,
    updating: 'note',
    note: '',
    note_by: '',
    note_modified: '',
    housekeeping_note: '',
})

function onReseravationNote($event, updating) {
    const selected = JSON.parse(JSON.stringify(rs.reservation))
    dataUpdate.value.note = selected.note
    dataUpdate.value.housekeeping_note = selected.housekeeping_note
    dataUpdate.value.updating = updating
    dataUpdate.value.name = rs.reservation.name,
        dataUpdate.value.reservation = rs.reservation.name,
        dataUpdate.value.is_apply_all_stays = false
    op.value.toggle($event)
}
function onSave() {
    saving.value = true
    postApi('reservation.update_note', { data: dataUpdate.value })
        .then((r) => {
            saving.value = false
            if (dataUpdate.value.is_apply_all_stays) {
                rs.reservationStays.forEach(stay => {
                    window.postMessage({ action: "ReservationStayDetail" }, "*")
                });
            }
            window.postMessage({ action: "ReservationDetail" }, "*")
            op.value.hide()
        }).catch((err) => {
            saving.value = false
        })
}

function onClose() {
    op.value.hide();
}
</script>
<style scoped>
.text-color-black {
    color: #495057 !important;
}

.link_line_action_res_note {
    border: 1px dashed #d1d4e5;
    border-radius: 10px;
    padding: 0 5px;
    display: inline-block;
    width: 100%;
    background-color: #fdfdff;
}
</style>