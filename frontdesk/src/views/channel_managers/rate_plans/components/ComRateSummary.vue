<template>
  <ComSelect  class="my-2" v-model="selectedRoomType" :options="roomTypesWithAll" optionLabel="room_type_name" optionValue="edoor_room_type" />
   
  <table class="w-full border text-sm">
     <!-- HEADER -->
    <thead>
      <tr class="bg-gray-100">
        <th class="border p-2 text-left">Room Type</th>
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
      <tr v-for="(row, i) in summaryRows" :key="i">

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
    </tbody>

  </table>
</template>

<script setup>
import { ref,computed, inject } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'
const selectedRoomType = ref(null)

const moment = inject('$moment')


const {
  roomTypes,
  roomRatesData,
  startDate,
  endDate
} = useRatePlan()


const roomTypesWithAll = computed(() => [
  {
    room_type_name: 'All',
    edoor_room_type: 'All'   // or 'ALL'
  },
  ...roomTypes.value
])
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
    console.log(sig)
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
  const room_type_selected = computed(() => {
    if (!selectedRoomType.value || selectedRoomType.value === 'All') {
      return roomTypes.value
    }
    return selectedRoomType.value
  })


  roomTypes.value
    .filter(r => r.selected)
    .forEach(rt => {

      const segments = buildSegments(room_type_selected.value , occList)

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
          room_type: rt.name || rt.edoor_room_type,
          from: seg.from,
          to: seg.to,
          values
        })

      })

    })

  return rows
})
</script>