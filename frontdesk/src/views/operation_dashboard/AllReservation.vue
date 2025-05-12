<template>
  <div class="grid">
    <div class="col-8">
      <ComFilter
        @onSearch="onSearch"
        :filters="filterOptions"
        v-model:filter="filter"
        :hideGroupByField="false"
      />
    </div>
    <div class="col-4 text-end">
      <div>
        <ComOrderBy
          doctype="Reservation Stay"
          @onOrderBy="onOrderBy"
          wrapper-class="justify-content-end"
        />
      </div>
    </div>
  </div>
  <div class="card mt-2">
    <DataTable
      :value="data_op"
      tableStyle="min-width: 50rem"
      :is-not-empty="op.all_reservation_data?.data.length > 0"
      rowGroupMode="subheader"
      :groupRowsBy="filter.group_by[2]"
      selectionMode="single"
      :selection="selectedRow"
      @row-dblclick="onRowDoubleClick"
      tableClass="operation_data_dashboard"
    >
      <Column header="Guest">
        <template #body="slotProps">
          <ComGuestCard :data="slotProps.data" />
        </template>
      </Column>
      <Column header="Accomodation">
        <template #body="slotProps">
          <ComAccomodationCard :data="slotProps.data" />
        </template>
      </Column>

      <Column header="Stay Info">
        <template #body="slotProps">
          <ComStayInfoCard :data="slotProps.data" />
        </template>
      </Column>
      <Column header="Status">
        <template #body="slotProps">
          <ComReservationStayStatus :data="slotProps.data" />
        </template>
      </Column>
      <Column header="Action">
        <template #body="slotProps">
          <ComStayAction
            :data="slotProps.data"
            @onMoreAction="OnMoreAction(slotProps.data)"
          />
        </template>
      </Column>
      <template #expansion="slotProps">
        <div class="p-3">Detail Action list here</div>
      </template>
      <template #groupheader="slotProps">
        <!-- <ComGroupInfo :data="slotProps.data" group_by="guest_name"/> -->
        <div class="text-2xl">
          <span v-if="filter.group_by[2] == 'room_type_id'">
            {{ slotProps.data.room_type }}
          </span>
          <span v-else>
            {{ slotProps.data[filter.group_by[2]] }}
          </span>

          <Badge
            :value="
              data_op?.filter(
                (r) =>
                  r[filter.group_by[2]] === slotProps.data[filter.group_by[2]]
              ).length
            "
          ></Badge>
        </div>
      </template>
    </DataTable>
  </div>
</template>

<script setup>
import {
  inject,
  ref,
  useRoute,
  watch,
  onMounted,
  getApi,
  postApi,
} from "@/plugin";
import ComGuestCard from "@/views/operation_dashboard/components/ComGuestCard.vue";
import ComAccomodationCard from "@/views/operation_dashboard/components/ComAccomodationCard.vue";
import ComStayInfoCard from "@/views/operation_dashboard/components/ComStayInfoCard.vue";
import ComReservationStayStatus from "@/views/operation_dashboard/components/ComReservationStayStatus.vue";
import ComStayAction from "@/views/operation_dashboard/components/ComStayAction.vue";
import ComOrderBy from "@/components/ComOrderBy.vue";

import ComGroupInfo from "@/views/operation_dashboard/components/ComGroupInfo.vue";
import ComFilter from "@/components/document/components/ComFilter.vue";
// import ComAccomodationCard from "@/views/operation_dashboard/components/ComAccomodationCard.vue"
const route = useRoute();
const old_op = inject("$operation_dashboard");
const op = inject("$operation_dashboard");
const rs = inject("$reservation_stay");
const data_op = ref();
const moment = inject("$moment");
op.page_title = route.meta.title;
op.current_route = route.name;

const selectedRow = ref({});
const data = ref([]);
const expandedRows = ref(null);
const filterOptions = [
  {
    fieldname: "business_source",
    fieldtype: "Link",
    options: "Business Source",
    label: "Business Source",
  },
  {
    fieldname: "room_type_id",
    fieldtype: "Link",
    options: "Room Type",
    label: "Room Type",
  },
  {
    fieldname: "group_by",
    fieldtype: "Select",
    default: "stay_type",
    options: [
      { label: "Arrival/Stay Over/Departure", value: "stay_type" },
      { label: "Business Source", value: "business_source" },
      { label: "Room Type", value: "room_type_id" },
      { label: "Guest", value: "guest" },
      { label: "Reservation", value: "reservation" },
    ],
    label: "Group By",
    hideOperator: true,
  },
];

const filter = ref({
  group_by: ["group_by", "=", "stay_type"],
});

// refresh
watch(
  () => op.refresh_token,
  (new_data) => {
    loadData();
  }
);

const onRowSelect = (event) => {
  expandedRows.value = [event.data];
};

function onSearch() {
  loadData();
}

function loadData() {
  const apiFilter = {
    property: window.property_name,
    date: moment(op.current_date).format("YYYY-MM-DD"),
    group_by_field: filter.value.group_by[2],
    order_by_field: filter.value.order_by || '',
    sort_type: filter.value.order_type || ''
  };
  if (filter.value.keyword) {
    apiFilter.keyword = encodeURIComponent(filter.value.keyword);
  }

  if (filter.value.business_source) {
    apiFilter.business_source = [
      filter.value.business_source[1],
      filter.value.business_source[2],
    ];
  }
  if (filter.value.room_type_id) {
    apiFilter.room_type_id = [
      filter.value.room_type_id[1],
      filter.value.room_type_id[2],
    ];
  }

  postApi(
    "operation_dashboard.get_all_guest",
    {
      param: apiFilter,
    },
    "",
    false
  ).then((result) => {
    op.all_reservation_data.date = moment(op.current_date).format("YYYY-MM-DD");

    data_op.value = result.message;
  });
}

onMounted(() => {
  loadData();
});

function onRowDoubleClick(event) {
  const rowData = event.data;
  window.postMessage("view_reservation_stay_detail" + "|" + rowData.name, "*");
}

const OnMoreAction = (data) => {
  rs.getReservationDetail(data.name, true);
};


const onOrderBy = (data) => {
  filter.value.order_by = data.order_by;
  filter.value.order_type = data.order_type;
  loadData();
};
</script>
