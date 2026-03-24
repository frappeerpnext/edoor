<template>
  <div
    class="availability-container"
    ref="container"
    @mousedown="onMouseDown"
    @mousemove="onMouseMove"
    @mouseup="onMouseUp"
    @mouseleave="onMouseUp"
  >
  
    <div class="grid-wrapper" ref="gridWrapper" @scroll="onWrapperScroll">
      <!-- Header row with sticky left column and virtual columns -->
      <div class="header-row">
        <div class="sticky-left room-type-header">Room Type</div>
        <div class="columns-scroller">
          <RecycleScroller
            :key="datesKey"
            ref="headerScroller"
            :items="dates"
            :item-size="CELL_WIDTH"
            :buffer="BUFFER"
            key-field="date"
            direction="horizontal"
            @scroll.native="onScrollerScroll"
            class="no-scroll"
          >
            <template #default="{ item: date, index: colIndex }">
              <div
                class="header-cell"
                :data-col="colIndex"
                v-html="formatDateHeader(date)"
              ></div>
            </template>
          </RecycleScroller>
        </div>
      </div>

      <!-- Body rows -->
      <div
        v-for="(rt, rowIndex) in roomTypes"
        :key="rt.name"
        class="body-row"
      >
        <div class="sticky-left room-type-cell">
          <div>Open/Close {{ rt.room_type }}</div>
          <div>PMS Availability</div>
        </div>
        <!-- render date and value -->
        <div class="columns-scroller">
          <RecycleScroller
          :key="datesKey"
            :items="dates"
            :item-size="CELL_WIDTH"
            :buffer="BUFFER"
            direction="horizontal"
            :scroll-data="scrollData"
            @scroll.native="onScrollerScroll"
             :class="rowIndex == (roomTypes.length - 1)?'last_row':'no-scroll'"
          >
            <template #default="{ item: date, index: colIndex }">
              <div
                class="cell"
                :data-row="rowIndex"
                :data-col="colIndex"
                :class="{ selected: isSelected(rowIndex, colIndex) }"
              >
                <div>
                  <template v-if="isCellLoading(rt.name, date)">
                    <ProgressSpinner  style="width:15px;height:15px"/>
                  </template>
                  <template v-else>
 <i @click="onUpdateStatus(rt.name,date,1)"  class="pi pi-check-circle" v-if="getStopSaleValue(rt.name, date)==0" style="font-size: 1rem;color:green"></i>
                  <i @click="onUpdateStatus(rt.name,date,0)" class="pi pi-ban" style="font-size: 1rem;color:red" v-else></i>
                 
                  </template>
                   
                </div>
                 
                <div>{{ getValue(rt.name, date) }}</div>
               
              </div>
            </template>
          </RecycleScroller>
        </div>
      </div>
    </div>

    <div v-if="dragging" class="selection-rect" :style="rectStyle"></div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch,inject, render } from "vue";
import { RecycleScroller } from "vue-virtual-scroller";
import "vue-virtual-scroller/dist/vue-virtual-scroller.css";

import ProgressSpinner from 'primevue/progressspinner';

const moment = inject('$moment')

const props = defineProps({
  startDate: String,
  endDate: String,
  roomTypes: Array,
  data: Array,
  
});
const emit = defineEmits(["update:selected"]);
const datesKey = computed(() => `${props.startDate}_${props.endDate}`);


// ---------- Dates ----------
const dates = ref([])

// ---------- Data ----------
const dataMap = computed(() => {
  const map = {};
  props.data.forEach((d) => {
   
    map[`${d.room_type_id}_${d.date}`] = d.value;
  });
  return map;
});
const getValue = (room, date) => dataMap.value[`${room}_${date}`] ?? 0;

const dataStopSale = computed(() => {
  const map = {};
  props.data.forEach((d) => {
   
    map[`${d.room_type_id}_${d.date}`] = d.stop_sale;
  });
  return map;
});
const getStopSaleValue = (room, date) => dataStopSale.value[`${room}_${date}`] ?? 0;

function isCellLoading(room_type,date){
    const updatedData = props.data?.find(x=>x.room_type_id == room_type && x.date == date)
    return updatedData?.loading || false

  
}

// ---------- Date Header ----------
const formatDateHeader = (d) => {
  const date = new Date(d);
  const month = date.toLocaleString("en-US", { month: "short" });
  const day = date.getDate().toString().padStart(2, "0");
  const dayName = date.toLocaleString("en-US", { weekday: "short" });
  return `${month}<br>${day}<br>${dayName}`;
};

 

/**
 * Clears all selections.
 */
const clearSelections = () => {
  selected.value.clear();
  emit("update:selected", []);
};

const onUpdateStatus = (room_type_id,date,status) => {
  
  emit("onUpdateStatus", {room_type_id:room_type_id,date:date,status:status});
};


// ---------- Dimensions ----------
const STICKY_WIDTH = 250;
const CELL_WIDTH = 35;
const BUFFER = 10; // extra columns to render outside viewport

// Column positions (absolute left of each date column)
const columnPositions = computed(() => {
  const positions = [];
  for (let i = 0; i < dates.value.length; i++) {
    positions.push(STICKY_WIDTH + i * CELL_WIDTH);
  }
  return positions;
});

// ---------- Virtual scrolling ----------
const gridWrapper = ref(null);
const container = ref(null);
const scrollLeft = ref(0);
const headerScroller = ref(null);
// We need to sync scroll between header and rows. RecycleScroller uses scroll event.
// We'll store the scroll position and apply to all scrollers.
const scrollData = ref({ scrollLeft: 0 });

const onScrollerScroll = (event) => {
  const target = event.target;
  scrollLeft.value = target.scrollLeft;
  // Update all scrollers to the same position
  const scrollers = document.querySelectorAll('.columns-scroller .vue-recycle-scroller');
  scrollers.forEach((scroller) => {
    if (scroller !== target) {
      scroller.scrollLeft = scrollLeft.value;
    }
  });
  scrollData.value = { scrollLeft: scrollLeft.value };
};

// When wrapper scrolls (vertical), we only need to handle vertical sync (none needed)
const onWrapperScroll = () => {
  // Not needed for columns, but we keep for completeness
};

// ---------- Selection ----------
const selected = ref(new Set());
const dragging = ref(false);
const isMouseDown = ref(false);
const mode = ref("select");
const startCell = ref(null);
const endCell = ref(null);
const startPoint = ref({ x: 0, y: 0 });
const DRAG_THRESHOLD = 5;

const key = (r, c) => `${r}_${c}`;
const isSelected = (row, col) => selected.value.has(key(row, col));

function renderDates(){
  const result = [];
  dates.value = []
  let current = moment.utc(moment(props.startDate).format("YYYY-MM-DD")).toDate()
  const end = moment.utc(moment(props.endDate).format("YYYY-MM-DD")).toDate()
   
  while (current <= end) {
    result.push(moment(current).format("YYYY-MM-DD"));
    current =  moment(current).add(1, 'day');
    
  }

  dates.value = result
 
}

watch([() => props.startDate, () => props.endDate], () => {
  renderDates();
  clearSelections();
}, { immediate: true });

// Get cell from mouse coordinates (works for off‑screen columns)
const getCellFromPosition = (clientX, clientY) => {
  const containerRect = container.value.getBoundingClientRect();
  const gridRect = gridWrapper.value.getBoundingClientRect();
  const scroll = scrollLeft.value;

  // Row
  const rows = document.querySelectorAll(".body-row");
  let rowIndex = -1;
  for (let i = 0; i < rows.length; i++) {
    const rect = rows[i].getBoundingClientRect();
    if (clientY >= rect.top && clientY <= rect.bottom) {
      rowIndex = i;
      break;
    }
  }
  if (rowIndex === -1) return null;

  // Column: x relative to grid content
  const x = clientX - gridRect.left + scroll;
  if (x < STICKY_WIDTH) return null; // ignore sticky column
  // binary search in columnPositions
  let colIndex = -1;
  for (let i = 0; i < columnPositions.value.length; i++) {
    const left = columnPositions.value[i];
    const right = left + CELL_WIDTH;
    if (x >= left && x <= right) {
      colIndex = i;
      break;
    }
  }
  if (colIndex === -1) return null;
  return { row: rowIndex, col: colIndex };
};

const onMouseDown = (e) => {
  const cell = getCellFromPosition(e.clientX, e.clientY);
  if (!cell) return;
  isMouseDown.value = true;
  startPoint.value = { x: e.clientX, y: e.clientY };
  startCell.value = cell;
  endCell.value = cell;
};

const onMouseMove = (e) => {
  if (!isMouseDown.value) return;
  const dx = Math.abs(e.clientX - startPoint.value.x);
  const dy = Math.abs(e.clientY - startPoint.value.y);
  if (!dragging.value) {
    if (dx < DRAG_THRESHOLD && dy < DRAG_THRESHOLD) return;
    dragging.value = true;
    mode.value = e.ctrlKey ? "deselect" : "select";
  }
  const cell = getCellFromPosition(e.clientX, e.clientY);
  if (!cell) return;
  endCell.value = cell;
};

const onMouseUp = () => {
  if (dragging.value) applySelection();
  dragging.value = false;
  isMouseDown.value = false;
};

const applySelection = () => {
  const minRow = Math.min(startCell.value.row, endCell.value.row);
  const maxRow = Math.max(startCell.value.row, endCell.value.row);
  const minCol = Math.min(startCell.value.col, endCell.value.col);
  const maxCol = Math.max(startCell.value.col, endCell.value.col);
  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minCol; c <= maxCol; c++) {
      const k = key(r, c);
      if (mode.value === "select") selected.value.add(k);
      else selected.value.delete(k);
    }
  }
  emitSelected()
};

// ---------- Selection Rectangle ----------
const rectStyle = computed(() => {
  if (!dragging.value || !startCell.value || !endCell.value) return {};

  const minRow = Math.min(startCell.value.row, endCell.value.row);
  const maxRow = Math.max(startCell.value.row, endCell.value.row);
  const minCol = Math.min(startCell.value.col, endCell.value.col);
  const maxCol = Math.max(startCell.value.col, endCell.value.col);

  const containerRect = container.value.getBoundingClientRect();
  const rows = document.querySelectorAll(".body-row");
  const startRowRect = rows[minRow]?.getBoundingClientRect();
  const endRowRect = rows[maxRow]?.getBoundingClientRect();
  if (!startRowRect || !endRowRect) return {};

  const top = startRowRect.top - containerRect.top;
  const bottom = endRowRect.bottom - containerRect.top;
  const left = columnPositions.value[minCol] - scrollLeft.value;
  const right = columnPositions.value[maxCol] + CELL_WIDTH - scrollLeft.value;

  return {
    left: left + "px",
    top: top + "px",
    width: right - left + "px",
    height: bottom - top + "px",
    border: mode.value === "deselect" ? "2px dashed #f44336" : "2px dashed #2196f3",
    backgroundColor: mode.value === "deselect" ? "rgba(244,67,54,0.15)" : "rgba(33,150,243,0.15)",
    position: "absolute",
    pointerEvents: "none",
    zIndex: 10,
  };
});

// ---------- Emit selected data ----------
const emitSelected = () => {
  const result = [];
  selected.value.forEach((k) => {
    const [r, c] = k.split("_").map(Number);
    result.push({
      room_type: props.roomTypes[r].name,
      date: dates.value[c],
      value: getValue(props.roomTypes[r].name, dates.value[c]),
      stop_sale: getStopSaleValue(props.roomTypes[r].name, dates.value[c])
    });
  });
 
  emit("update:selected", result);
};

const getSelections = () => {
  const result = [];
  selected.value.forEach((k) => {
    const [r, c] = k.split("_").map(Number);
    
    result.push({
      room_type: props.roomTypes[r].name,
      date: dates.value[c],
      value: getValue(props.roomTypes[r].name, dates.value[c]),
      stop_sale: getStopSaleValue(props.roomTypes[r].name, dates.value[c]),
    });
  });
  return result;
};

defineExpose({
  getSelections,
  clearSelections,
  renderDates
});




// ---------- Resize handling for container width (needed for scroller) ----------
let resizeObserver = null;
onMounted(() => {
  if (gridWrapper.value) {
    // Ensure scrollers have the correct width
    resizeObserver = new ResizeObserver(() => {
      // Trigger re-render if needed
    });
    resizeObserver.observe(gridWrapper.value);
  }
  renderDates()
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
});
</script>

<style scoped>
.availability-container {
  position: relative;
  user-select: none;
  border: 1px solid #ddd;
  width: calc(100vw - 100px);
}

.grid-wrapper {
  max-height: 500px;
  overflow-y: auto; /* vertical scroll only */
  overflow-x: hidden; /* horizontal scroll handled by inner scroller */
  position: relative;
}
 
.no-scroll{
  overflow: auto; /* or scroll */

  /* Firefox */
  scrollbar-width: none;

  /* IE & Edge */
  -ms-overflow-style: none;
}

/* Chrome, Safari */
.no-scroll::-webkit-scrollbar {
  display: none;
}

.header-row,
.body-row {
  display: flex;
  align-items: stretch;
}

.sticky-left {
  position: sticky;
  left: 0;
  background: white;
  z-index: 3;
  width: 250px;
  flex-shrink: 0;
  border: 1px solid #ccc;
  box-sizing: border-box;
  text-align: left;
  padding: 2px 4px;
}

.room-type-header {
  font-weight: bold;
  background: #f1f1f1;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  height:80px;
}

.room-type-cell {
  background: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.columns-scroller {
  flex: 1;
  overflow-x: auto;
  position: relative;
}

/* Override vue-virtual-scroller styles to make horizontal work */
.columns-scroller .vue-recycle-scroller {
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  white-space: nowrap;
}

.columns-scroller .vue-recycle-scroller__item-wrapper {
  display: flex;
}
 
.vue-recycle-scroller.ready.direction-horizontal.last_row {
  height:75px
}

.header-cell,
.cell {
  width: 35px;
  flex-shrink: 0;
  border: 1px solid #ccc;
  text-align: center;
  padding: 2px 4px;
  box-sizing: border-box;
  font-size: 12px;
  height: 80px;
  background: #617c76;
}

.cell {
  background: white;
  height: 80px;
}

.header-cell {
  background: #f1f1f1;
  position: sticky;
  top: 0;
  z-index: 2;
}

.cell.selected {
  background: #8deb90;
  color: white;
}

.selection-rect {
  position: absolute;
  pointer-events: none;
  z-index: 10;
}

.btn {
  margin-top: 10px;
  padding: 6px 12px;
  cursor: pointer;
}
</style>