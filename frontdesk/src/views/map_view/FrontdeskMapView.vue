<template>
  <ComFrontDeskLayout
    :title="$t('Map View')"
    :showSetting="true"
    :showRefreshButton="true"
    @onRefresh="onRefreshData"
    @onSetting="onSetting"
  >
    <ComFilter
      @onFilter="onRefreshData"
      :filters="filters"
      :columns="data.columns"
    />
    <hr class="my-2" />
    <div class="grid">
      <div class="col-12 px-3">
        <!-- summayr -->
        <ComSummaryKPI :report_summary="data.report_summary" />
      </div>
    </div>

    <!-- chart -->
    <ComChartView v-if="data?.chart" :chart="data?.chart" />
    <!-- Tab View Map View and Table View -->
    <TabView class="tabview-custom mt-3" @tab-change="onTabChange">
      <TabPanel :header="$t('Map View')">
        <ComViewDataOnMap
          :data="data.result"
          :columns="data.columns"
          :filters="filters"
        />
      </TabPanel>
      <TabPanel :header="$t('Data View')">
        <ComViewDataInTable
          v-if="tabTableViewLoaded"
          :data="data.result"
          :columns="data.columns"
        />
      </TabPanel>
    </TabView>
  </ComFrontDeskLayout>
</template>
<script setup>
import { ref, getApi, inject, onMounted, nextTick, computed } from "@/plugin";
import ComFrontDeskLayout from "@/views/frontdesk/components/ComFrontDeskLayout.vue";
import ComFilter from "@/views/map_view/components/ComFilter.vue";
import ComChartView from "@/views/map_view/components/ComChartView.vue";
import ComSetting from "@/views/map_view/components/ComSetting.vue";

import ComViewDataInTable from "@/views/map_view/components/ComViewDataInTable.vue";
import ComViewDataOnMap from "@/views/map_view/components/ComViewDataOnMap.vue";
import ComSummaryKPI from "@/views/map_view/components/ComSummaryKPI.vue";

import { i18n } from "@/i18n";
import { useDialog } from "primevue/usedialog";
import { collapseTransitionProps } from "@varlet/ui";
const { t: $t } = i18n.global;
const dialog = useDialog();
const tabTableViewLoaded = ref(false);

// Openlayer
const data = ref({});

const gv = inject("$gv");

const property_name = window.property_name;
const filters = ref({
  timespan: "This Year",
  display_field: "occupancy",
  row_group: "Nationality",
  property: property_name,
  chart_type: "bar",
  show_summary: 1,
  show_chart_series: [],
});

function onTabChange(event) {
  if (event.index == 1) {
    tabTableViewLoaded.value = true;
  }
}

function onSetting() {
  dialog.open(ComSetting, {
    props: {
      header: $t("Setting"),
      style: {
        width: "40vw",
      },
      modal: true,
      maximizable: false,
      closeOnEscape: true,
      position: "top",
      breakpoints: {
        "960px": "80vw",
        "640px": "100vw",
      },
    },
    onClose: (options) => {
      if (options) {
        // dynamic assign key to setting
        const data = options.data;
        Object.keys(data).forEach((key) => {
          filters.value[key] = data[key];
        });
        onRefreshData();
      }
    },
  });
}

function onRefreshData(f) {
  onLoadData();
}

async function onLoadData() {
  await nextTick();
  if (filters.value.timespan == "Date Range") {
    if (!filters.value.start_date || !filters.value.end_date) {
      return;
    }
  }

  gv.loading = true;
  getApi(
    "frappe.desk.query_report.run",
    {
      report_name: "Revenue and Occupancy Summary Report",
      filters: filters.value,
      ignore_prepared_report: false,
      are_default_filters: false,
    },
    ""
  )
    .then((result) => {
      data.value = result.message;
      // check if occupancy in result list
      if (
        data.value.columns.filter(
          (r) => r.fieldname == filters.value.display_field
        ).length == 0
      ) {
        filters.value.display_field = data.value.columns[1].fieldname;
      }

      gv.loading = false;
    })
    .catch((error) => {
      gv.loading = false;
    });
}

onMounted(() => {
  const s = localStorage.getItem("frontdesk_map_view_setting");
  if (s) {
    const filter = JSON.parse(s);
    Object.keys(filter).forEach((key) => {
      filters.value[key] = filter[key];
    });
  }
  onLoadData();
});
</script>
