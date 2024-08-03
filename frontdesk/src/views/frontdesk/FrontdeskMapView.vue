<template>
  <ComFrontDeskLayout :title="$t('Map View')">
    <!-- Filter -->
    <!-- {{ filters }} -->
    <!-- {{ data }} -->
    <div class="page-form rounded-lg">
      <div class="form-group frappe-control input-max-width md:w-full">
        <div class="link-field ui-front flex items-center space-x-9">
          <ComSelect
            :clear="false"
            v-if="data.columns"
            :options="data?.columns"
            v-model="filters.display_field"
            optionLabel="label"
            optionValue="fieldname"
            class="w-full overflow-x-auto"
          />
          <ComSelect
            :clear="false"
            :options="timespanOption"
            v-model="filters.timespan"
            :placeholder="$t('Select Timespan')"
            class="w-full overflow-x-auto"
          />
          <ComSelect
            :filters="[['property', '=', property_name]]"
            :placeholder="$t('All Room Types')"
            v-model="filters.room_type"
            doctype="Room Type"
            optionLabel="room_type"
            optionValue="name"
            class="w-full overflow-x-auto"
          ></ComSelect>
          <!-- <div :class="bodyClass"> -->
          <ComAutoComplete
            isFull
            :filters="[['property', '=', property_name]]"
            :placeholder="$t('All Business Source')"
            v-model="filters.business_source"
            doctype="Business Source"
            optionLabel="business_source"
            optionValue="name"
            class="w-full overflow-x-auto"
          />
          <!-- </div> -->
        </div>
      </div>
    </div>

    <!-- Openlayer Map -->
    <!-- {{ mapCoordinate }} -->
    <ol-map style="height: 100vh" @click="handleMapClick">
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
        v-for="(d, index) in data.result?.filter((r) => r.lat && r.long)"
        :key="index"
        :position="[d.long, d.lat]"
        positioning="center-center"
      >
        <div class="overlay-content" @click="handleOverlayClick">
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
                {{ d[filters.display_field] }}
              </text>
            </svg>
          </div>
        </div>
      </ol-overlay>
    </ol-map>
  </ComFrontDeskLayout>
</template>
<script setup>
import { ref, h, getApi, onMounted } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComMapViewTooltip from "@/views/frontdesk/components/ComMapViewTooltip.vue";
import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
import { useTippy } from "vue-tippy";
const mapCoordinate = ref();
// Openlayer
const data = ref({});

const center = ref([104.991, 12.5657]); // Center on Cambodia
const projection = ref("EPSG:4326");
const zoom = ref(0);
const filters = ref({ timespan: "This Year", display_field: "occupy" });
const timespanOption = ref([
  "Today",
  "Yesterday",
  "This Month",
  "Next Month",
  "Last Month",
  "This Year",
  "Last Year",
  "Date Range",
]);
const property_name = window.property_name;

const tooltipIndex = ref(null);

function handleOverlayClick() {
  alert("this is over lay click");
}
const handleMapClick = (event) => {
  // Get the coordinate where the click happened
  mapCoordinate.value = event.coordinate;
};

function onLoadData() {
  getApi(
    "frappe.desk.query_report.run",
    {
      report_name: "Revenue and Occupancy Summary Report",
      filters: {
        property: "ESTC  & HOTEL's",
        timespan: "Date Range",
        start_date: "2024-08-01",
        end_date: "2024-08-31",
        row_group: "Nationality",
        show_columns: [],
        show_summary: 1,
        show_summary_field: [],
        chart_type: "bar",
        show_chart_series: [],
      },
      ignore_prepared_report: false,
      are_default_filters: false,
    },
    ""
  ).then((result) => {
    data.value = result.message;
  });
}

function showTooltip(event, data) {
  useTippy(event.target.parentNode, {
    content: h(ComMapViewTooltip, { data: data }),
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

onMounted(() => {
  onLoadData();
});
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
