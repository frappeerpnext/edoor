<template>
    <Stack row gap="4px">
 
        <InputText v-if="!hideSearchField" class="px-2 py-1" v-model="filter.keyword" variant="filled" placeholder="Search" size="small" v-debounce="onSearch" style="height: 30px !important;"/>
        <template v-for="(f, index) in filters" :key="index">
            <ComFilterInput-ata v-if="f.fieldtype=='Data'" :option="f"  @onFilter="onFilter"   :defaultValue="filter[f.fieldname]"/>
            <ComFilterInputLink v-if="f.fieldtype=='Link'" :option="f"  @onFilter="onFilter"   :defaultValue="filter[f.fieldname]" :operator="f.operator" :optionValue="f.optionValue"/> 
            <ComFilterInputDate v-if="f.fieldtype=='Date'" :option="f"  @onFilter="onFilter"   :defaultValue="filter[f.fieldname]"/>
            <ComFilterInputSelect v-if="f.fieldtype=='Select'" :option="f"  @onFilter="onFilter" :defaultValue="filter[f.fieldname]"  />
            <ComFilterInputNumber v-if="['Currency','Int','Float'].includes(f.fieldtype)" :option="f"  @onFilter="onFilter"   :defaultValue="filter[f.fieldname]"/>
        </template>
        <Button class="border-none content_btn_b h-full px-2 py-1" label="Clear Filter" @click="onClearFilter" style="height: 30px !important;" severity="warning"></Button>
        

    </Stack>
   
</template>
<script setup>
import {ref,useRouter} from "@/plugin"
import ComFilterInputData from "@/components/document/components/ComFilterInputData.vue"
import ComFilterInputLink from "@/components/document/components/ComFilterInputLink.vue"
import ComFilterInputDate from "@/components/document/components/ComFilterInputDate.vue"
import ComFilterInputSelect from "@/components/document/components/ComFilterInputSelect.vue"
import ComFilterInputNumber from "@/components/document/components/ComFilterInputNumber.vue"
const props = defineProps({
    filters:Object,
    hideSearchField:Boolean
})

const router = useRouter();

const emit = defineEmits()
const filter = defineModel('filter', { type:Object, default: {keyword:""} })

function  onSearch(){
    
    emit("onSearch",filter.value);
}

function onFilter(f){
    if((typeof f[0]) =="string"){
        if(f[2]){
            filter.value[f[0]] = f;
        
        }else {
            delete filter.value[f[0]]
        }
    }else {
        filter.value[f[0][0]] = f;
    }
  
    emit("onSearch",filter.value);
}

function onClearFilter(){
    filter.value = { "keyword": "" }
    emit("onSearch", { "keyword": "" });
    const url =window.location;
const parsedUrl = new URL(url);

// Extract path from the URL
const path = parsedUrl.pathname;
 
router.push(path);
}

</script>