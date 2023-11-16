<template>
    <div class="mt-1 grid px-1">
        <div class="col-12 flex border-b justify-content-between" v-for="(i, index) in doc.slice(0, limitview)" :key="index">
    <div>{{ i.name }}</div>
    <span class="px-3 me-2 border-round-lg" :style="{ background: i.color }"></span>
</div>
<div @click="toggleShowAll" v-if="doc.length > 5" class="flex justify-content-end w-full">
    <Button :label="showAll ? 'Show Less' : 'View More'" class="mt-2 dialog_btn_transform conten-btn" text/>
</div>

    </div>
</template>
<script setup>
import { ref, inject,getDocList, onMounted  } from "@/plugin"
const doc = ref([]);
let limitview = 5;
onMounted(()=>{
    getDocList("Reservation Color Code", {
        fields: ["name","color"],
        limit:1000,
        orderBy: {
			field: "creation",
			order:"DESC",
		},
    }).then(data=>{
        doc.value = data
    })
})
const showAll = ref(false);

const toggleShowAll = () => {
  showAll.value = !showAll.value;
  limitview = showAll.value ? 1000 : 5 ;
};

</script>