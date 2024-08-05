<template>

  <ol-map style="height: 100vh">
    <ol-view
      ref="view"
      :center="center"
      :zoom="zoom"
      :projection="projection"
    />

    <ol-tile-layer>
      <ol-source-osm />
    </ol-tile-layer>

    <ol-overlay
      :position="item.position"
      v-for="(item, index) in list" :key="index"
 
      :autoPan="true"
    > <draggable-resizable-vue
    v-model:x="item.x"
    v-model:y="item.y"
    v-model:h="item.height"
    v-model:w="item.width"
    v-model:active="item.isActive"
 >
      <div class="overlay-content">
        {{ item }}
      </div>
    </draggable-resizable-vue>
    </ol-overlay>
  </ol-map>
</template>

<script setup>
import { ref } from "vue";


const element = ref({
  x: 20,
  y: 20,
  width: 200,
  height: 200,
  isActive: false,
})

const center = ref([40, 40]);
const projection = ref("EPSG:4326");
const zoom = ref(8);
const offset = ref(0);
const list = ref([{"title":"Mr. Jhan",position:[1 + 37.9, 40.1], x: 20,
  y: 20,
  width: 200,
  height: 200,
  isActive: false}]);

 
</script>

<style scoped>
.overlay-content {
  background: #efefef;
  box-shadow: 0 5px 10px rgb(2 2 2 / 20%);
  padding: 10px 20px;
  font-size: 16px;
  color: black;
}
</style>

 