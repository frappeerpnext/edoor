<template> 
    <ComOverlayPanelContent style="min-width:15rem;" title="Change Rate Type" :loading="isLoading" @onSave="onSave"
        @onCancel="emit('onClose')">
        <div class="my-2" style="min-width:10rem;">
            <ComSelect v-model="rateType" placeholder="Rate Type" doctype="Rate Type" class="auto__Com_Cus w-full"  @onSelected="onRateTypeChange"  />
            <div class="flex gap-2 flex-col mt-3">
                <div class="flex gap-2" v-if="!hideApplyAll">
                    <Checkbox inputId="apply-all" v-model="applyToAllStay" :binary="true" />
                    <label for="apply-all" class="cursor-pointer">Apply to All Stay 
                        <span>
                        ({{ rs.reservation.total_active_reservation_stay - rs.reservation.total_checked_out }})
                    </span>
                    </label>
                </div>
                <Message severity="warn" v-if="rate_type_data?.allow_user_to_edit_rate==0">This rate this is not allow to change rate. Room rate will be set to <CurrencyFormat :value="0" /> </Message>

                <div class="flex gap-2" v-if="rate_type_data?.allow_user_to_edit_rate==1">
                    <Checkbox inputId="apply-all-stay" v-model="regenerateNewRate" :binary="true" />
                    <label for="apply-all-stay" class="cursor-pointer">Regenerate New Rate</label>
                </div>
                <Message severity="warn" v-if="regenerateNewRate">Generate new rate will be affect only active reservation and future stay</Message>
            </div>
            <div class="flex gap-2 flex-col mt-2" v-if="rate_type_data?.tax_rule">
                    <div>
                        <Checkbox v-model="rate_type_data.is_rate_include_tax" :binary="true" :trueValue="1"
                            :falseValue="0" />
                        <label> Is rate include tax</label>
                    </div>
                    <div v-if="rate_type_data.tax_rule.tax_1_rate">
                        <Checkbox v-model="rate_type_data.tax_1_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_1_rate" :falseValue="0" />
                        <label> {{ rate_type_data.tax_rule.tax_1_name }} {{ rate_type_data.tax_rule.tax_1_rate }}%</label>

                    </div>
                    <div v-if="rate_type_data.tax_rule.tax_2_rate">
                        <Checkbox v-model="rate_type_data.tax_2_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_2_rate" :falseValue="0" />
                        <label> {{ rate_type_data.tax_rule.tax_2_name }} {{ rate_type_data.tax_rule.tax_2_rate }}%</label>

                    </div>
                    <div v-if="rate_type_data.tax_rule.tax_3_rate">
                        <Checkbox v-model="rate_type_data.tax_3_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_3_rate" :falseValue="0" />
                        <label> {{ rate_type_data.tax_rule.tax_3_name }} {{ rate_type_data.tax_rule.tax_3_rate }}%</label>

                    </div>
                </div>
           
        </div>
    </ComOverlayPanelContent>
</template>     
<script setup>
import { ref, inject, postApi,getApi } from "@/plugin"
import ComOverlayPanelContent from '@/components/form/ComOverlayPanelContent.vue';
import Checkbox from 'primevue/checkbox';
import Message from 'primevue/message';
const rs = inject('$reservation_stay');
const emit = defineEmits(['onClose', 'onSave'])
const rate_type_data = ref()
const onRateTypeChange = (rate_type) => {
    if (rate_type) {
        getApi("utils.get_rate_type_info", { name: rate_type })
            .then((result) => {
                rate_type_data.value = result.message
                if (result.message?.tax_rule) {
                    rate_type_data.value.tax_rule_name = result.message.tax_rule.name
                    rate_type_data.value.is_rate_include_tax = result.message.tax_rule.is_rate_include_tax
                    rate_type_data.value.tax_1_rate = result.message.tax_rule.tax_1_rate
                    rate_type_data.value.tax_2_rate = result.message.tax_rule.tax_2_rate
                    rate_type_data.value.tax_3_rate = result.message.tax_rule.tax_3_rate
                    rate_type_data.value.allow_user_to_edit_rate = result.message.allow_user_to_edit_rate
                } else {
                    clearRateTypeTax()
                }
            })
    } else {
        clearRateTypeTax()
    }
}

function clearRateTypeTax() {
    rate_type_data.value.tax_rule = ""
    rate_type_data.value.tax_1_rate = 0
    rate_type_data.value.tax_2_rate = 0
    rate_type_data.value.tax_3_rate = 0
}

const props = defineProps({
    rate_type: {
        type: String,
        default: ''
    },
    reservation: {
        type: String,
        default: ''
    },
    update_reservation: {
        type:Boolean,
        default: false
    },
    reservation_stay: {
        type: String,
        default: ''
    },
    hideApplyAll: {
        type: Boolean,
        default: false
    }
})

const rateType = ref(props.rate_type);
const applyToAllStay = ref(false);
const regenerateNewRate = ref(false);
const property = JSON.parse(localStorage.getItem("edoor_property"))
const isLoading = ref(false)

function onSave() {
    isLoading.value = true

    postApi('reservation.change_rate_type', {
        property: property.name,
        reservation_stay: props.reservation_stay,
        reservation: props.reservation,
        rate_type: rateType.value,
        apply_to_all_stay: applyToAllStay.value,
        regenerate_new_rate: regenerateNewRate.value,
        update_reservation: props.update_reservation
    })
        .then((result) => {
            isLoading.value = false
            emit('onSave', result.message)
            window.socket.emit("ReservationStayList", { property: window.property_name })
            
         
        })
        .catch((error) => {
            isLoading.value = false
        })
}
</script>
