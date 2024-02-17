<template>
  <div class="flex-col flex" style="height: calc(100vh - 92px);">
    <div>
      <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
        <template #start>
          <div class="text-xl md:text-2xl">Block Room</div>
        </template>
        <template #end>
          <Button class="border-none" @click="onAddNewRommBlock()">Add New Room Block</Button>
        </template>
      </ComHeader>
      <div class="mb-3 flex justify-between">
        <div class="flex gap-2">
          <div v-if="!isMobile" class="w-20rem">
            <div class="w-full p-input-icon-left">
              <i class="pi pi-search" />
              <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
            </div>
          </div>
          <div>
            <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceSearch" />
          </div>
          <div v-if="gv.isNotEmpty(filter, 'search_date_type')">
            <Button class="content_btn_b" :label="isMobile ? 'Clear' : 'Clear Filter' " icon="pi pi-filter-slash" @click="onClearFilter" />
          </div>
        </div>
        
        <div class="flex">
          <div class="px-2">
            <ComOrderBy doctype="Room Block" @onOrderBy="onOrderBy" />
          </div>
          <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
            <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
          </Button>
        </div>
      </div>
    </div>
    <div class="overflow-auto h-full">
      <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="data.length > 0">
        <DataTable class="res_list_scroll" :resizableColumns="true" columnResizeMode="expand" showGridlines
          stateStorage="local" scrollable stateKey="table_room_block_list_state" :reorderableColumns="true" :value="data"
          tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail" scrollHeight="70vh">
          <Column v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname"
            :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''"
            :frozen="c.frozen">
            <template #body="slotProps">
              <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)"
                link>
                {{ slotProps.data[c.fieldname] }}
                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
              </Button>

              <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">
                {{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }}
              </span>
              <span v-else-if="c.fieldtype == 'Datetime'">
                {{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a")}}
              </span>
              <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
              <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                v-if="slotProps?.data && slotProps?.data?.rooms">
                <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                  <span>{{ item }}</span>
                  <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                </template>
              </div>
              <template v-else-if="c.fieldtype == 'Status'"> 
                <Chip class="text-white surface-400 p-1px px-2" v-if="slotProps.data[c.fieldname] == 1"><i class="pi pi-lock-open me-2" /> Unblock</Chip>    
                <Chip class="text-white bg-black-alpha-90 p-1px px-2" v-else-if="slotProps.data[c.extra_field] == 1"><i class="pi pi-lock me-2" />Block</Chip>
                <Chip class="text-white bg-orange-500 p-1px px-2" v-else-if="slotProps.data[c.extra_field] == 0"><i class="pi pi-file-edit me-2" />Draft</Chip>
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
  <OverlayPanel ref="showAdvanceSearch" >
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
      icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
      <div class="grid">
        <div v-if="isMobile" class="col-12">
            <div class="w-full p-input-icon-left">
              <i class="pi pi-search" />
              <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
            </div>
          </div>
        <ComSelect class="col-6" width="100%" :options="['Draft','Blocked','Unblocked']" v-model="filter.block_status" @onSelected="onSearch" placeholder="Block Status" />
        <ComSelect class="col-6" width="100%" :filters="[['property', '=', property.name]]" optionLabel="room_number"
          optionValue="name" v-model="filter.selected_room_id" @onSelected="onSearch" placeholder="Room" doctype="Room"
          isFilter />
        <ComSelect class="col-6" width="100%" :filters="[['property', '=', property.name]]"
          v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type" doctype="Room Type" isFilter
          optionLabel="room_type" optionValue="name" />
 
        <ComSelect class="col-6" width="100%" v-model="filter.search_date_type" :options="dataTypeOptions"
          optionLabel="label" optionValue="value" placeholder="Search Date Type" :clear="false"
          @onSelectedValue="onSelectFilterDate($event)"></ComSelect>
         
        <div class="col-6" v-if="filter.search_date_type">
          <Calendar selectOtherMonths class="w-full" hideOnRangeSelection dateFormat="dd-mm-yy"
            v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
            placeholder="Select Date Range" />
        </div>
      </div>
    </ComOverlayPanelContent>
  </OverlayPanel>
</template>
<script setup>
import { inject, ref, reactive, getCount, getDocList, onMounted, getApi, useDialog, computed,onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import { Timeago } from 'vue2-timeago'
import ComEditRoomBlock from "@/views/room_block/components/ComEditRoomBlock.vue";
const moment = inject("$moment")
const gv = inject("$gv")
const dialog = useDialog()
const opShowColumn = ref()
const data = ref([])
const filter = ref({})
const showAdvanceSearch = ref()
const selectedColumns = ref([]);
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))
const isMobile = ref(window.isMobile) 
const columns = ref([
  { fieldname: 'name', label: 'Room Block Code', header_class: "text-center", fieldtype: "Link", post_message_action: "view_room_block_detail", default: true },
  { fieldname: 'block_date', label: 'Block Date', header_class: "text-center", fieldtype: "Date", default: true },
  { fieldname: 'start_date', label: 'Start Date', header_class: "text-center", fieldtype: "Date", default: true },
  { fieldname: 'end_date', label: 'Release Date', header_class: "text-center", fieldtype: "Date", default: true },
  { fieldname: 'room_number', label: 'Room Number', header_class: "text-center", default: true },
  { fieldname: 'room_type', label: 'Room Type', default: true },
  { fieldname: 'total_night_count', label: 'Total Night(s)', header_class: "text-center", default: true },
  { fieldname: 'reason', label: 'Reason', default: true },
  { fieldname: 'unblock_date', label: 'Unblock Date', fieldtype: "Date", header_class: "text-center", default: true },
  { fieldname: 'unblock_note', label: 'Unblock Note', default: true },
  { fieldname: 'is_unblock',extra_field:'docstatus', fieldtype: "Status", label: 'Status', header_class: "text-center", default: true },

])

const getColumns = computed(() => {
  if (filter.value.search_field) {
    return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
  } else {
    return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
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
  window.location.reload()


}

function onOpenLink(column, data) {
  window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

const Refresh = debouncer(() => {
  pageState.value.page = 0
  loadData()
}, 500);
function pageChange(page) {
  pageState.value.page = page.page
  pageState.value.rows = page.rows

  loadData()
}

function loadData(show_loading=true) {
   
  gv.loading = show_loading
  let filters = [
    ["property", "=", property.name]
  ]
  if (filter.value?.keyword) {
    filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
  }
  if(filter.value.block_status){
    if(filter.value.block_status == 'Draft'){
      filters.push(["docstatus","=",0])
      filters.push(["is_unblock","=",0])
    }
    else if(filter.value.block_status == 'Blocked'){
      filters.push(["docstatus","=",1])
      filters.push(["is_unblock","=",0])
    }
    else if(filter.value.block_status == 'Unblocked'){
      filters.push(["is_unblock","=",1])
    }
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

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="RoomBlockList"){
            setTimeout(()=>{
              loadData(false)
            },1000*3)
            
        }
    };
}  
onMounted(() => {
  if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
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
function onAddNewRommBlock(room_block) {
  if(!gv.cashier_shift?.name){
        gv.toast('error', 'Please Open Cashier Shift.')
        return
    }
  dialog.open(ComEditRoomBlock, {
    data: { name: room_block },
    props: {
      header: 'Add New Room Block ',
      style: {
        width: '50vw',
      },
      modal: true,
      position: 'top',
      closeOnEscape: false,
      breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
    },
    onClose: (options) => {
      const result = options.data;
      if (result) {
        loadData()
        window.postMessage("view_room_block_detail|" + result.name, "*")
      }
    }
  })
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
  window.removeEventListener('message', actionRefreshData, false)
})
</script>