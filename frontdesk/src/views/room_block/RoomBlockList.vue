<template>
  <div>
    <ComHeader isRefresh @onRefresh="Refresh()">
      <template #start>
        <div class="text-2xl">Block Room</div>
      </template>
      <template #end>
        <Button @click="onAddNewRommBlock()">Add New Room Block</Button>
      </template>
    </ComHeader>
    <div class="mb-3">
      <div class="flex flex-wrap gap-2">
        <span class="p-input-icon-left">
          <i class="pi pi-search" />
          <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
        </span>
        <div class="col p-0">
          <ComSelect v-model="filter.search_date_type" :options="dataTypeOptions" optionLabel="label"
          optionValue="value" placeholder="Search Date Type" :clear="false"
          @onSelectedValue="onSelectFilterDate($event)"></ComSelect>
          <Calendar hideOnRangeSelection v-if="filter.search_date_type" dateFormat="dd-MM-yy"
          v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
          placeholder="Select Date Range" />


          <ComSelect :filters="[['property', '=', property.name]]" optionLabel="room_number" optionValue="name" v-model="filter.selected_room_id" @onSelected="onSearch"
            placeholder="Room" doctype="Room" isFilter />
          <ComSelect :filters="[['property', '=', property.name]]" v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type"
            doctype="Room Type" isFilter 
            optionLabel="room_type" optionValue="name"
            />
        </div>
        <ComOrderBy doctype="Room Block" @onOrderBy="onOrderBy" />
      </div>
    </div>
    <Button label="Show Column" @click="toggleShowColumn" />
    <Button label="Reset List" @click="onResetTable" />

    <DataTable resizableColumns columnResizeMode="fit" showGridlines stateStorage="local"
      stateKey="table_room_block_list_state" :reorderableColumns="true" :value="data" tableStyle="min-width: 50rem"
      @row-dblclick="onViewReservationStayDetail">
      <Column v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.header)" :key="c.fieldname"
        :field="c.fieldname" :header="c.header" :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''"
        :frozen="c.frozen">
        <template #body="slotProps">
          <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
            {{ slotProps.data[c.fieldname] }}
            <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
            <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
          </Button>
          <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
            moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
          <span v-else-if="c.fieldtype == 'datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a") }}
          </span>
          <Timeago v-else-if="c.fieldtype == 'Timeago'" :datetime="slotProps.data[c.fieldname]" long></Timeago>
          <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
            v-if="slotProps?.data && slotProps?.data?.rooms">
            <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
              <span>{{ item }}</span>
              <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
            </template>
          </div>
          <template v-else-if="c.fieldtype == 'Status'">
             
            <Chip v-if="slotProps.data[c.fieldname]==1">
              Unblock
            </Chip>
            <Chip v-else>Block</Chip>
          </template>
          <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
          <span v-else>
            {{ slotProps.data[c.fieldname] }}
            <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
            <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
          </span>
        </template>
      </Column>

    </DataTable>
  </div>

  <Paginator :rows="pageState.rows" :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]"
    @page="pageChange">
    <template #start="slotProps">
      Total Records: {{ pageState.totalRecords }}
    </template>
  </Paginator>

  <OverlayPanel ref="opShowColumn">
    <InputText v-model="filter.search_field" placeholder="Search" />
    <div v-for="(c, index) in getColumns.filter(r => r.header)" :key="index">

      <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
      <label :for="c.fieldname">{{ c.header }}</label>
    </div>
    <Button @click="OnSaveColumn">Save</Button>
  </OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, getApi, useDialog, computed } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'
import ComEditRoomBlock from "../../views/room_block/components/ComEditRoomBlock.vue";
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const gv = inject("$gv")
const toast = useToast()
const dialog = useDialog()
const opShowColumn = ref();
const socket = inject("$socket")
const data = ref([])
const filter = ref({})
const selectedColumns = ref([]);
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))


socket.on("RefreshGuestDatabase", (arg) => {

  if (arg == property.name) {
    loadData()

  }
})

const columns = ref([
  { fieldname: 'name', header: 'Room Block Code', fieldtype: "Link", post_message_action: "view_room_block_detail", default: true },
  { fieldname: 'block_date', header: 'Block Date', fieldtype: "Date", default: true },
  { fieldname: 'start_date', header: 'Start Date', fieldtype: "Date ", default: true },
  { fieldname: 'end_date', header: 'Release Date', fieldtype: "Date", default: true },
  { fieldname: 'room_number', header: 'Room Number', default: true },
  { fieldname: 'room_type', header: 'Room Type', default: true },
  { fieldname: 'reason', header: 'Reason', default: true },
  { fieldname: 'unblock_date', header: 'Unblock Date', fieldtype: "Date", default: true },
  { fieldname: 'unblock_note', header: 'Unblock Note', default: true },
  { fieldname: 'is_unblock', fieldtype:"Status", header: 'Status', default: true },

])

const getColumns = computed(()=>{
    if (filter.value.search_field){ 
        return columns.value.filter(r=>(r.label ||"").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    }else {
        return columns.value.filter(r=>r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

let dateRange = reactive({
    start: '',
    end: ''
})
const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Block Date', value: 'block_date' },
    { label: 'Start Date', value: 'start_date' },
    { label: 'Release Date', value: 'end_date' },
    { label: 'Unblock Date', value: 'unblock_date' },
  ])
  function onDateSelect() {
    if (filter.value.date_range && filter.value.date_range[0] && filter.value.date_range[1]) {
        dateRange.start = moment(filter.value.date_range[0]).format("YYYY-MM-DD")
        dateRange.end = moment(filter.value.date_range[1]).format("YYYY-MM-DD")
        loadData()
    }
}
const toggleShowColumn = (event) => {
  opShowColumn.value.toggle(event);
}
function OnSaveColumn(event) {
  selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
  pageState.value.selectedColumns = selectedColumns.value
  localStorage.setItem("page_state_room_block", JSON.stringify(pageState.value))
  opShowColumn.value.toggle(event);
}


function onResetTable() {
  localStorage.removeItem("page_state_room_block")
  localStorage.removeItem("table_room_block_list_state")
  window.location.reload


}

function onOpenLink(column, data) {
  window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

function Refresh() {
  pageState.value.page = 0
  loadData()
}

function pageChange(page) {
  pageState.value.page = page.page
  pageState.value.rows = page.rows

  loadData()
}

function loadData() {
  gv.loading = true
  let filters = [
    ["property","=",property.name]
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
  if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }
  let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
  fields = [...fields, ...selectedColumns.value]
  fields = [...new Set(fields.filter(x => x))]

  getDocList('Room Block', {
    fields: fields,
    orderBy: {
      field: '`tabRoom Block`.' + pageState.value.order_by,
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

  localStorage.setItem("page_state_room_block", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

  getCount('Room Block', filters)

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
  let state = localStorage.getItem("page_state_room_block")
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
  getApi("frontdesk.get_meta", { doctype: "Room Block" }).then((result) => {
    console.log(result.message)
    result.message.fields.filter(r => r.in_list_view == 1 && !columns.value.map(x => x.fieldname).includes(r.fieldname)).forEach(r => {
      let header_class = ""

      if (["Date", "Int"].includes(r.fieldtype)) {
        header_class = "text-center"
      } else if (["Currency"].includes(r.fieldtype)) {
        header_class = "text-right"
      }

      columns.value.push({
        fieldname: r.fieldname,
        header: r.label,
        fieldtype: r.fieldtype.toLowerCase(),
        header_class: header_class,
        selected: selectedColumns.value.includes(r.fieldname)
      })
    })
  })

})
function onAddNewRommBlock() {
    dialog.open(ComEditRoomBlock, {
        data:{
          
        },
        props: {
            header: 'Add New Room Block ',
            style: {
                width: '50vw',
            },
            modal: true,
            position:'top',
            closeOnEscape: false
        },
        onClose: (options) => {
            const result = options.data;
            if(result){
                loadData()
            }
        }
    })
}
</script>