<template>
    <tr v-for="(c, index) in data.changed" :key="index">
        <td>{{ c.property }}</td>
        <td style="background:var(--red-100);"><div v-html="c.original_value"></div></td>
        <td style="background:var(--green-100);"><div v-html="c.new_value"></div></td>
    </tr>
</template>
<script setup>
    import {ref,getApi} from '@/plugin'
    const props = defineProps({
        doctype:String,
        docname:String
    })
    const loading = ref(false)
    const data = ref("ee") 
    if(props.doctype && props.docname){
        loading.value = true
        getApi('reservation.get_audit_trail',{
            doctype: props.doctype,
            docname: props.docname,
            is_last_modified: true
        }).then((r)=>{
            data.value = r.message
            loading.value = false
        }).catch((err)=>{
            loading.value = false
        })
    } 
</script>
<style scoped>
    table {
        border-collapse: collapse;
        border: 1px solid rgba(204, 204, 204, 0.3);
        width: 100%;
    }
    th, td {
        padding: .5rem;
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
 