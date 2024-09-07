<template>
  <ComOwnerContentTitle :label="'Transaction'" :date="moment(date).format('DD-MM-YYYY')">
    <div class="flex-col flex">
      <div class="px-2 mb-4 border-bottom-1">
        <Button class="ms-2 col px-3 border-1 mt-2 p-tabview-nav-link recent_transaction_tap"
          :class="{ 'active_recent_transaction': activeIndex === index }" @click="onFilterFolioTransaction(btn, index)"
          v-for="(btn, index) in ['All', 'Reservation Folio', 'Desk Folio', 'Deposit Ledger']" :key="index">

          {{ $t(btn) }}

        </Button>
      </div>


      <ComPlaceholder text="No Data" height="40rem" :loading="gv.loading" :is-not-empty="data.length > 0">
        <div style="min-height:40rem;">
          <DataTable scrollable :rows="5" :rowsPerPageOptions="[5, 10, 20, 50]" class="res_list_scroll" showGridlines
            :value="data" tableStyle="min-width: 50rem;" @row-dblclick="onViewReservationStayDetail"
            scrollHeight="70vh">
            <Column
              v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes') == 'Yes')"
              :key="c.fieldname" :field="c.fieldname" :header="$t(c.label)" :headerClass="c.header_class || ''"
              :bodyClass="c.header_class || ''" :frozen="c.frozen">
              <template #body="slotProps">
                <Button v-if="c.fieldtype == 'Link' && slotProps.data[c.fieldname]" class="p-0 link_line_action1"
                  @click="onOpenLink(c, slotProps.data)" link>
                  {{ slotProps.data[c.fieldname] }}
                  <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                  <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </Button>
                <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
                  moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                <span v-else-if="c.fieldtype == 'Datetime'">
                  {{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a") }}
                </span>
                <!-- <Timeago v-else-if="c.fieldtype == 'Timeago'" :datetime="slotProps.data[c.fieldname]" long></Timeago> -->
                <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
                <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                  v-if="slotProps?.data && slotProps?.data?.rooms">
                  <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                    <span>{{ item }}</span>
                    <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                  </template>
                </div>
                <template v-else-if="c.fieldtype == 'Status'">

                  <Chip class="text-white bg-black-alpha-90 p-1px px-2" v-if="slotProps.data[c.fieldname] == 1">
                    <i class="pi pi-lock-open me-2" />
                    Unblock
                  </Chip>
                  <Chip class="text-white bg-black-alpha-90 p-1px px-2" v-else><i class="pi pi-lock me-2" />Block</Chip>
                </template>
                <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                <span v-else-if="c.fieldtype == 'reservation_status'"
                  class="px-2 rounded-lg text-white p-1px border-round-3xl"
                  :style="`background: ${slotProps.data.reservation_status_color}`">{{ slotProps.data[c.fieldname]
                  }}</span>
                <span v-else-if="c.fieldtype == 'username'">{{ slotProps.data[c.fieldname].split("@")[0] }}</span>
                <span v-else>
                  {{ slotProps.data[c.fieldname] }}
                  <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                  <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </span>
              </template>
            </Column>
          </DataTable>
        </div>
      </ComPlaceholder>
    </div>

  </ComOwnerContentTitle>

</template>
<script setup>
import ComOwnerContentTitle from '@/views/dashboard/components/ComOwnerContentTitle.vue'
import { inject, ref, getCount, getDocList, onMounted, getApi, computed, onUnmounted, defineProps, watch } from '@/plugin'
import { Timeago } from 'vue2-timeago'
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
const gv = inject("$gv")
const data = ref([])
const filter = ref({})
const loading = ref(false)
const selectedColumns = ref([])
const working_date = JSON.parse(localStorage.getItem("edoor_working_day"))
const activeIndex = ref(0);
const property = window.property
const props = defineProps({
  date: {
    type: Date,
  },
});
const isMobile = ref(window.isMobile)
const columns = ref([
  { fieldname: 'name', label: 'Transaction #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_folio_transaction_detail", default: true },
  { fieldname: 'room_number', label: 'Rooms', header_class: "text-center", default: true },
  { fieldname: 'transaction_type', label: 'Transaction Type', default: true, header_class: "transaction_type" },
  { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
  { fieldname: 'account_code', extra_field: "account_name", extra_field_separator: "-", label: 'Account Code', default: true },
  { fieldname: 'amount', label: 'Amount', header_class: "text-right", fieldtype: "Currency", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
  { fieldname: 'discount_amount', label: 'Total Discount', header_class: "text-right", fieldtype: "Currency", default: true },
  { fieldname: 'total_tax', label: 'Total Tax', header_class: "text-right", fieldtype: "Currency", default: true },
  { fieldname: 'bank_fee', label: 'Bank Fee', header_class: "text-right", fieldtype: "Currency", default: true },
  { fieldname: 'total_amount', label: 'Total Amount', header_class: "text-right", fieldtype: "Currency", default: true },
  { fieldname: 'modified_by', label: 'Modifield By', header_class: "text-left", default: true, fieldtype: "username" },
  { fieldname: 'modified', label: 'Last Modifield', fieldtype: "Timeago", header_class: "text-left", default: true },
  { fieldname: 'reservation_status', label: 'Status', header_class: "text-center", fieldtype: "reservation_status" },
  { fieldname: 'posting_date', label: 'Date', header_class: "text-center", fieldtype: "Date" },
  { fieldname: 'payment_by', label: 'Pay by' },
  { fieldname: 'payment_by_phone_number', label: 'Phone Number' },

])


function onOpenLink(column, data) {
  window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

const Refresh = debouncer(() => {
  pageState.value.page = 0
  loadData();
}, 500);

let filters = [
  ["property", "=", property.name],
  ["parent_reference", "is", "not set"],
  ["posting_date", "=", props.date || moment(working_date).format('YYYY-MM-DD')],
]
watch(() => props.date, (newDate) => {
  if (newDate) {
    filters = [
      ["property", "=", property.name],
      ["parent_reference", "is", "not set"],
      ["posting_date", "=", props.date || moment(working_date).format('YYYY-MM-DD')],
    ]
    loadData();
  }
});
function onFilterFolioTransaction(transaction_type, index) {
  activeIndex.value = index;
  if (transaction_type != "All") {

    filters = [
      ["property", "=", property.name],
      ["parent_reference", "is", "not set"],
      ["posting_date", "=", props.date || moment(working_date).format('YYYY-MM-DD')],
    ]
    filter.value.transaction_type = transaction_type
  } else {
    filter.value.transaction_type = ''
    filters = [
      ["property", "=", property.name],
      ["parent_reference", "is", "not set"],
      ["posting_date", "=", props.date || moment(working_date).format('YYYY-MM-DD')],
    ]
  }
  loadData();
}
function loadData() {
  loading.value = true

  if (filter.value?.transaction_type) {
    filters.push(["transaction_type", '=', filter.value.transaction_type])

  }


  let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
  fields = [...fields, ...selectedColumns.value]
  fields = [...new Set(fields.filter(x => x))]
  fields.push("reservation_status_color")

  getDocList('Folio Transaction', {
    fields: fields,
    orderBy: {
      field: '`tabFolio Transaction`.modified',
      order: "desc",
    },
    filters: filters,
    limit: 20,
  })
    .then((doc) => {
      data.value = doc
      loading.value = false
    })
    .catch((error) => {
      loading.value = false

    });



}


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

onMounted(() => {

  selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)

  columns.value.forEach(r => {
    r.selected = selectedColumns.value.includes(r.fieldname)
  });
  loadData()
  getApi("frontdesk.get_meta", { doctype: "Folio Transaction" }).then((result) => {
    result.message.fields.filter(r => r.in_list_view == 1 && !columns.value.map(x => x.fieldname).includes(r.fieldname)).forEach(r => {
      let header_class = ""

      if (["Date", "Int"].includes(r.fieldtype)) {
        header_class = "text-center"
      } else if (["Currency"].includes(r.fieldtype)) {
        header_class = "text-right"
      }

      columns.value.push({
        fieldname: r.fieldname,
        label: r.label,
        fieldtype: r.fieldtype.toLowerCase(),
        header_class: header_class,
        selected: selectedColumns.value.includes(r.fieldname)
      })


    })

  })



})




</script>