<template>
    <div>
        {{ data }}
    </div>
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
            console.log(r.message)
            loading.value = false
        }).catch((err)=>{
            loading.value = false
        })
    } 
</script>
 