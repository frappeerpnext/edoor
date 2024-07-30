<template>
  <div id="map" style="height: 500px;">
    <ol-map>
      <ol-view
        :center="center"
        :zoom="zoom"
      ></ol-view>

      <ol-layer-tile>
        <ol-source-osm></ol-source-osm>
      </ol-layer-tile>
    </ol-map>
  </div>
</template>

<script setup>
import 'vue3-openlayers/dist/vue3-openlayers.css';
import { ref } from 'vue';
import { useGeographic } from 'ol/proj';

// Ensure coordinates are in the geographic (EPSG:4326) projection
useGeographic();

const center = ref([104.991531, 12.565679]); // Longitude and latitude of Cambodia
const zoom = ref(6);
</script>
