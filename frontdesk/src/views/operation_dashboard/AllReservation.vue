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
      @rowContextmenu="onRowContextMenu" contextMenu
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
        <div class="text-2xl flex align-items-center gap-2">
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

  <ContextMenu ref="cm" :model="menuModel" @before-show="onBeforeShow">
    <template #item="{ item, props }">
      <a v-ripple class="flex items-center" v-bind="props.action">
          <!-- <ComIcon :icon="item.customIcon" style="height: 12px;" /> -->
          <i :class="`pi ${item.customIcon}`"></i>
          <span class="ml-2">{{ item.label }}</span>

          <Badge v-if="item.badge" class="ml-auto" :value="item.badge" />
          <span v-if="item.shortcut"
              class="ml-auto border border-surface rounded bg-emphasis text-muted-color text-xs p-1">
              {{ item.shortcut }}
          </span>
          <i v-if="item.items" class="pi pi-angle-right ml-auto"></i>
      </a>
    </template>
  </ContextMenu>
  <div>xxx</div>
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
  useDialog
} from "@/plugin";
import { useConfirm } from "primevue/useconfirm";
import ComGuestCard from "@/views/operation_dashboard/components/ComGuestCard.vue";
import ComAccomodationCard from "@/views/operation_dashboard/components/ComAccomodationCard.vue";
import ComStayInfoCard from "@/views/operation_dashboard/components/ComStayInfoCard.vue";
import ComReservationStayStatus from "@/views/operation_dashboard/components/ComReservationStayStatus.vue";
import ComStayAction from "@/views/operation_dashboard/components/ComStayAction.vue";
import ComOrderBy from "@/components/ComOrderBy.vue";
import ComConfirmCheckIn from '@/views/reservation/components/confirm/ComConfirmCheckIn.vue'
import ComGroupInfo from "@/views/operation_dashboard/components/ComGroupInfo.vue";
import ComFilter from "@/components/document/components/ComFilter.vue";
import ContextMenu from 'primevue/contextmenu';

import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const dialog = useDialog()
const route = useRoute();
const old_op = inject("$operation_dashboard");
const op = inject("$operation_dashboard");
const rs = inject("$reservation_stay");
const data_op = ref();
const moment = inject("$moment");
const confirm = useConfirm()
const rowData = ref({})
op.page_title = route.meta.title;
op.current_route = route.name;

const cm = ref();
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


// const onRowContextMenu = (event) => {
//   rowData.value = event.data;
//   cm.value.show(event.originalEvent);
//   rs.reservation.name = event.data.reservation
//   rs.reservationStay.name = event.data.name
//   rs.reservationStay.arrival_date = event.data.arrival_date
//   rs.reservationStay.is_reserved_room = event.data.is_reserved_room
//   rs.reservationStay.departure_date = event.data.departure_date
//   rs.reservationStay.reservation_status = event.data.reservation_status
// }; 

// const menuModel = ref([])

// console.log(rs.canCheckIn() && rs.reservationStay?.reservation_status != 'In-house')

// if (rs.canCheckIn() && rs.reservationStay?.reservation_status != 'In-house'){
//   menuModel.value.push({label: 'Check-In', customIcon: 'pi-sign-in', command: () => onCheckIn()})
// }

// menuModel.value.push({
//   separator: true
// })

// if (rs.reservationStay?.reservation_status === 'In-house' && (moment(working_day.date_working_day) >= moment(rs.reservationStay.departure_date).add(-1, 'day'))){
//   menuModel.value.push({label: 'Check Out', customIcon: 'pi-sign-out', command: () =>onCheckOut()})
// }


// const onCheckIn = () => {
//   const dialogRef = dialog.open(ComConfirmCheckIn, {
//       props: {
//           header: $t('Confirm Check In'),
//           style: {
//               width: '650px',
//           },
//           modal: true,
//           closeOnEscape: false,
//           breakpoints:{
//               '960px': '650px',
//               '640px': '100vw'
//           },

//       },
//       onClose: (options) => {
//           const result = options.data;
//           if (result) {
//               rs.loading = true
              
//               postApi("reservation.check_in", {
//                   reservation: rowData.value.reservation,
//                   reservation_stays: [rowData.value.name],
//                   note: result.note,
//                   arrival_time:result.checked_in_date
//               }).then((result) => {
//                   rs.loading = false
//                   window.postMessage({"action":"ComHousekeepingStatus"},"*");
//                   window.postMessage({"action":"Dashboard"},"*")
//                   window.postMessage({action:"ReservationList"},"*")
//                   window.postMessage({action:"ReservationDetail"},"*")
//                   window.postMessage({action:"Frontdesk"},"*")
//                   window.postMessage({action:"TodaySummary"},"*")
//                   window.postMessage({action:"GuestLedger"},"*")
//                   window.postMessage({action:"GuestLedgerTransaction"},"*")
//                   window.postMessage({action:"Reports"},"*")
//                 window.postMessage({action:"FolioTransactionList"},"*")

//                   onRefresh(false)
//               })
//                   .catch((err) => {
//                       rs.loading = false
//                   })
//           }
//       }
//   })
// }

// const onCheckOut = () => {
//   confirm.require({
//       message: 'Are you sure you want to check out this room?',
//       header: 'Confirmation',
//       acceptLabel: 'OK',
//       rejectVisible: true,
//       rejectClass: 'hidden',
//       acceptClass: 'border-none',
//       acceptIcon: 'pi pi-check-circle',
//       icon: 'pi pi-exclamation-triangle',
//       accept: () => {
//           rs.loading = true
//           postApi("reservation.check_out", {
//               reservation: rowData.value.reservation,
//               reservation_stays: [rowData.value.name]
//           }, "Check out successfully")
//               .then((result) => {
//                   rs.loading = false
//                   onRefresh()
//                   window.postMessage({"action":"ComHousekeepingStatus"},"*");
//                   window.postMessage({"action":"Dashboard"},"*")
//                   window.postMessage({action:"ReservationStayList"},"*")
//                   window.postMessage({action:"ReservationList"},"*") 
//                   window.postMessage({action:"ReservationDetail"},"*")
//                   window.postMessage({action:"Frontdesk"},"*")
//                   window.postMessage({action:"TodaySummary"},"*")
//                   window.postMessage({action:"GuestLedger"},"*")
//                   window.postMessage({action:"GuestLedgerTransaction"},"*")
//                   window.postMessage({action:"Reports"},"*")
//                 window.postMessage({action:"FolioTransactionList"},"*")
//                   window.socket.emit("ComRunNightAudit", { property: window.property_name })

//               })
//               .catch((err) => {
//                   rs.loading = false
//               })
//       }
//   });
// }
</script>
