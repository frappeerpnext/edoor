<template>
    <ComOverlayPanelContent title="Update Reservation Information" :width="isMobile ? '100%' : '50rem'" :loading="isLoading" @onSave="onSave" @onCancel="emit('onClose')">
        <div class="py-2 grid">
            <div class="col-12">
                <label>{{ $t('Res. Date') }} </label><br/>
                <Calendar class="p-inputtext-sm w-full" :selectOtherMonths="true" v-model="data.reservation_date"
                placeholder="Reservation Date" dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear"/>
            </div>
            <div class="col-6">
                <label>{{ $t('Ref. No') }} </label><br/>
                <InputText v-model="data.reference_number" class="w-full"/>
            </div>
            <div class="col-6">
                <label>{{$t('Int. No')}}</label><br/>
                <InputText v-model="data.internal_reference_number" class="w-full"/>
            </div>
            <div v-if="data.reservation_type != 'FIT'" class="col-12">
                <div class="grid">
                    <div class="col-6 lg:col-5">
                        <label>{{$t('Group Name')}}</label><br/>
                        <InputText v-model="data.group_name" class="w-full"/>
                    </div>
                    <div class="col-6 lg:col-5">
                        <label>{{$t('Group Code')}}</label><br/>
                        <InputText v-model="data.group_code" class="w-full"/>
                    </div>
                    <div class="col-12 lg:col-2">
                        <label>{{$t('Group Color')}}</label>
                        <div @click="toggleColor" class="w-full border-blue-100 h-3rem border-round-xl border-1" :style="{background:data.group_color}"></div>
                    </div>
                </div>
            </div>
            
            <div class="col flex gap-3">
                <div class="flex items-center">
                    <template v-if="data.doctype=='Reservation Stay'">
                        <Checkbox inputId="update_to_reservation" v-model="update_to_reservation" :binary="true" />
                        <label for="update_to_reservation" class="cursor-pointer m-auto ps-2">
                            {{$t('Apply change to reservation')}}
                            </label>
                    </template>
                </div>
                <div class="flex items-center">
                    <Checkbox inputId="apply-all-stay" v-model="apply_all_stay" :binary="true" />
                    <label for="apply-all-stay" class="cursor-pointer m-auto ps-2">
                        {{$t(' Apply to all active stays')}}
                       </label>
                </div>
            </div>
        </div>
    </ComOverlayPanelContent>
    <OverlayPanel ref="opColor">
                                    <ComColorPicker v-model="data.group_color" />
                                </OverlayPanel>
</template>     
<script setup>

import { ref, inject, onMounted,postApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const isMobile = ref(window.isMobile)

const moment = inject("$moment")
const emit = defineEmits(['onClose'])
const props = defineProps({
    doctype: String
})
const opColor = ref();
const toggleColor = (event) => {
    opColor.value.toggle(event);
}
const isLoading = ref(false)
const rs = inject('$reservation_stay');
const r = inject('$reservation');
const data = ref({})
const apply_all_stay = ref(false)
const update_to_reservation = ref(false)
onMounted(() => {
    if(props.doctype == 'Reservation Stay'){
        data.value = JSON.parse(JSON.stringify(rs.reservationStay))
    }else{
        data.value = JSON.parse(JSON.stringify(r.reservation))
    }
    data.value.reservation_date = moment(data.value.reservation_date).toDate();
})
 
const onSave = () => {
    isLoading.value = true;
    let doc = JSON.parse(JSON.stringify(data.value))
    doc.reference_number = doc.reference_number || ""
    doc.internal_reference_number = doc.internal_reference_number || ""
    doc.group_code = doc.group_code || ""
    doc.group_name = doc.group_name || ""
    doc.group_color = doc.group_color || ""
    doc.doctype = props.doctype
    if (doc.reservation_date) doc.reservation_date = moment(doc.reservation_date).format("yyyy-MM-DD")

    postApi("reservation.update_reservation_information",{
            doc:doc,
            apply_all_active_stay:apply_all_stay.value,
            update_to_reservation:update_to_reservation.value
            
        }).then((doc) => {
            isLoading.value = false;
            window.postMessage({action:"ReservationList"},"*")
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.postMessage({action:"ReservationDetail"},"*")
        emit("onClose", doc.message)
    }).catch((ex) => {
        isLoading.value = false;
    })
} 
</script>
