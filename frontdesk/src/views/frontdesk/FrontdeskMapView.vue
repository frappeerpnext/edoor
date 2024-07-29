<template>
  <ol-map ref="map" style="height: 100vh" @pointermove="handlePointerMove">
    <ol-view
      ref="view"
      :center="center"
      :rotation="rotation"
      :zoom="zoom"
      :projection="projection"
      @change:center="centerChanged"
      @change:resolution="resolutionChanged"
      @change:rotation="rotationChanged"
    />

    <ol-tile-layer>
      <ol-source-osm />
    </ol-tile-layer>

    <ol-rotate-control></ol-rotate-control>
    <ol-interaction-link />

    <!-- Vector layer for the pins -->
    <ol-vector-layer>
      <ol-source-vector :features="features" />
    </ol-vector-layer>

    <!-- Popover element -->
    <div ref="popover" class="popover">
      <div class="popover-content">{{ popoverContent }}</div>
    </div>
  </ol-map>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { fromLonLat } from 'ol/proj'
import { Feature, Overlay } from 'ol'
import Point from 'ol/geom/Point'
import { Style, Icon, Text, Fill } from 'ol/style'

// Center the map on the world
const center = ref(fromLonLat([0, 0])) // Center around the world
const rotation = ref(0)
const zoom = ref(2) // Zoom out to see the whole world
const projection = ref('EPSG:3857')

// Function to handle changes in the center
const centerChanged = (event) => {
  center.value = event.target.getCenter()
}

// Function to handle changes in the resolution
const resolutionChanged = (event) => {
  zoom.value = event.target.getZoom()
}

// Function to handle changes in the rotation
const rotationChanged = (event) => {
  rotation.value = event.target.getRotation()
}

// Define the coordinates for capital cities and their labels
const capitalData = [
  { coords: [2.2137, 48.6278], label: '1', info: 'Paris, France' },
  { coords: [13.4050, 52.5200], label: '2', info: 'Berlin, Germany' },
  { coords: [-0.1276, 51.5074], label: '3', info: 'London, UK' },
  { coords: [139.6917, 35.6895], label: '4', info: 'Tokyo, Japan' },
  { coords: [-74.0060, 40.7128], label: '5', info: 'New York, USA' },
  { coords: [116.4074, 39.9042], label: '6', info: 'Beijing, China' },
  { coords: [10.4515, 51.1657], label: '7', info: 'Germany' },
  { coords: [121.4737, 31.2304], label: '8', info: 'Shanghai, China' },
  { coords: [37.6173, 55.7558], label: '9', info: 'Moscow, Russia' },
  { coords: [-58.3816, -34.6037], label: '10', info: 'Buenos Aires, Argentina' },
  { coords: [116.5704, 39.6519], label: '11', info: 'Ulaanbaatar, Mongolia' }
]

// Create a feature for each pin
const createPinFeature = (coords, label, info) => {
  const feature = new Feature({
    geometry: new Point(fromLonLat(coords)),
    info: info // Store the additional information in the feature
  })
  return feature
}

// SVG for the pin
const svgIcon = `
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
    <path fill="green" stroke="#000000" stroke-width="0" d="M24 8C14.63 8 8 14.63 8 24c0 10.5 14 26 14 26s14-15.5 14-26c0-9.37-6.63-16-14-16z" />
  </svg>`;

const svgIconUrl = 'data:image/svg+xml;base64,' + btoa(svgIcon);

// Create pin features and apply styles
const features = ref(
  capitalData.map(({ coords, label, info }) => {
    const pinFeature = createPinFeature(coords, label, info)
    pinFeature.setStyle(
      new Style({
        image: new Icon({
          src: svgIconUrl,
          anchor: [0.5, 1],
          scale: 1.5 // Adjust the scale as needed to make the pin bigger
        }),
        text: new Text({
          text: label,
          font: 'bold 16px Arial',
          fill: new Fill({ color: 'red' }),
          offsetY: -35 // Position the label above the pin
        })
      })
    )
    return pinFeature
  })
)

const popoverContent = ref('')
const popoverElement = ref(null)
let popoverOverlay = null

// Function to handle pointer move
const handlePointerMove = (event) => {
  if (!popoverOverlay.value) return

  const map = popoverOverlay.value.getMap()
  const pixel = event.pixel
  const feature = map.forEachFeatureAtPixel(pixel, (feature) => feature)
  
  if (feature) {
    popoverContent.value = feature.get('info')
    const coordinates = feature.getGeometry().getCoordinates()
    popoverOverlay.value.setPosition(coordinates)
    popoverElement.value.style.display = 'block'
  } else {
    popoverElement.value.style.display = 'none'
  }
}

// Initialize the popover overlay
onMounted(() => {
  nextTick(() => {
    const mapElement = document.querySelector('ol-map')
    const mapInstance = mapElement.__vue_map__
    popoverElement.value = document.querySelector('.popover')
    
    popoverOverlay = new Overlay({
      element: popoverElement.value,
      positioning: 'bottom-center',
      stopEvent: false
    })
    mapInstance.addOverlay(popoverOverlay)
  })
})
</script>

<style scoped>
/* Set the map container height to 100vh */
ol-map {
  height: 100vh;
}

.popover {
  display: none;
  position: absolute;
  background-color: white;
  padding: 5px;
  border: 1px solid black;
  border-radius: 3px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.popover-content {
  font-size: 14px;
  color: black;
}
</style>
