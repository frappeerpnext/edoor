<template>

    <ComRepeatView ref="repeatView" classList="flex flex-col gap-2" v-model:items="items" doctype="List Filter" :options="{
        fields: ['name', 'filter_name', 'for_user', 'custom_view_filters'],
        filters: [['reference_doctype', '=', doctype]]
    }">
        
        <template #default="{ item, index }">
            <Button icon="pi pi-times" iconPos="right" iconClass="text-xs" class="w-full border-0 text-left saved_filter_button"
                style="height:30px !important; background: rgb(99 102 241 / 24%);color:#6366f1;"
                :label="item.filter_name" @click="onOpenView(item)"></Button>
        </template>
    </ComRepeatView>
    
</template>
<script setup>
import { useRouter, ref } from "@/plugin"
import { onMounted } from "vue"
import { useApp } from "@/hooks/useApp";
const router = useRouter()
const props = defineProps({
    doctype: String,
    options: Object,
    router_name: String
})
const items = defineModel([])
const repeatView = ref(null)
defineExpose({
    reloadData 
})
function reloadData(){
   
    repeatView.value.loadData();

   
}

function onOpenView(v) {
    router.push({ name: props.router_name, hash: "#" + v.name })
}


</script>
<style>
    .saved_filter_button .p-button-label {
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 235px;
        display: inline-block;
    }
</style>