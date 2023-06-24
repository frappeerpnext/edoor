<template>
    <div>
        <div class="at-update-row" v-if="!loading"> 
            <h2 class="h-title mb-3">{{ data.deleted_doctype }}</h2>
            <table class="w-full">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <template v-for="(i, index) in deleteData" :key="index">
                        <tr v-if="show(i.property)"> 
                                <td>
                                    {{ getTitle(i.property) }}
                                </td>
                                <td style="background:var(--red-100)">  
                                    {{ i.value }}
                                </td> 
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
    import {ref, getApi} from '@/plugin'
    const props = defineProps({
        type: 'added',  // added or removed
        data: Object
    })
    const loading = ref(true)
    const deleteData = ref([])
    const meta = ref()
    if(props.data){
        loading.value = true
        Object.entries(JSON.parse(props.data.data)).forEach(([key, value]) => { 
            deleteData.value.push({property: key, value: value})
        });
        getApi('frontdesk.get_meta',{doctype: props.data.deleted_doctype}).then((r)=>{
            meta.value = r.message
            loading.value = false
        }).catch(()=>{
            loading.value = false
        })
    }
    function show(key){
        if(meta.value){
            const metaData = meta.value.fields.find((r)=>r.fieldname == key)
            if(metaData?.hidden){
                return false
            }
            return true
        }
    }
    function getTitle(key){
        if(meta.value){
            const metaData = meta.value.fields.find((r)=>r.fieldname == key)
            if(metaData?.label){
                return metaData?.label
            }
            return key
        }
    }
</script>
<style scoped>
.at-update-row table tbody tr td.nth-2_td{
    padding: 0;
    border: none;
}
td.nth-2_td table tr:first-child td:first-child{
    border-top: none;
}
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