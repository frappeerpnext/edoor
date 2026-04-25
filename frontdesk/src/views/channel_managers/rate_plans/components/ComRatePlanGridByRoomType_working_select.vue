<template>
  <div class="table-wrapper">
    
    <div
      v-if="dragRect.visible"
      class="drag-rect"
      :class="{ 'drag-rect-deselect': dragMode === 'deselect' }"
      :style="{
        left: dragRect.x + 'px',
        top: dragRect.y + 'px',
        width: dragRect.width + 'px',
        height: dragRect.height + 'px'
      }"
    ></div>
    <div>
      <table class="rate-table">
        <thead>
          <tr>
            <th class="sticky-left header-cell left-header">
              {{ year }}
            </th>
            <th
              v-for="n in numDays"
              :key="n"
              class="header-cell text-center"
            >
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
              <div class="guest-lines">
                <template v-for="rt in selectedRoomType" :key="rt.edoor_room_type">
                  <div v-for="occ in rt.occupancy_codes" :key="occ.occupancy_code">
                    {{ occ.title }}
                  </div>
                </template>
              </div>
            </th>
            <td
              v-for="n in numDays"
              :key="n"
              :data-day="n"
              :data-month-idx="monthIdx"
              :data-month="m.month"
              :class="[
                'dc',
                isClosed(m.month, n) == 1 ? 'closed' : '',
                (n > m.total_days || today > moment(getDateKey(m.month, n)).local().toDate()) ? 'disable' : '',
                isCellSelected(m.month, n) ? 'selected-cell' : '',
                (n <= m.total_days ? moment.utc(`${moment.utc(m.month).format('YYYY-MM')}-${n}`).format('dd') : '')
              ]"
              @mousedown="startDrag($event, monthIdx, n, m.month)"
              @mouseenter="updateDragRect($event)"
             
            >
              <div class="day-name">
                <span v-if="n <= m.total_days">
                  {{ moment.utc(`${moment.utc(m.month).format("YYYY-MM")}-${n}`).format("D dd") }}<br />
                </span>
              </div>
              <template v-for="rt in selectedRoomType" :key="rt.edoor_room_type">
                <div
                  v-for="occ in rt.occupancy_codes"
                  :key="occ.occupancy_code"
                  class="v"
                  v-if="n <= m.total_days"
                >
                  {{ getData(rt.edoor_room_type, m.month, n, occ.occupancy_code) }}
                </div>
              </template>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { computed, inject, ref, onMounted, onUnmounted } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'

const { roomTypes, roomRatesData, selectedDates, startDate, closeSaleData } = useRatePlan()
const moment = inject('$moment')
const props = defineProps({ year: Number, room_types: Object })

const numDays = Array.from({ length: 31 }, (_, i) => i + 1)

function getData(room_type_id, month, day, occupancy_code) {
  const key = moment(month).format("YYMM") + String(day).padStart(2, "0") + room_type_id + occupancy_code
  return roomRatesData.value[key] >= 0 ? roomRatesData.value[key].toLocaleString('en-US') : "__"
}

function isClosed(month, day) {
  const key = moment(month).format("YYMM") + String(day).padStart(2, "0")
  return (closeSaleData.value || {})[key] || 0
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

/* DRAG STATE */
const isDragging = ref(false)
const dragRect = ref({ x: 0, y: 0, width: 0, height: 0, visible: false })
const dragMode = ref('select')

let dragStart = { monthIdx: null, day: null, monthKey: null, cellEl: null }
let dragCurrent = { monthIdx: null, day: null, monthKey: null }

let rafId = null

function startDrag(e, monthIdx, day, monthKey) {

  const cell = e.currentTarget
  if (cell.classList.contains("disable")) return

  e.preventDefault()
  e.stopPropagation()

  dragStart = { monthIdx, day, monthKey, cellEl: cell }
  dragCurrent = { monthIdx, day, monthKey }
  dragMode.value = selectedDates.value.has(getDateKey(monthKey, day)) ? 'deselect' : 'select'

  isDragging.value = true
  updateDragRectFromCells(cell) // initial rectangle
}

function updateDragRect(e) {
  console.log(e)
  if (!isDragging.value) return

  const cell = e.currentTarget
  if (cell.classList.contains("disable")) return

  const monthIdx = parseInt(cell.dataset.monthIdx)
  const day = parseInt(cell.dataset.day)
  const monthKey = cell.dataset.month

  if (dragCurrent.monthIdx === monthIdx && dragCurrent.day === day) return

  dragCurrent = { monthIdx, day, monthKey }

  // Throttle with requestAnimationFrame for smooth 60fps updates
  if (rafId) cancelAnimationFrame(rafId)
  rafId = requestAnimationFrame(() => {
    updateDragRectFromCells(cell)
    rafId = null
  })
    
}

function updateDragRectFromCells(endCellEl) {
  console.log(endCellEl)
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
 
onMounted(() => {
  window.addEventListener("mouseup", endDrag)
})

onUnmounted(() => {
  window.removeEventListener("mouseup", endDrag)
  if (rafId) cancelAnimationFrame(rafId)
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
}
.dc:hover {
  background-color: rgba(64, 158, 255, 0.05);
}
.Sa,
.Su {
  background: rgb(246, 253, 217);
}
.closed .day-name {
  background: red;
}
</style>