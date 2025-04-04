<template>
    <div :class="classList">

        <template v-for="(item, index) in items" :key="index">
            <slot :item="item" :index="index">
                {{ item.name }}
            </slot>
        </template>
    </div>



</template>
<script setup>
import { getDocumentList, ref, inject } from "@/plugin"
import { onMounted } from "vue";
const props = defineProps({
    doctype: String,
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

const items = defineModel("items")
 
async function loadData() {
    
    const res = await getDocumentList(props.doctype, props.options);
    if (res.data) {
        items.value = res.data;
    }
}

onMounted(async () => {
    await loadData();;

})
</script>