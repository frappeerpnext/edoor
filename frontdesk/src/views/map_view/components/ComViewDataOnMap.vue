<template>
  <Message :closable="false">You are viewing field <strong> {{ columns?.find(r=>r.fieldname == filters.display_field).label }} </strong></Message>
     <ol-map  style="height: 100vh" @click="handleMapClick">
      <ol-view
        ref="view"
        :center="center"
        :zoom="zoom"
        :projection="projection"
        v-if="data"
      />

      <ol-tile-layer>
        <ol-source-osm />
      </ol-tile-layer>

      <ol-overlay
        v-for="(d, index) in data?.filter((r) => r.lat && r.long)"
        :key="index"
        :position="[d.long, d.lat]"
        positioning="center-center"
      >
        <div class="overlay-content" @click="handleOverlayClick(d)">
          <div
            class="pin-marker"
            @mouseover="(event) => showTooltip(event, d)"
            @mouseleave="hideTooltip"
          >
         
          
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 200 200"
              :style="{ fill: getPinColor(d.occupancy) }"
              class="svg-pin"
            >
              <circle
                cx="100"
                cy="100"
                r="100"
                stroke="#ffffff"
                stroke-width="7"
              />
              <text
                x="50%"
                y="50%"
                alignment-baseline="middle"
                text-anchor="middle"
                font-size="50"
                fill="#ffffff"
              >

              <CurrencyFormat  v-if="fieldtype=='Currency'" :hideWrapper="true" :value="d[filters.display_field]" />
              <template v-else-if="fieldtype=='Percent'">
                {{ parseFloat(d[filters.display_field]).toFixed(2) }} %
              </template>
              <template v-else>
                {{ d[filters.display_field] }}
              </template>
              </text>
            </svg>
          </div>
        </div>
      </ol-overlay>
    </ol-map>

</template>
<script setup>
import { ref,inject ,computed,h } from "@/plugin"
import ComMapViewTooltip from "@/views/map_view/components/ComMapViewTooltip.vue";
import { i18n } from "@/i18n";
import { useTippy } from "vue-tippy";
import ComViewSummaryByNationality from "@/views/map_view/components/ComViewSummaryByNationality.vue";
import { useDialog } from 'primevue/usedialog';
import Message from "primevue/message";
const dialog = useDialog();
const { t: $t } = i18n.global;
const mapCoordinate = ref();
const center = ref([104.991, 12.5657]); // Center on Cambodia
const projection = ref("EPSG:4326");
const zoom = ref(1);

const props = defineProps({
    filters:Object,
    columns:Object,
    data:Object
})

const emit = defineEmits(['update:modelValue','onSelect'])


const fieldtype =computed(()=>{
  return props.columns.find(r=>r.fieldname == props.filters.display_field).fieldtype
})


function showTooltip(event, info) {
  useTippy(event.target.parentNode, {
    content: h(ComMapViewTooltip, { data:info, columns:props.columns }),
    placement: "top",
    followCursor: true,
  });
  return;
}

function getPinColor(occ) {
  if (occ <= 25) {
    return "#aa7f1f";
  } else if (occ > 25 && occ <= 50) {
    return "#ec864b";
  } else if (occ > 50 && occ <= 75) {
    return "#4763f2";
  } else {
    return "#15b5f3";
  }
}

function handleOverlayClick(data) {
  const new_filters = JSON.parse(JSON.stringify(props.filters))

  new_filters.nationality = data.row_group
  dialog.open(ComViewSummaryByNationality, {
    data: {
      filters: new_filters
    },
    props: {
      header: $t('View Summary by Nationality') + " - " + data.row_group,
      style: {
        width: '80vw',
      },
      modal: true,
      maximizable: true,
      closeOnEscape: false,
      position: "top",
      breakpoints: {
        '960px': '80vw',
        '640px': '100vw'
      },

    },
    onClose: (options) => {


    }
  });
}

const handleMapClick = (event) => {

  mapCoordinate.value = event.coordinate;
};


function onRefreshData(){
    emit("onFilter",props.filters)
}


</script>


<style scoped>
.pin-marker {
  position: relative; /* To position the tooltip */
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer; /* Show pointer cursor */
}

.svg-pin {
  width: 50px; /* Increased size of pin */
  height: 50px; /* Increased size of pin */
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