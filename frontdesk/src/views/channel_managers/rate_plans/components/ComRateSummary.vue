<template>
        <div class="flex gap-2 mb-3">
            <Chip label="All Room Types" @click="onEnableUpdateAllRoomType()"
                :icon="(updateRoomTypes.size == roomTypes.length) ? 'pi pi-check' : ''" :class="(updateRoomTypes.size == roomTypes.length) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"></Chip>
            <Chip :label="rt.room_type_name" :icon="(updateRoomTypes.has(rt.edoor_room_type)) ? 'pi pi-check' : ''"
                @click="onToggleRoomTypeToUpdate(rt.edoor_room_type)" v-for="rt in roomTypes"
                :key="'rt_selection' + rt.edoor_room_type" :class="(updateRoomTypes.has(rt.edoor_room_type)) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"/>

        </div>
  <table class="w-full border text-sm">
     <!-- HEADER -->
    <thead>
      <tr class="bg-gray-100">
        <th style="width: 100px;" class="border p-2 text-left">Room Type</th>
        <th style="width: 175px;" class="border p-2 text-left">Date Range</th>

        <th
          v-for="occ in occupancyColumns"
          :key="occ.code"
          class="border p-2 text-left"
        >
          {{ occ.title }}
        </th>
        
      </tr>
    </thead>

    <!-- BODY -->
    <tbody>
      <tr v-if="summaryRows.length"  v-for="(row, i) in summaryRows" :key="i">

        <!-- ROOM TYPE -->
        <td class="border p-2 font-semibold">
          {{ row.room_type }}
        </td>

        <!-- DATE RANGE -->
        <td class="border p-2">
          {{ formatDate(row.from) }} → {{ formatDate(row.to) }}
        </td>

        <!-- OCCUPANCY VALUES -->
        <td
          
          v-for="occ in occupancyColumns"
          :key="occ.code"
          class="border p-2 text-center"
        >
          {{ row.values[occ.code] ?? '-' }}
        </td>

      </tr>
      <tr v-else>
        <td colspan="100%" class="border p-2 text-center text-gray-500">
          No data to display. Please select room types to update.
        </td>
      </tr>
    </tbody>

  </table>
</template>

<script setup>
import { ref,computed, inject, onMounted} from 'vue'
import { useRoute } from '@/plugin'
import { useRatePlan } from '../hooks/useRatePlan'
const route = useRoute();
const updateRoomTypes = ref(new Set())
const moment = inject('$moment')


const {
  roomTypes,
  roomRatesData,
  startDate,
  endDate,
  getRoomRateData
} = useRatePlan()

async function onToggleRoomTypeToUpdate(room_type) {
  const newSet = new Set(updateRoomTypes.value)

  if (newSet.has(room_type)) {
    newSet.delete(room_type)
  } else {
    newSet.add(room_type)
  }
  roomTypes.value.find(x => x.edoor_room_type == room_type).selected = newSet.has(room_type)
  updateRoomTypes.value = newSet

  const l  = await window.showLoading("ReSync Restriction...")
  const res = await getRoomRateData({
  room_types: Array.from(updateRoomTypes.value || []),
  rate_type: route.params.name,
  start_date: moment(startDate.value),
  end_date: moment(endDate.value)
})
l.close();
}

function onEnableUpdateAllRoomType(room_type) {
  
    if (updateRoomTypes.value.size == roomTypes.value.length) {
        // remove 
        updateRoomTypes.value = new Set()
      roomTypes.value.forEach(x => x.selected = false)
    } else {
        updateRoomTypes.value = new Set(
  roomTypes.value.map(x => x.edoor_room_type)
)
roomTypes.value.forEach(x => x.selected = true)
    }
    summaryRows.value
getRoomRateData({
  room_types: Array.from(updateRoomTypes.value || []),
  rate_type: route.params.name,
  start_date: moment(startDate.value),
  end_date: moment(endDate.value)
})
}


/* =========================
   FORMAT DATE
========================= */
function formatDate(date) {
  return moment(date).format("DD MMM YYYY")
}

/* =========================
   OCCUPANCY COLUMNS
========================= */
const occupancyColumns = computed(() => {
  const map = new Map()
  roomTypes.value
    .filter(r => r.selected)
    .forEach(rt => {
      rt.occupancy_codes.forEach(occ => {
        map.set(occ.occupancy_code, occ.title)
      })
    })

  return Array.from(map.entries()).map(([code, title]) => ({
    code,
    title
  }))
})

/* =========================
   KEY (MUST MATCH BACKEND)
========================= */
function getKey(room_type_id, date, occ) {
  return (
    moment(date).format("YYMMDD") +
    room_type_id +
    occ
  )
}

/* =========================
   GET VALUE
========================= */
function getValue(room_type_id, date, occ) {
  const key = getKey(room_type_id, date, occ)
  return roomRatesData.value?.[key] ?? null
}

/* =========================
   SIGNATURE (COMPARE ALL OCC)
========================= */
function getSignature(room_type_id, date, occList) {
  return occList
    .map(o => getValue(room_type_id, date, o.code))
    .join('|')
}

/* =========================
   BUILD SEGMENTS (FIXED LOOP)
========================= */
function buildSegments(room_type_id, occList) {

  const segments = []

  let currentStart = moment(startDate.value)
  const end = moment(endDate.value)

  let prevSig = getSignature(room_type_id, currentStart, occList)
  let cursor = currentStart.clone().add(1, 'day')

  while (cursor.isSameOrBefore(end, 'day')) {

    const sig = getSignature(room_type_id, cursor, occList)
    if (sig !== prevSig) {

      segments.push({
        from: currentStart.clone(),
        to: cursor.clone().subtract(1, 'day')
      })

      currentStart = cursor.clone()
      prevSig = sig
    }

    cursor = cursor.clone().add(1, 'day')
  }

  segments.push({
    from: currentStart.clone(),
    to: end.clone()
  })

  return segments
}

/* =========================
   FINAL SUMMARY ROWS
========================= */
const summaryRows = computed(() => {

  const rows = []
  const occList = occupancyColumns.value

  roomTypes.value
    .filter(r => updateRoomTypes.value.has(r.edoor_room_type))
    .forEach(rt => {

      const segments = buildSegments(rt.edoor_room_type, occList) 
      segments.forEach(seg => {

        const values = {}

        occList.forEach(occ => {
          values[occ.code] = getValue(
            rt.edoor_room_type,
            seg.from,
            occ.code
          )
        })

        rows.push({
          room_type: rt.name || rt.room_type_name
,
          from: seg.from,
          to: seg.to,
          values
        })

      })

    })

  return rows
})
onMounted(() => {
  updateRoomTypes.value.add(roomTypes.value.find(x => x.selected).edoor_room_type)
})

</script>