<template>
 
  <ComFrontDeskLayout :title="$t('Map View')">
    {{ filter }}
    {{ data.result }}
    <!-- filter -->
    <ComSelect :clear="false" v-model="filter.timespan" :options="timespanOption"  @onSelected="onSearch"/>
    <Calendar  :selectOtherMonths="true"  v-model="filter.date_range" v-if="filter.timespan == 'Date Range'"  selectionMode="range"  @date-select="onSearch" dateFormat="dd-mm-yy" showButtonBar showIcon panelClass="no-btn-clear"/>
    <ComSelect   :filters="[['property', '=', property_name]]" :placeholder="$t('All Room Types')" v-model="filter.room_type" doctype="Room Type"   optionLabel="room_type" optionValue="name" @onSelected="onSearch"> </ComSelect>
    <ComAutoComplete  :filters="[['property', '=', property_name]]" :placeholder="$t('All Business Source')" v-model="filter.business_source" doctype="Business Source" optionLabel="business_source" optionValue="name" @onSelected="onSearch"/>
            
    <!-- Openlayer Map -->
    <ol-map style="height: 100vh" 
      v-if="data"
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
        v-for="(d, index) in data.result"
        :key="index"
        :position="[d.long, d.lat]"
        :autoPan="true"
         
      >
        <div class="overlay-content" @click="handleOverlayClick">
          <div

            class="pin-marker"
            @mouseover="(event) => showTooltip(event, d)"
            
          >
            <!-- SVG Icon as Pin Marker with dynamic fill color -->
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 384 512"
              :style="{ fill: getPinColor(d.adr) }"
              class="svg-pin"
            >
              <path
                d="M384 192c0 87.4-117 243-168.3 307.2c-12.3 15.3-35.1 15.3-47.4 0C117 435 0 279.4 0 192C0 86 86 0 192 0S384 86 384 192z"
              />
            </svg>
            <!-- Label inside pin -->
            <div class="pin-label">
              {{ d.adr }}
            </div>
          </div>
        </div>
      </ol-overlay>
   
    </ol-map>
  </ComFrontDeskLayout>
</template>
<script setup>
import { ref,h,getApi } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComMapViewTooltip from "@/views/frontdesk/components/ComMapViewTooltip.vue";
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
import { useTippy } from 'vue-tippy'

// Openlayer

const center = ref([0, 0]); 
const projection = ref("EPSG:4326");
const zoom = ref(1);
const offset = ref(0);
const property_name = window.property_name
const filter = ref({timespan:"This Year",
  property:property_name,
  row_group:"Nationality",
  show_summary:0
})

const data = ref({})

const timespanOption = ["Today","Yesterday","This Month","Next Month","Last Month","This Year","Last Year", "Date Range"]

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

 
const onSearch = debouncer((show_loading = true) => {
  getApi("frappe.desk.query_report.run",{
    report_name:"Revenue and Occupancy Summary Report", 
    filters:filter.value
  },"").then(result=>{
    data.value = result.message
  })
}, 1000);

function  handleOverlayClick(){
  alert("this is over lay click")
}
function  mapClick(){
  alert(123)
}



function showTooltip(event,d) {
  console.log(d)
  useTippy(event.target.parentNode, {
      content: h(ComMapViewTooltip, { data: d }),
      placement: "top",
      followCursor: true,
  })
  return
}

 

function getPinColor(population) {
  return "red";
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
