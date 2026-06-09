<template>
  <div class="table-wrapper">
   
  <Message v-if="cm_info?.restrictions == 'Deliver to PMS'">
    Room restriction are managed by the Channel Manager.
</Message>
  <Message v-if="cm_info?.closed == 0 && cm_info?.restrictions != 'Deliver to PMS' && restrictionManageByCM.length>0">
   <strong
  class="m-2 border-white  border border-round px-2 py-1 inline-block"
  v-for="s in restrictionManageByCM"
>
  {{cm_info.restrictions}}  {{rateInfo?.cm_rate_plan_list?.cm_rate_plan}}
</strong>
    <p>Manage by the Channel Manager.</p>
    
</Message>

    <div v-if="dragRect.visible" class="drag-rect" :class="{ 'drag-rect-deselect': dragMode === 'deselect' }" :style="{
      left: dragRect.x + 'px',
      top: dragRect.y + 'px',
      width: dragRect.width + 'px',
      height: dragRect.height + 'px'
    }"></div>

    <!-- Hover Popover -->
    <Teleport to="body">
      <div v-if="showPopover" class="cell-popover"
        :style="{ left: popoverPosition.x + 'px', top: popoverPosition.y + 'px' }" @mouseenter="handlePopoverMouseEnter"
        @mouseleave="handlePopoverMouseLeave">
        <ComRoomRateDetailPopOver v-if="selectedRoomType" :rate_type="rateType" :date="hoverDate"
          :room_type_id="selectedRoomType[0].edoor_room_type" />

      </div>
    </Teleport>

    <div>
      <table class="rate-table">
        <thead>
          <tr>
            <th class="sticky-left header-cell left-header">
              {{ year }}
            </th>
            <th v-for="n in numDays" :key="n" class="header-cell text-center">
              {{ n }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(m, monthIdx) in months" :key="m.month">
            <th class="sticky-left month-cell text-left">
              <div class="font-semibold text-lg mb-2">
                {{ moment.utc(m.month).format("MMM - YYYY") }}
              </div>
              <div v-for="rt in _restrictionTypes">
                {{ rt.restriction_type }}
              </div>

            </th>
            <td v-for="n in numDays" :key="n" :data-day="n" :data-month-idx="monthIdx" :data-month="m.month" :class="[
              'dc',
              getRestrictionValue('Closed', m.month, n) == 1 ? 'closed' : '',
              (n > m.total_days || today > moment(getDateKey(m.month, n)).local().toDate()) ? 'disable' : '',
              isCellSelected(m.month, n) ? 'selected-cell' : '',
              (n <= m.total_days ? moment.utc(`${moment.utc(m.month).format('YYYY-MM')}-${n}`).format('dd') : '')
            ]" @mousedown="startDrag($event, monthIdx, n, m.month)"
              @mouseenter="handleCellMouseEnter($event, monthIdx, n, m.month)" @mouseleave="handleCellMouseLeave"
              @click.stop="handleCellClick($event, m.month, n)">
              <div class="day-name">
                <span v-if="n <= m.total_days">
                  {{ moment.utc(`${moment.utc(m.month).format("YYYY-MM")}-${n}`).format("D dd") }}<br />
                </span>
              </div>
              <div v-for="rt in _restrictionTypes" class="v">
                <template v-if="n <= m.total_days">
                  <template v-if="['Closed', 'Cta', 'Ctd'].includes(rt.restriction_type)">
                    <i class="pi pi-times text-red-400" v-if="getRestrictionValue(rt.restriction_type, m.month, n)"
                      style="font-size: 1rem"></i>
                    <i class="pi pi-check  text-green-400" v-else style="font-size: 1rem"></i>
                  </template>
                  <template v-else-if="rt.restriction_type=='FullPatternLos'">
                   <div
  v-if="getRestrictionValue(rt.restriction_type, m.month, n)!='__'"
  class="bg-primary-400 border-circle flex align-items-center pt-1 justify-content-center text-white text-xs"
  style="width:1.2rem; height:1.2rem; line-height:1.2rem;    margin: 0 auto;"
>
  {{ getRestrictionValue(rt.restriction_type, m.month, n) }}
</div>

<span v-else>__</span>
                  </template>
                  <template v-else>
                    <span>
                      {{ getRestrictionValue(rt.restriction_type, m.month, n) }}
                    </span>
                  </template>

                </template>
              </div>

            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref, onMounted, onUnmounted, Teleport } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'
import { useRoute } from 'vue-router';
import ComRoomRateDetailPopOver from "@/views/channel_managers/rate_plans/components/ComRoomRateDetailPopOver.vue"
const route = useRoute();
const rateType = ref(route.params.name)

const { roomTypes, selectedDates, startDate, restrictionData,
  restrictionTypes,
  selectedRestrictionTypes,
  cm_info,
  rateInfo

} = useRatePlan()
const moment = inject('$moment')
const props = defineProps({ year: Number, room_types: Object })
const restrictionManageByCM = computed(()=>{
  const _data = []
  if (cm_info.value.closed==0){
    _data.push("Closed")
  }
  if (cm_info.value.cta==0){
    _data.push("Cta")
  }
  if (cm_info.value.ctd==0){
    _data.push("Ctd")
  }
  if (cm_info.value.minlos==0){
    _data.push("MinLos")
  }
  
  if (cm_info.value.maxlos==0){
    _data.push("MaxLos")
  }
  
  if (cm_info.value.minlosarrival==0){
    _data.push("MinLosArrival")
  }
  
  if (cm_info.value.maxlosarrival==0){
    _data.push("MaxLosArrival")
  }
  
  if (cm_info.value.minadvbooking==0){
    _data.push("MinAdvBooking")
  }
  
  if (cm_info.value.maxadvbooking==0){
    _data.push("MaxAdvBooking")
  }
  if (cm_info.value.fullpatternlos==0){
    _data.push("FullPatternLos")
  }


return _data



})

const _restrictionTypes = computed(() => {
  return restrictionTypes.filter(x => selectedRestrictionTypes.value.includes(x.restriction_type))
})

const numDays = Array.from({ length: 31 }, (_, i) => i + 1)


function getRestrictionValue(restriction_type, month, day) {

  const key = moment(month).format("YYMM") + String(day).padStart(2, "0") + selectedRoomType.value[0].edoor_room_type
  if (["Closed", "Cta", "Ctd"].includes(restriction_type)) {
    return (restrictionData.value[restriction_type] || {})[key]
  } else {
    if (key in (restrictionData.value[restriction_type] || {})) {
      return (restrictionData.value[restriction_type] || {})[key] || 0
    } else {
      return "__"
    }
  }

}

const today = moment(moment().local().format("YYYY-MM-DD")).toDate()

const months = computed(() => {
  return Array.from({ length: 12 }, (_, i) => {
    const month = i + 1
    const m = `${props.year}-${String(month).padStart(2, "0")}-01`
    return { month: m, total_days: moment.utc(m).startOf('month').daysInMonth() }
  }).filter(x => moment(x.month).toDate() >= moment(startDate.value).local().toDate())
})

const selectedRoomType = computed(() => roomTypes.value.filter(r => r.selected))

function getDateKey(monthFirstDay, day) {
  const monthStr = monthFirstDay.slice(0, 7)
  return `${monthStr}-${String(day).padStart(2, '0')}`
}

function isCellSelected(month, day) {
  return selectedDates.value.has(getDateKey(month, day))
}

/* ---------- DRAG LOGIC (unchanged) ---------- */
const isDragging = ref(false)
const dragRect = ref({ x: 0, y: 0, width: 0, height: 0, visible: false })
const dragMode = ref('select')

let dragStart = { monthIdx: null, day: null, monthKey: null, cellEl: null }
let dragCurrent = { monthIdx: null, day: null, monthKey: null }

let rafId = null

function startDrag(e, monthIdx, day, monthKey) {
  const cell = e.currentTarget
  if (cell.classList.contains("disable")) return

  if (cm_info.value.restrictions=="Deliver to PMS" && rateInfo.value?.cm_rate_plan_list?.cm_rate_plan) return


  e.preventDefault()
  e.stopPropagation()

  dragStart = { monthIdx, day, monthKey, cellEl: cell }
  dragCurrent = { monthIdx, day, monthKey }
  dragMode.value = selectedDates.value.has(getDateKey(monthKey, day)) ? 'deselect' : 'select'

  isDragging.value = true
  updateDragRectFromCells(cell)

  // Cancel any pending hover when drag starts
  cancelHoverTimer()
  hidePopover()
}

function updateDragRect(e) {
  if (!isDragging.value) return

  const cell = e.currentTarget
  if (cell.classList.contains("disable")) return

  const monthIdx = parseInt(cell.dataset.monthIdx)
  const day = parseInt(cell.dataset.day)
  const monthKey = cell.dataset.month

  if (dragCurrent.monthIdx === monthIdx && dragCurrent.day === day) return

  dragCurrent = { monthIdx, day, monthKey }

  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    updateDragRectFromCells(cell)
    rafId = null
  })
}

function updateDragRectFromCells(endCellEl) {
  const startCellEl = dragStart.cellEl
  if (!startCellEl || !endCellEl) {
    dragRect.value.visible = false
    return
  }

  const startRect = startCellEl.getBoundingClientRect()
  const endRect = endCellEl.getBoundingClientRect()

  const left = Math.min(startRect.left, endRect.left)
  const top = Math.min(startRect.top, endRect.top)
  const right = Math.max(startRect.right, endRect.right)
  const bottom = Math.max(startRect.bottom, endRect.bottom)

  dragRect.value = {
    x: left,
    y: top,
    width: right - left,
    height: bottom - top,
    visible: true
  }
}

function endDrag() {
  if (!isDragging.value) return

  if (rafId) {
    cancelAnimationFrame(rafId)
    rafId = null
  }

  if (dragStart.monthIdx !== null && dragCurrent.monthIdx !== null) {
    const minMonth = Math.min(dragStart.monthIdx, dragCurrent.monthIdx)
    const maxMonth = Math.max(dragStart.monthIdx, dragCurrent.monthIdx)
    const minDay = Math.min(dragStart.day, dragCurrent.day)
    const maxDay = Math.max(dragStart.day, dragCurrent.day)

    const cellsToToggle = new Set()

    for (let mIdx = minMonth; mIdx <= maxMonth; mIdx++) {
      const monthObj = months.value[mIdx]
      const monthKey = monthObj.month
      const daysInMonth = monthObj.total_days
      for (let d = minDay; d <= maxDay; d++) {
        if (d <= daysInMonth) {
          cellsToToggle.add(getDateKey(monthKey, d))
        }
      }
    }

    const newSet = new Set(selectedDates.value)
    if (dragMode.value === 'select') {
      for (const key of cellsToToggle) {
        newSet.add(key)
      }
    } else {
      for (const key of cellsToToggle) {
        newSet.delete(key)
      }
    }
    selectedDates.value = newSet
  }

  isDragging.value = false
  dragRect.value.visible = false
  dragStart = { monthIdx: null, day: null, monthKey: null, cellEl: null }
  dragCurrent = { monthIdx: null, day: null, monthKey: null }
}

function handleCellClick(event, month, day) {
  const totalDays = moment(month).daysInMonth()
  if (day > totalDays) return

  if (
    dragStart.monthIdx !== null &&
    dragCurrent.monthIdx !== null &&
    (dragStart.monthIdx !== dragCurrent.monthIdx || dragStart.day !== dragCurrent.day)
  ) {
    return
  }
  // existing click logic (if any)
}

/* ---------- HOVER POPOVER LOGIC ---------- */
const showPopover = ref(false)
const popoverLoading = ref(false)
const popoverData = ref({})
const popoverPosition = ref({ x: 0, y: 0 })
const hoverDate  = ref()

// Flags for mouse presence
const isMouseOverCell = ref(false)
const isMouseOverPopover = ref(false)

let hoverTimer = null
let hideTimer = null
let currentHoverCell = null
let abortController = null

// Function to call your server API – adjust endpoint and parameters as needed
async function fetchPopoverDetails(month, day) {
  // Example: replace with actual API call
  // const response = await fetch(`/api/cell-details?month=${month}&day=${day}`, { signal: abortController.signal })
  // return await response.json()

  // Mock data for demo
  return {
    date: moment.utc(`${month.slice(0, 7)}-${String(day).padStart(2, '0')}`).format('YYYY-MM-DD'),
    roomType: 'Deluxe',
    occupancy: '2 Adults',
    rate: '$150'
  }
}

function handleCellMouseEnter(event, monthIdx, day, monthKey) {
  // Always update drag if dragging
  if (isDragging.value) {
    updateDragRect(event)
    return
  }

  const cell = event.currentTarget
  if (cell.classList.contains("disable")) return

  // Mark that mouse is over cell
  isMouseOverCell.value = true
  clearHideTimer()

  // Cancel any previous hover timer and hide popover immediately
  cancelHoverTimer()
  hidePopover()

  // Store current cell info and mouse position for popover placement
  currentHoverCell = { cell, monthKey, day, mouseX: event.clientX, mouseY: event.clientY }

  // Start timer to show popover after 1 second
  hoverTimer = setTimeout(() => {
    if (currentHoverCell && isMouseOverCell.value) {
      showPopoverForCell(currentHoverCell.cell, currentHoverCell.monthKey, currentHoverCell.day, currentHoverCell.mouseX, currentHoverCell.mouseY)
    }
  }, 500)
}

function handleCellMouseLeave() {
  isMouseOverCell.value = false
  cancelHoverTimer()
  scheduleHidePopover()
  currentHoverCell = null
}

function handlePopoverMouseEnter() {
  isMouseOverPopover.value = true
  clearHideTimer()
}

function handlePopoverMouseLeave() {
  isMouseOverPopover.value = false
  scheduleHidePopover()
}

function scheduleHidePopover() {
  clearHideTimer()
  // Small delay to allow moving from cell to popover
  hideTimer = setTimeout(() => {
    if (!isMouseOverCell.value && !isMouseOverPopover.value) {
      hidePopover()
    }
  }, 100)
}

function clearHideTimer() {
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

function cancelHoverTimer() {
  if (hoverTimer) {
    clearTimeout(hoverTimer)
    hoverTimer = null
  }
  // Abort any ongoing fetch
  if (abortController) {
    abortController.abort()
    abortController = null
  }
}

function hidePopover() {
  showPopover.value = false
  popoverLoading.value = false
  popoverData.value = {}
  cancelHoverTimer()
  clearHideTimer()
}


async function showPopoverForCell(cell, monthKey, day, mouseX, mouseY) {
  
  if (!cell) return
  const rect = cell.getBoundingClientRect();

    let x = rect.left     // distance from left of viewport
    let y = rect.top;  

    if (x+500>window.innerWidth){
      x = window.innerWidth - 500 + rect.width
    }else {
      x = x + rect.width;
    }

    if ((y+400)> window.innerHeight){
      y = window.innerHeight - 450;
    }

  // Position popover near mouse pointer (with offset)
  popoverPosition.value = {
    x: x , // 15px right of cursor
    y: y  // 10px below cursor
  }

  // Prepare fetch

  popoverLoading.value = true
  hoverDate.value = moment.utc(`${monthKey.slice(0, 7)}-${String(day).padStart(2, '0')}`).format('YYYY-MM-DD')
  showPopover.value = true


}

/* ---------- LIFECYCLE ---------- */
onMounted(() => {
  window.addEventListener("mouseup", endDrag)
})

onUnmounted(() => {
  window.removeEventListener("mouseup", endDrag)
  if (rafId) cancelAnimationFrame(rafId)
  cancelHoverTimer()
  clearHideTimer()
})
</script>

<style scoped>
.table-wrapper {
  user-select: none;
  position: relative;
}

.disable {
  background: #f5f5f5 !important;
  color: #bbb;
  pointer-events: none;
}

.selected-cell {
  background: #cfe5ff !important;
}

.drag-rect {
  position: fixed;
  pointer-events: none;
  z-index: 9999;
  border: 2px dashed #409eff;
  background: rgba(64, 158, 255, 0.08);
  animation: dash-move 0.5s linear infinite;
  box-shadow: 0 0 6px rgba(64, 158, 255, 0.6);
}

.drag-rect.drag-rect-deselect {
  border: 2px dashed #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.dc {
  transition: background-color 0.05s ease;
  position: relative;
  border-right-width: 1px;
  padding-right: 3px;
  padding-left: 3px;
  text-align: center;
}

.dc:hover {
  background-color: rgba(64, 158, 255, 0.05);
}

.Sa,
.Su {
  background: rgb(246, 253, 217);
}

.closed .day-name {
  background: #ff0000b1 !important;
  border-radius: 10px;
  color: #fff !important;
}

/* Popover styling */
.cell-popover {
  position: absolute;
  z-index: 10000;
  background: white;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  padding: 12px 16px;
  min-width: 200px;
  pointer-events: auto;
  font-size: 14px;
}

.popover-loading {
  color: #666;
  font-style: italic;
}

.rate-table {
  width: 100%;
}

.dc:not(.disable) .day-name {
  color: rgb(66, 66, 120);
}

.day-name {
  text-align: center;
  margin-bottom: 0.5rem;
  font-weight: bold;
  font-size: 10px;
}

.v {
  text-align: center;
}

.dc:not(.disable) .v {
  color: rgb(66, 66, 120);
}

.table-wrapper {
  margin-top: 20px;
}

.table-wrapper th {
  border-width: 1px;
  padding: 8px 0;
}

.rate-table>* {
  font-size: 12px !important;
}

.sticky-left.month-cell.text-left {
  padding-left: 5px;
}

.table-wrapper th {
  background: #e9e9ff;
}

.dc.selected-cell.Sa>.day-name,
.dc.selected-cell.Su>.day-name {
  background: rgb(246, 253, 217);
  border-radius: 10px;
}
.rate-table > thead{
  position: -webkit-sticky;
  position: sticky;
  top: 118px;
  z-index: 950;
}
</style>