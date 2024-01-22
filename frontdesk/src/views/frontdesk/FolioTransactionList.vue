<template>
  <div class="flex-col flex" style="height: calc(100vh - 92px);">
    <div>
      <ComHeader isRefresh @onRefresh="Refresh()">
        <template #start>
          <div class="text-2xl">Folio Transaction</div>
        </template>

      </ComHeader>
      <div class="mb-3 flex justify-between">
        <div class="flex gap-2">
          <div>
            <div class="p-input-icon-left">
              <i class="pi pi-search" />
              <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
            </div>
          </div>
          <div>
            <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceSearch" />
          </div>
          
        </div>
        <div class="flex">
          <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
            <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter" />
          </div>
          <div class="px-2">
            <ComOrderBy doctype="Folio Transaction" @onOrderBy="onOrderBy" />
          </div>
          <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
            <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
          </Button>
        </div>
      </div>
    </div>
    <div class=" h-full"> 
      <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data.length > 0">
        <DataTable class="res_list_scroll" :resizableColumns="true" columnResizeMode="expand" showGridlines
          stateStorage="local" stateKey="table_folio_transaction_list_state" :reorderableColumns="true" :value="data"
          tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail" scrollHeight="70vh">
          <Column
            v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes') == 'Yes')"
            :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''"
            :bodyClass="c.header_class || ''" :frozen="c.frozen">
            <template #body="slotProps">
              <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1"
                  @click="onOpenLink(c, slotProps.data)" link>
                  {{ slotProps.data[c.fieldname] }}
                  <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                  <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
              </Button>
              <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
              <span v-else-if="c.fieldtype == 'Datetime'">
              {{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a")}}
              </span>
              <!-- <Timeago v-else-if="c.fieldtype == 'Timeago'" :datetime="slotProps.data[c.fieldname]" long></Timeago> -->
              <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]"/>
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
              <span v-else-if="c.fieldtype=='reservation_status'" class="px-2 rounded-lg text-white p-1px border-round-3xl" :style="`background: ${slotProps.data.reservation_status_color}`">{{ slotProps.data[c.fieldname] }}</span>
              <span v-else-if="c.fieldtype=='username'" >{{ slotProps.data[c.fieldname].split("@")[0] }}</span>
              <span v-else>
                    {{ slotProps.data[c.fieldname] }}
                    <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                    <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </span>
            </template>
          </Column>
        </DataTable>
      </ComPlaceholder>
    </div>
    <div>
      <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows"
        :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange">
        <template #start="slotProps">
          <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
        </template>
      </Paginator>
    </div>
  </div>
  <OverlayPanel ref="opShowColumn" style="width:30rem;">
    <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save"
      @onCancel="onCloseColumn">
      <template #top>
        <span class="p-input-icon-left w-full mb-3">
          <i class="pi pi-search" />
          <InputText class="w-full flex-nowrap" v-model="filter.search_field" placeholder="Search" />
        </span>
      </template>
      <div class="grid">
        <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
          <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
          <label :for="c.fieldname">{{ c.label }}</label>
        </div>
      </div>
      <template #footer-left>
        <Button class="border-none" label="Reset List" @click="onResetTable" />
      </template>
    </ComOverlayPanelContent>
  </OverlayPanel>

  <OverlayPanel ref="showAdvanceSearch" style="width:50rem">
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
      icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
      <div class="grid">
        <ComSelect class="col-6" width="100%" :filters="[['property', '=', property.name]]" optionLabel="room_number"
          optionValue="name" v-model="filter.selected_room_id" @onSelected="onSearch" placeholder="Room" doctype="Room"
          isFilter />
        <ComSelect class="col-6" width="100%" :filters="[['property', '=', property.name]]"
          v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type" doctype="Room Type" isFilter
          optionLabel="room_type" optionValue="name" />
        <div class="col-6">
          <div class="flex relative">
            <Calendar :selectOtherMonths="true" class="w-full" inputClass="pl-6" hideOnRangeSelection
              dateFormat="dd-mm-yy" v-model="filter.date_range" selectionMode="range" :manualInput="false"
              @date-select="onDateSelect" placeholder="Select Date Range" :disabled="!filter.search_by_date" showIcon />
            <div class="check-box-filter">
              <Checkbox v-model="filter.search_by_date" :binary="true" @change="onChecked" />
            </div>
          </div>
        </div>
      </div>
    </ComOverlayPanelContent>
  </OverlayPanel>
</template>
<script setup>
import { inject, ref, getCount, getDocList, onMounted, getApi, computed, onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'

const moment = inject("$moment")
const gv = inject("$gv")
const opShowColumn = ref();
const data = ref([])
const filter = ref({})
const showAdvanceSearch = ref()
const selectedColumns = ref([]);
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const property = window.property

const columns = ref([
  { fieldname: 'name', label: 'Folio Transaction', header_class: "text-center", fieldtype: "Link", post_message_action: "view_folio_transaction_detail", default: true },
  { fieldname: 'reservation', label: 'Reservation #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_detail", default: true },
  { fieldname: 'reservation_stay', label: 'Stay #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_stay_detail", default: true },
  { fieldname: 'transaction_number', label: 'Folio #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_folio_detail", default: true },
  { fieldname: 'room_number', label: 'Rooms', header_class: "text-center", default: true },
  { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
  { fieldname: 'account_code', extra_field: "account_name", extra_field_separator: "-", label: 'Account Code', default: true },
  { fieldname: 'amount', label: 'Amount', header_class: "text-right", fieldtype: "Currency", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
  { fieldname: 'discount_amount', label: 'Total Discount', header_class: "text-right",fieldtype:"Currency", default: true },
  { fieldname: 'total_tax', label: 'Total Tax', header_class: "text-right",fieldtype:"Currency", default: true },
  { fieldname: 'bank_fee', label: 'Bank Fee', header_class: "text-right",fieldtype:"Currency", default: true },
  { fieldname: 'total_amount', label: 'Total Amount', header_class: "text-right",fieldtype:"Currency", default: true },
  { fieldname: 'modified_by', label: 'Modifield By', header_class: "text-left", default: true,fieldtype:"username" },
  { fieldname: 'modified', label: 'Last Modifield', fieldtype: "Timeago", header_class: "text-left", default: true },
  { fieldname: 'reservation_status', label: 'Status', header_class: "text-center", fieldtype:"reservation_status" },
  { fieldname: 'posting_date', label: 'Date', header_class: "text-center", fieldtype: "Date" },
  { fieldname: 'payment_by', label: 'Pay by'},
  { fieldname: 'payment_by_phone_number', label: 'Phone Number'},

])

const getColumns = computed(() => {
  if (filter.value.search_field) {
    return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
  } else {
    return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
  }
})



function onDateSelect() {
  if (filter.value.date_range && filter.value.date_range[1]) {
    loadData()
  }
}
function onChecked() {
  if (!filter.value.search_by_date) {
    filter.value.date_range = null
  }
  if (!filter.value.search_by_date) {
    loadData()
  } else {
    onDateSelect()
  }
}
const toggleShowColumn = (event) => {
  opShowColumn.value.toggle(event);
}
function OnSaveColumn(event) {
  selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
  pageState.value.selectedColumns = selectedColumns.value
  localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value))
  opShowColumn.value.toggle(event);
}


function onResetTable() {
  localStorage.removeItem("page_state_folio_transaction")
  localStorage.removeItem("table_folio_transaction_list_state")
  window.location.reload()


}

function onOpenLink(column, data) {
  window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}


const Refresh = debouncer(() => {
  pageState.value.page = 0
  loadData();
}, 500);

function pageChange(page) {
  pageState.value.page = page.page
  pageState.value.rows = page.rows

  loadData()
}

function loadData(showLoading = true) {
  gv.loading = showLoading
  let filters = [
    ["property", "=", property.name],
    ["parent_reference","is","not set"],
    ["transaction_type","=","Reservation Folio"],
  ]
  if (filter.value?.keyword) {
    filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
  }
  if (filter.value?.selected_room_id) {
    filters.push(["room_id", '=', filter.value.selected_room_id])
  }
  if (filter.value?.selected_room_type) {
    filters.push(["room_type_id", '=', filter.value.selected_room_type])
  }
  if (filter.value.date_range && filter.value.search_by_date) {
    filters.push(['posting_date', 'between', [moment(filter.value.date_range[0]).format("YYYY-MM-DD"), moment(filter.value.date_range[1]).format("YYYY-MM-DD")]])
  }



  let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
  fields = [...fields, ...selectedColumns.value]
  fields = [...new Set(fields.filter(x => x))]
  fields.push("reservation_status_color")

  getDocList('Folio Transaction', {
    fields: fields,
    orderBy: {
      field: '`tabFolio Transaction`.' + pageState.value.order_by,
      order: pageState.value.order_type,
    },
    filters: filters,
    limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
    limit: pageState.value?.rows || 20,
  })
    .then((doc) => {
      data.value = doc
      gv.loading = false
    })
    .catch((error) => {
      gv.loading = false

    });

  getTotalRecord(filters)

  localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

  getCount('Folio Transaction', filters)

    .then((count) => {
      pageState.value.totalRecords = count || 0
    })

}
function onOrderBy(data) {
  pageState.value.order_by = data.order_by
  pageState.value.order_type = data.order_type
  pageState.value.page = 0
  loadData()

}

function onSelectFilterDate(event) {
  filter.value.search_date_type = event
  if (filter.value.search_date_type == '')
    filter.value.date_range = null
  loadData()
}

const onSearch = debouncer(() => {
  loadData();
}, 500);

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
  let state = localStorage.getItem("page_state_folio_transaction")
  if (state) {
    state = JSON.parse(state)
    state.page = 0
    pageState.value = state
    if (state.selectedColumns) {
      selectedColumns.value = state.selectedColumns

    } else {
      selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
    }
  } else {
    selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
  }
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
 
  window.addEventListener('message', actionRefreshData, false);

})

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="FolioTransactionList"){
            setTimeout(()=>{
              loadData(false)
            },1000*3)
            
        }
    };
}

const advanceSearch = (event) => {
  showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
  filter.value = {}
  loadData()
  showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
  showAdvanceSearch.value.hide()
}

const onCloseColumn = () => {
  opShowColumn.value.hide()
}

onUnmounted(() => {
  window.removeEventListener('message', actionRefreshData, false);
})

</script>