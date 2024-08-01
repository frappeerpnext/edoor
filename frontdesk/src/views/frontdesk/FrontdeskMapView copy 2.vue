<template>
  
  <ComFrontDeskLayout :title="$t('Map View')">
    <!-- Openlayer Map -->
    <ol-map style="height: 100vh" 
    @click="handleMapClick"
    >
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
        v-for="(province, index) in provinces"
        :key="index"
        :position="[province.longitude + offset, province.latitude]"
         positioning="center-center"
      >
        <div class="overlay-content" @click="handleOverlayClick">
          <div

            class="pin-marker"
            @mouseover="(event) => showTooltip(event, province)"
            @mouseleave="hideTooltip"
          >
            <!-- SVG Icon as Pin Marker with dynamic fill color -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 384 512"
              :style="{ fill: getPinColor(province.population) }"
              class="svg-pin"
            >
              <path
                d="M384 192c0 87.4-117 243-168.3 307.2c-12.3 15.3-35.1 15.3-47.4 0C117 435 0 279.4 0 192C0 86 86 0 192 0S384 86 384 192z"
              />
            </svg>
            <!-- Label inside pin -->
            <div class="pin-label">
              {{ province.label }}
            </div>
          </div>
        </div>
      </ol-overlay>
    </ol-map>
  </ComFrontDeskLayout>
</template>
<script setup>
import { ref,h } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComMapViewTooltip from "@/views/frontdesk/components/ComMapViewTooltip.vue";
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
import { useTippy } from 'vue-tippy'
// Openlayer

const center = ref([104.991, 12.5657]); // Center on Cambodia
const projection = ref("EPSG:4326");
const zoom = ref(3.5);
const offset = ref(0);

const tooltipIndex = ref(null);

function  handleOverlayClick(){
  alert("this is over lay click")
}
const handleMapClick = (event) => {
  // Get the coordinate where the click happened
  const mapCoordinate = event.coordinate;
  console.log('Map clicked at:', mapCoordinate);

  // You can transform the coordinate if needed
  const lonLatCoordinate = transform(mapCoordinate, 'EPSG:3857', 'EPSG:4326');
  console.log('Map clicked at (lon, lat):', lonLatCoordinate);

  // You can add logic here to handle the map click, such as adding a marker
};


const provinces = ref([
  {
    label: "1",
    name: "Phnom Penh",
    population: "2,280,000",
    area: "678",
    latitude: 12.5657,
    longitude: 104.991,
  },
  {
    label: "5",
    name: "thailan",
    population: "2,280,000",
    area: "678",
    latitude: 15.8700,
    longitude: 100.9925,
  },
  {
    label: "45",
    name: "austra",
    population: "2,280,000",
    area: "678",
    latitude:  -24.040006426735218,
    longitude:  135.60985529465643
  },
  {
    label: "45",
    name: "japan",
    population: "2,280,000",
    area: "678",
    latitude:   36.128148764327356,
    longitude:138.07695898731566
  },
]);

function showTooltip(event,data) {
  useTippy(event.target.parentNode, {
      content: h(ComMapViewTooltip, { data: data }),
      placement: "top",
      followCursor: true,
  })
  return
}

function hideTooltip() {
  tooltipIndex.value = null;
}



function getPinColor(population) {
  const pop = parseInt(population.replace(/,/g, ""), 10); // Remove commas and convert to number

  if (pop > 500000) return "green"; // High population
  if (pop > 100000) return "gold"; // Medium population
  return "red"; // Low population
}
</script>

<style scoped>
.overlay-content {
  padding: 10px 20px;
  font-size: 16px;
  color: black;
}

.pin-marker {
  position: relative; /* To position the tooltip */
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer; /* Show pointer cursor */
}

.svg-pin {
  width: 40px; /* Increased size of pin */
  height: 40px; /* Increased size of pin */
  transition: transform 0.3s ease, fill 0.3s ease; /* Smooth scale and color transition */
}

.pin-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white; /* Change color if needed */
  font-size: 14px; /* Adjust font size */
  font-family: "Arial", sans-serif; /* Change font family */
  font-weight: bold;
  z-index: 1; /* Ensure the label is above the SVG */
  text-align: center;
}
 
</style>
