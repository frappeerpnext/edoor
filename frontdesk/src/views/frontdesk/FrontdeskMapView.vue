<template>
  <ComFrontDeskLayout :title="$t('Map View')">
  
    <!-- Filter -->
    <!-- {{ filters }} -->
    {{ data.report_summary }}
 
    <div class="page-form rounded-lg">
      <div class="form-group frappe-control input-max-width md:w-full">
        <div class="link-field ui-front flex items-center space-x-9">
          

          <ComSelect
            :clear="false"
            :options="timespanOption"
            v-model="filters.timespan"
            @onSelected="onRefreshData"
            :placeholder="$t('Date')"
            class="w-full overflow-x-auto"
          />
          <Calendar 
            class="w-full"
              :selectOtherMonths="true"   hideOnRangeSelection v-if="filters.timespan =='Date Range'" dateFormat="dd-MM-yy"
                  v-model="filters.date_range" selectionMode="range" :manualInput="false" 
                  @date-select="onSelectDateRange"
                  placeholder="Select Date Range" showIcon />
         
          <ComSelect
            :filters="[['property', '=', property_name]]"
            :placeholder="$t('All Room Types')"
            v-model="filters.room_type"
            doctype="Room Type"
            optionLabel="room_type"
            optionValue="name"
            class="w-full overflow-x-auto"
            @onSelected = "onRefreshData"
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
            @onSelected = "onRefreshData"
          />
          <!-- </div> -->
          <ComSelect
            :clear="false"
            v-if="data.columns"
            :options="data?.columns.filter(r=>r.fieldtype)"
            v-model="filters.display_field"
            optionLabel="label"
            optionValue="fieldname"
            class="w-full overflow-x-auto"
          />
        </div>
      </div>
    </div>

    <!-- summayr -->
    <div v-for="(s, index) in data.report_summary" :key="index" :class="s.indicator" >
      {{ s.label }} <br/>
      <span :style="'color:' + s.indicator"> {{s.value}}</span>
     

    </div>
    <!-- Openlayer Map -->
    <!-- {{ mapCoordinate }} -->
    <TabView   class="tabview-custom mt-3">
      <TabPanel :header="$t('Map View')">
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
    </TabPanel>
    <TabPanel :header="$t('Data View')">
    <DataTable :value="data.result" tableStyle="min-width: 50rem">
      <Column v-for="col of data.columns" :key="col.fieldname" :field="col.fieldname" 
      :header="col.label"
         :headerClass="getAlignment(col.fieldtype)" 
         :bodyClass="getAlignment(col.fieldtype)"
         sortable 
      >
        <template #body="slotProps">
          
          <CurrencyFormat v-if="col.fieldtype=='Currency'" :value="slotProps.data[col.fieldname]"  :class="slotProps.data.is_total_row ==1?'font-bold':''"/>
         
            <span  v-else-if="col.fieldtype=='Percent'"  :class="slotProps.data.is_total_row ==1?'font-bold':''">{{ parseFloat(slotProps.data[col.fieldname]).toFixed(2)}}% </span>
          
          <span :class="slotProps.data.is_total_row ==1?'font-bold':''" v-else>
            {{slotProps.data[col.fieldname]}}
          </span>
        </template>
      </Column>
  </DataTable>
    </TabPanel>
</TabView>
  </ComFrontDeskLayout>
</template>
<script setup>
import { ref, h, getApi, inject, onMounted,nextTick,computed } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComMapViewTooltip from "@/views/frontdesk/components/ComMapViewTooltip.vue";
import ComViewSummaryByNationality from "@/views/frontdesk/components/ComViewSummaryByNationality.vue";
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();

import { i18n } from "@/i18n";
const { t: $t } = i18n.global;
import { useTippy } from "vue-tippy";
import CurrencyFormat from "../../components/CurrencyFormat.vue";

const mapCoordinate = ref();
// Openlayer
const data = ref({});
const moment = inject("$moment");
const gv =  inject("$gv")

const center = ref([104.991, 12.5657]); // Center on Cambodia
const projection = ref("EPSG:4326");
const zoom = ref(0);
const property_name = window.property_name;
const filters = ref({ timespan: "This Year", display_field: "occupy",row_group: "Nationality",property: property_name,chart_type: "bar",show_summary: 1 });
 
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



const fieldtype =computed(()=>{
  return data.value.columns.find(r=>r.fieldname == filters.value.display_field).fieldtype
})

function getAlignment(fieldtype){
  if (fieldtype=='Currency') return "text-right"
  if (fieldtype=='Percent' || fieldtype=='Int' || fieldtype=='Float') return "text-center"

  return "text-left" 
}

function handleOverlayClick(data) {
  dialog.open(ComViewSummaryByNationality, {
        props: {
            header: $t('View Summary by Nationality') + " - " + data.row_group,
            style: {
                width: '80vw',
            }, 
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
             
            
        }
    });
}

const handleMapClick = (event) => {
  // Get the coordinate where the click happened
  mapCoordinate.value = event.coordinate;
};

const onSelectDateRange = (data) => {
  if (filters.value.date_range){
    if (!filters.value.date_range[0]){
      delete filters.value["start_date"]
    }else {
      filters.value.start_date = moment(filters.value.date_range[0]).format("YYYY-MM-DD")
    }
    if (!filters.value.date_range[1]){
      delete filters.value["end_date"]
    }else {
      filters.value.end_date = moment(filters.value.date_range[1]).format("YYYY-MM-DD")
    }
  }

  onRefreshData()
};


function onRefreshData(){

  onLoadData()
}

async function onLoadData() {
  await nextTick();
  if (filters.value.timespan=="Date Range"){
    if (!filters.value.start_date || !filters.value.end_date){
      return
    }
  }

  gv.loading = true
  getApi(
    "frappe.desk.query_report.run",
    {
      report_name: "Revenue and Occupancy Summary Report",
      filters:filters.value,
      ignore_prepared_report: false,
      are_default_filters: false,
    },
    ""
  ).then((result) => {
    data.value = result.message;
    gv.loading = false ;
  }).catch(error=>{
    gv.loading = false ;
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
