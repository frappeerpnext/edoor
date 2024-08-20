<template>
  <ComDialogContent
    hideButtonClose
    :titleButtonOK="Ok"
    :hideIcon="false"
    :loading="loading"
  >
    <div class="card">
      <Fieldset
        class="mt-2"
        v-for="(d, index) in Categories"
        :key="index"
        :legend="d"
      >
        <div class="element cursor-pointer grid">
          <div
            class="flex"
            v-for="(d, index) in datas.filter((r) => r.category == d)"
            :key="index"
            style="height: 100px; width: 150px"
          >
            <div
              style="width: 100px; height: 100px"
              :id="'el_' + d.name"
              @click="onSelect('#el_' + d.name)"
              v-html="d.custom_shape"
            ></div>
          </div>
        </div>
      </Fieldset>
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

  dialogRef.value.close(element);
}
const Categories = ref([]);
getDocList("Floor Plant Element", {
  fields: ["category", "name", "custom_shape", "photo"],
}).then((doc) => {
  datas.value = doc;
  Categories.value = [...new Set(doc.map((i) => i.category))];
});
</script>
