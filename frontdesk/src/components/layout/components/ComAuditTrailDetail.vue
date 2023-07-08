<template>
    <ComDialogContent hideButtonOK>
        <ComPlaceholder :loading="loading" :is-not-empty="true">
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
                    <h2 class="h-title mb-3">Values Changed</h2>
                    <table class="w-full" border="1">
                        <thead>
                            <tr>
                                <th>Property</th>
                                <th>Original Value</th>
                                <th>New Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="(c, index) in data.changed" :key="index">
                                <td>{{ c.property }}</td>
                                <td style="background:var(--red-100);"><div v-html="c.original_value"></div></td>
                                <td style="background:var(--green-100);"><div v-html="c.new_value"></div></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <ComAuditTrailDetailChangedRow v-else-if="data.row_changed" :data="data"/>
                <div v-if="list">
                    <ComAuditTrailDetailDeletedDoc :data="list"/>
                </div>
                <div v-if="data.comment_type == 'Created'" class="created">
                    <ComAuditTrailDetailCreatedDoc :data="data"/>
                </div>
            </div>
        </ComPlaceholder>
    </ComDialogContent>
</template>
<script setup>
import {ref, getDoc} from '@/plugin'
import ComAuditTrailDetailAddRemoveRow from './ComAuditTrailDetailAddRemoveRow.vue';
import ComAuditTrailDetailDeletedDoc from './ComAuditTrailDetailDeletedDoc.vue';
import ComAuditTrailDetailCreatedDoc from './ComAuditTrailDetailCreatedDoc.vue';
import ComAuditTrailDetailChangedRow from './ComAuditTrailDetailChangedRow.vue';
const emit = defineEmits('onClose')
const props = defineProps({
    data: Object
})
const loading = ref(false)
const list = ref(null)
if(props.data){
    if(props.data.comment_type == 'Deleted Folio'){
        loading.value = true
        const content = props.data.content.split('|')
        getDoc('Deleted Document', content[4]).then((r)=>{
            list.value = r
            loading.value = false
        }).catch(()=>{
            loading.value = false
        })
    }
}

function onClose(){
    emit('onClose')
}
</script>
<style scoped>
    .h-title{
        font-weight: 600;
        font-size: 1.125rem;
    }
    table {
        border-collapse: collapse;
        border: 1px solid rgba(204, 204, 204, 0.3);
        width: 100%;
    }
    th, td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid rgba(204, 204, 204, 0.3);
    }
    th {
        border-top: 1px solid rgba(204, 204, 204, 0.3);
        border-bottom: 2px solid rgba(204, 204, 204, 0.3);
        border-left: 1px solid rgba(204, 204, 204, 0.3);
        font-weight: normal;
    }
    td{
        border-top: 1px solid rgba(204, 204, 204, 0.3);
        border-bottom: 1px solid rgba(204, 204, 204, 0.3);
        border-left: 1px solid rgba(204, 204, 204, 0.3);
        vertical-align: baseline;
    }
    tr:last-of-type td {
        border-bottom: none;
    }
</style>