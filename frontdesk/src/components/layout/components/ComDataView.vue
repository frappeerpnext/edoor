<template>
   <slot :data="model" >
                {{ model }}
            </slot>

</template>
<script setup>
import { getDocumentList, ref, inject,getDocument ,getData} from "@/plugin"
import { onMounted } from "vue";
const props = defineProps({
    doctype: String,
    docname:String,
    apiUrl:String,
    options: {
        type: Object,
        default: {
            fields: ["name"],
            limit: 20
        }
    },
    classList: {
        type: String,
        default: ''
    }
})
defineExpose({
    loadData 
})

const model = defineModel()
 
async function loadData() {
    if(props.doctype && !props.docname){
        await loadDocumentList();
        return
    }
    
    if(props.doctype && props.docname){
        await loadDocument();
        return
    }
    if(props.apiUrl){
        await loadApiData();
        return
    }

  
}
async function loadDocumentList() {
    
    const res = await getDocumentList(props.doctype, props.options);
    if (res.data) {
        model.value = res.data;
    }
}

async function loadDocument() {
    
    const res = await getDocument(props.doctype, props.docname);
    if (res.data) {
        model.value = res.data;
    }
}
async function loadApiData() {
    
    const res = await getData(props.apiUrl, props.options);
    if (res.data) {
        model.value = res.data;
    }
}

onMounted(async () => {
    await loadData();

})
</script>