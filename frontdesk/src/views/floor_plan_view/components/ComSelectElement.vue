<template>
  <ComDialogContent
    hideButtonClose
    :titleButtonOK="Ok"
    :hideIcon="false"
    :loading="loading"
  >
    <div class="element">
      <div class="flex" v-for="(d, index) in datas" :key="index" style="height: 100px;width:150px;">
       
        <div :id="'el_' + d.name" v-html="d.custom_shape"></div>
        <Button label="Select Me" @click="onSelect('#el_' + d.name)" />
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup>
import Button from "primevue/button";

import { ref, inject, getDocList } from "@/plugin";

const loading = ref(false);
const dialogRef = inject("dialogRef");
const datas = ref([]);

function onSelect(id) {
  const element = document.querySelector(id);
  console.log(element);
  dialogRef.value.close(element);
}

getDocList("Floor Plant Element", {
  fields: ["category", "name", "custom_shape", "photo"],
}).then((doc) => {
  datas.value = doc;
  console.log(doc);
});
</script>
