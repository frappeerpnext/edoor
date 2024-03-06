<template>
    <div v-if="rs.reservationStay">
        <div class="grid">
            <div class="col-12">
                <div class="w-full">
                    <div v-if="rs.reservationStay.note" class="link_line_action_res_note px-3">
                        <div class="pt-2 pb-3 text-color-black">
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">{{$t('Reseravation Note')}}</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem"
                                        @click="onReseravationNote($event, 'note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">{{$t('Last Modified')}}: </span><span class="text-500 font-italic"> {{
                                        rs.reservationStay.note_by.split("@")[0] }} {{ gv.datetimeFormat(rs.reservationStay.note_modified)}}
                                    </span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ rs.reservationStay.note }}</div>
                        </div>
                    </div>
                    <div v-else class="link_line_action px-3" @click="onReseravationNote($event, 'note')">
                        <div class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">{{$t('Add Reseravation Note')}}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 pb-0">
                <div class="w-full">
                    <div class="link_line_action_res_note px-3" v-if="rs.reservationStay.housekeeping_note">
                        <div class="pt-2 pb-3 text-color-black">
                            <div class="">
                                <div class="flex justify-content-between flex-wrap">
                                    <span class="text-lg font-semibold line-height-4">{{$t('Housekeeping Note')}}</span>
                                    <Button text icon="pi pi-file-edit" class="w-1rem h-1rem"
                                        @click="onReseravationNote($event, 'housekeeping_note')"></Button>
                                </div>
                                <div class="text-sm">
                                    <span class="font-italic">{{$t('Last Modified')}}: </span><span class="text-500 font-italic"> {{
                                        rs.reservationStay.housekeeping_note_by.split("@")[0]  }} {{
        gv.datetimeFormat(rs.reservationStay.housekeeping_note_modified) }}</span>
                                </div>
                            </div>
                            <hr class="my-2">
                            <div class="text-color wrap__sp_not">{{ rs.reservationStay.housekeeping_note }}</div>
                        </div>
                    </div>
                    <div v-else class="link_line_action px-3" @click="onReseravationNote($event, 'housekeeping_note')">
                        <div class="flex justify-center items-center my-3">
                            <ComIcon icon="iconNoteBlue" class="me-2" style="height: 16px;" />
                            <span class="text-xl">{{$t('Add Housekeeping Note')}}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComOverlayPanelContent width="100%" :loading="saving" @onSave="onSave" @onCancel="onClose">
                <div>
                    <div v-if="dataUpdate.updating == 'note'">
                        <label for="textnote" class="text-lg font-semibold line-height-4">{{$t('Reservation Note')}}</label><br />
                        <Textarea class="w-full my-2" id="textnote" v-model="dataUpdate.note" rows="5" />
                    </div>
                    <div v-else>
                        <label for="textnote" class="text-lg font-semibold line-height-4">{{$t('Housekeeping Note')}}</label><br />
                        <Textarea class="w-full my-2" id="textnote" v-model="dataUpdate.housekeeping_note" rows="5" />
                    </div>
                </div>
                <template #footer-right>
                    <div class="block lg:flex">
                        <div class="flex align-items-center px-2">
                            <Checkbox v-model="dataUpdate.is_apply_all_stays" :binary="true" inputId="checkapplyall" />
                            <label for="checkapplyall"> {{$t('Apply all stays')}}  ({{ rs.reservation.total_active_reservation_stay
                            }})</label>
                        </div>
                        <div class="flex align-items-center px-2">
                            <Checkbox v-model="dataUpdate.is_apply_reseration" :binary="true" inputId="checkmasterguest" />
                            <label for="checkmasterguest">{{$t('Apply Reservation')}} </label>
                        </div>
                    </div>
                </template>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
import { ref, postApi, inject } from '@/plugin'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const rs = inject('$reservation_stay')
const gv = inject('$gv')
const saving = ref(false)
const op = ref()


const dataUpdate = ref({
    doctype: "Reservation Stay",
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

function onClose() {
    op.value.hide();
}
function onReseravationNote($event, updating) {
    const selected = JSON.parse(JSON.stringify(rs.reservationStay))
    dataUpdate.value.note = selected.note
    dataUpdate.value.housekeeping_note = selected.housekeeping_note
    dataUpdate.value.updating = updating
    dataUpdate.value.name = rs.reservationStay.name,
        dataUpdate.value.is_apply_all_stays = false
    dataUpdate.value.is_apply_reseration = false
    op.value.toggle($event)
}
function onSave() {
    saving.value = true
    dataUpdate.value.reservation = (dataUpdate.value.is_apply_reseration || dataUpdate.value.is_apply_all_stays) ? rs.reservationStay.reservation : ''
 
    postApi('reservation.update_note', { data: dataUpdate.value })
        .then((r) => {
            saving.value = false
            if(dataUpdate.value.is_apply_all_stays){
                rs.reservationStay.note = r.message.note
                rs.reservationStay.note_by = r.message.note_by
                rs.reservationStay.note_modified = r.message.note_modified
                rs.reservationStay.housekeeping_note = r.message.housekeeping_note
                rs.reservationStay.housekeeping_note_by = r.message.housekeeping_note_by
                rs.reservationStay.housekeeping_note_modified = r.message.housekeeping_note_modified
                rs.reservationStayNames.forEach(stay => {
                    stay.name = r.message.name
                    
                });
   
            }else{
                rs.reservationStay.note = r.message.note
                rs.reservationStay.note_by = r.message.note_by
                rs.reservationStay.note_modified = r.message.note_modified
                rs.reservationStay.housekeeping_note = r.message.housekeeping_note
                rs.reservationStay.housekeeping_note_by = r.message.housekeeping_note_by
                rs.reservationStay.housekeeping_note_modified = r.message.housekeeping_note_modified
            }
            if(dataUpdate.value.is_apply_reseration){
                rs.reservationStay.note = r.message.note
                rs.reservationStay.note_by = r.message.note_by
                rs.reservationStay.note_modified = r.message.note_modified
                rs.reservationStay.housekeeping_note = r.message.housekeeping_note
                rs.reservationStay.housekeeping_note_by = r.message.housekeeping_note_by
                rs.reservationStay.housekeeping_note_modified = r.message.housekeeping_note_modified
                rs.reservation.name = r.message.name
            }
            
            
            op.value.hide()
            
        }).catch((err) => {
            saving.value = false
        })
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
}</style>