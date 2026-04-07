<template>
  <div class="table-wrapper">
    {{ selectedDates }}
    <!-- Drag Rectangle with dynamic style based on mode -->
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
              :data-month="m.month"
              :data-day="n"
              :data-month-idx="monthIdx"
              :data-date="n <= m.total_days ? getDateKey(m.month, n) : ''"
              :class="[
                'dc',
                n > m.total_days ? 'disable' : '',
                isCellSelected(m.month, n) ? 'selected-cell' : '',
                (n <= m.total_days ? moment.utc(`${moment.utc(m.month).format('YYYY-MM')}-${n}`).format('dd') : '')
              ]"
              @mousedown="startDrag($event, monthIdx, n, m.month)"
              @mouseenter="updateDragRect($event)"
              @click.stop="handleCellClick($event, m.month, n)"
            >
              <div class="day-name">
                <span v-if="n <= m.total_days">
                  {{ moment.utc(`${moment.utc(m.month).format("YYYY-MM")}-${n}`).format("Ddd") }}<br/>
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

const { roomTypes, roomRatesData } = useRatePlan()
const moment = inject('$moment')
const props = defineProps({ year: Number, room_types: Object })

const numDays = Array.from({ length: 31 }, (_, i) => i + 1)

function getData(room_type_id, month, day, occupancy_code) {
  const key = moment(month).format("YYMM") + String(day).padStart(2, "0") + room_type_id + occupancy_code
  return roomRatesData.value[key] >= 0 ? roomRatesData.value[key].toLocaleString('en-US') : "__"
}

const months = computed(() => {
  return Array.from({ length: 12 }, (_, i) => {
    const month = i + 1
    const m = `${props.year}-${String(month).padStart(2, "0")}-01`
    return { month: m, total_days: moment.utc(m).startOf('month').daysInMonth() }
  })
})

const selectedRoomType = computed(() => roomTypes.value.filter(r => r.selected))

/* SELECTION STATE - Set for O(1) lookups */
const selectedDates = ref(new Set())

function getDateKey(monthFirstDay, day) {
  const monthStr = monthFirstDay.slice(0, 7) // "YYYY-MM"
  return `${monthStr}-${String(day).padStart(2, '0')}`
}

function isCellSelected(month, day) {
  return selectedDates.value.has(getDateKey(month, day))
}

/* DRAG STATE – stores cell coordinates (month index, day) */
const isDragging = ref(false)
const dragRect = ref({ x: 0, y: 0, width: 0, height: 0, visible: false })
const dragMode = ref('select') // 'select' or 'deselect'

let dragStart = { monthIdx: null, day: null, monthKey: null }
let dragCurrent = { monthIdx: null, day: null, monthKey: null }

function startDrag(e, monthIdx, day, monthKey) {
  const cell = e.currentTarget
  if (cell.classList.contains("disable")) return

  e.preventDefault()
  e.stopPropagation()

  dragStart = { monthIdx, day, monthKey }
  dragCurrent = { ...dragStart }
  dragMode.value = selectedDates.value.has(getDateKey(monthKey, day)) ? 'deselect' : 'select'

  isDragging.value = true
  updateDragRectFromCells()
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
  updateDragRectFromCells()
}

function updateDragRectFromCells() {
  const startCell = document.querySelector(`td.dc[data-month-idx="${dragStart.monthIdx}"][data-day="${dragStart.day}"]`)
  const endCell = document.querySelector(`td.dc[data-month-idx="${dragCurrent.monthIdx}"][data-day="${dragCurrent.day}"]`)

  if (!startCell || !endCell) {
    dragRect.value.visible = false
    return
  }

  const startRect = startCell.getBoundingClientRect()
  const endRect = endCell.getBoundingClientRect()

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
  dragStart = { monthIdx: null, day: null, monthKey: null }
  dragCurrent = { monthIdx: null, day: null, monthKey: null }
}

function handleCellClick(event, month, day) {
  const totalDays = moment(month).daysInMonth()
  if (day > totalDays) return

  if (dragStart.monthIdx !== null && dragCurrent.monthIdx !== null &&
      (dragStart.monthIdx !== dragCurrent.monthIdx || dragStart.day !== dragCurrent.day)) {
    return
  }

  const key = getDateKey(month, day)
  const newSet = new Set(selectedDates.value)
  if (newSet.has(key)) {
    newSet.delete(key)
  } else {
    newSet.add(key)
  }
  selectedDates.value = newSet
}

onMounted(() => {
  window.addEventListener("mouseup", endDrag)
})
onUnmounted(() => {
  window.removeEventListener("mouseup", endDrag)
})
</script>

<style scoped>
.table-wrapper { 
  user-select: none; 
  position: relative;
}
.disable { 
  background: #f5f5f5!important; 
  color: #bbb; 
  pointer-events: none; 
}
.selected-cell { 
  background: #cfe5ff!important; 
}

/* Drag rectangle - dashed border, blue for select mode */
.drag-rect { 
  position: fixed; 
  border: 2px dashed #409eff; 
  background: rgba(64, 158, 255, 0.1); 
  pointer-events: none; 
  z-index: 9999; 
}

/* Deselect mode - red dashed border and red tint */
.drag-rect.drag-rect-deselect {
  border: 2px dashed #f56c6c;
  background: rgba(245, 108, 108, 0.1);
}

.dc { 
  cursor: crosshair; 
  transition: background-color 0.05s ease;
  position: relative;
}
.dc:hover {
  background-color: rgba(64, 158, 255, 0.05);
}
</style>