<template>
    <ComDialogContent hideButtonOK>
    <div> 
        <div class="at-add" v-if="data?.added || data?.removed">
            <div v-if="data?.added">
                <ComAuditTrailDetailAddRemoveRow :data="data.added" type="added" />
            </div>
            <div v-else>
                <ComAuditTrailDetailAddRemoveRow :data="data.removed" type="removed" />
            </div>
        </div>
        <div class="changed" v-if="data?.changed">
            <h2>Values Changed</h2>
            <table class="w-full">
                <thead>
                    <tr>
                        <td>Property</td>
                        <td>Original Value</td>
                        <td>New Value</td>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(c, index) in data.changed" :key="index">
                        <td>{{ c.property }}</td>
                        <td class="bg-red-300"><div v-html="c.original_value"></div></td>
                        <td class="bg-green-300"><div v-html="c.new_value"></div></td>
                    </tr>
                </tbody>
            </table>
        </div> 
    </div>
</ComDialogContent>
</template>
<script setup>
import ComAuditTrailDetailAddRemoveRow from './ComAuditTrailDetailAddRemoveRow.vue';
const emit = defineEmits('onClose')
const props = defineProps({
    data: Object
})

function onClose(){
    emit('onClose')
}
</script>
<style lang="">
    
</style>