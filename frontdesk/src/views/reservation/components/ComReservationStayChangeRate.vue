<template> 
    <ComOverlayPanelContent hideButtonOK style="min-width:15rem;" title="Change Rate" @onCancel="$emit('onClose')">
        <div class="rte_message">
            <Message>If you change room rate here. <br/>This room will stop automatically get rate from rate plan. <br/>
            To use rate from Rate Plan, click on Reverse Button
            </Message>
        </div>
        <div class="flex gap-2 mb-2 mt-2">
            <div class="ch__rate_nres relative border-round-lg overflow-hidden">
                <div @click="$emit('onUseRatePlan')" v-tooltip.top="'Reverse to Rate Plan'" class="cursor-pointer absolute h-full w-3rem border-y-1 border-round-y border-round-left border-left-1" style="background: var(--bg-input-field);border-color: #a0bde0;">
                    <div class="translate-y-2/4 text-center">
                        <i class="pi pi-replay text-xl text-dark font-bold"></i>
                    </div>
                </div>
                <InputNumber class="text-right" v-model="rate" :min="0"/>
            </div>
        </div>
        <template #footer-right>
            <Button @click="$emit('onChangeRate')" icon="pi pi-file-edit" label="Update New Rate" class="border-none cursor-pointer"/>
        </template>
    </ComOverlayPanelContent>
</template>
<script setup>
    import {ref, computed} from 'vue'
    const emit = defineEmits(['update:modelValue'])
    const props = defineProps({
        modelValue: Number,
        default: 0
    })
    let rate = computed({
        get(){
            return props.modelValue
        },
        set(newValue){
            emit('update:modelValue', newValue)
            return newValue
        }
    })
</script>
<style scope>
.rte_message .p-message{
    margin-top: .5rem;
    margin-bottom: 1rem;
}
</style>