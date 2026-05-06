<template>
   <ComDialogContent @onOK="onOk" hideButtonClose hideButtonOK hideFooter titleButtonOK="Save" :hideIcon="false">
    <div>
    <!-- =========================
      ROOM TYPE SELECT
    ========================= -->
   <div class="flex items-center gap-4 flex-wrap mb-2">

  <!-- Chips -->
  <div class="flex gap-2 items-center flex-wrap">
    <Chip
      label="All Room Types"
      @click="onEnableUpdateAllRoomType"
      :icon="(updateRoomTypes.size == roomTypes.length) ? 'pi pi-check' : ''"
      :class="(updateRoomTypes.size == roomTypes.length) ? 'p-chip-selected' : ''"
      class="cursor-pointer select-none"
    />

    <Chip
      v-for="rt in roomTypes"
      :key="'rt_' + rt.edoor_room_type"
      :label="rt.room_type_name"
      @click="onToggleRoomType(rt.edoor_room_type)"
      :icon="updateRoomTypes.has(rt.edoor_room_type) ? 'pi pi-check' : ''"
      :class="updateRoomTypes.has(rt.edoor_room_type) ? 'p-chip-selected' : ''"
      class="cursor-pointer select-none"
    />
  </div>

  <!-- Dates -->
 <div class="flex items-center gap-4">

  <!-- Start Date -->
  <div class="flex flex-column gap-1">
    <label class="text-sm">Start Date</label>
    <Calendar
      v-model="start_date"
      dateFormat="dd-mm-yy"
      showButtonBar
      showIcon
      panelClass="no-btn-clear"
      class="w-12rem"
    />
  </div>

  <!-- End Date -->
  <div class="flex flex-column gap-1">
    <label class="text-sm">End Date</label>
    <Calendar
      v-model="end_date"
      dateFormat="dd-mm-yy"
      showButtonBar
      showIcon
      panelClass="no-btn-clear"
      class="w-12rem"
    />
  </div>

</div>

</div>


    <!-- =========================
      GROUP BY RESTRICTION TYPE
    ========================= -->
    <div
      v-for="(rows, type) in groupedByRestriction"
      :key="type"
      class="mb-1 border rounded"
    >

      <!-- HEADER -->
      <div
        class="bg-gray-200 p-3 cursor-pointer flex justify-between items-center"
        @click="toggleExpand(type)"
      >
        <span class="font-semibold">
          Restriction Type: {{ type }}
        </span>

        <i :class="expanded[type] ? 'pi pi-chevron-down' : 'pi pi-chevron-right'"></i>
      </div

      <!-- TABLE -->
      <table v-if="expanded[type]" class="w-full text-sm">
        <thead>
          <tr class="bg-gray-100">
            <th class="border p-2 text-left">Room Type</th>
            <th class="border p-2 text-left">Date Range</th>
            
            <th class="border p-2 text-center">Value</th>
          </tr>
        </thead>

        <tbody>

          <tr v-if="rows.length" v-for="(row, i) in rows" :key="i">
            
            <!-- ROOM -->
            <td class="border p-2 font-semibold">
              {{ row.room_type }}
            </td>

            <!-- DATE -->
            <td class="border p-2">
              {{ formatDate(row.from) }} → {{ formatDate(row.to) }}
            </td>


            <!-- VALUE -->
            <td class="border p-2 text-center">

              <template v-if="row.value == 0">
                <i class="pi pi-check text-green-400"></i>
              </template>

              <template v-else-if="row.value == 1 || row.value == '1'">
                <i class="pi pi-times text-red-400"></i>
              </template>

              <template v-else>
                {{ row.value ?? '-' }}
              </template>

            </td>

          </tr>

          <tr v-else>
            <td colspan="3" class="border p-2 text-center text-gray-500">
              No data
            </td>
          </tr>

        </tbody>
      </table>

    </div>

  </div>
  </ComDialogContent>
</template>

<script setup>
import { ref, computed, inject, watch , onMounted } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'
const start_date = ref(null)
const end_date = ref(null)
const moment = inject('$moment')

/* =========================
   STATE
========================= */
const updateRoomTypes = ref(new Set())
const expanded = ref({})

/* =========================
   DATA
========================= */
const {
  roomTypes,
  startDate,
  endDate,
  restrictionData,
  restrictionTypes,
  selectedRestrictionTypes
} = useRatePlan()

/* =========================
   FILTER RESTRICTIONS
========================= */
const _restrictionTypes = computed(() => {
  return restrictionTypes.filter(x =>
    selectedRestrictionTypes.value.includes(x.restriction_type)
  )
})

/* =========================
   SELECTED ROOM TYPES
========================= */
const selectedRoomType = computed(() =>
  roomTypes.value.filter(r => updateRoomTypes.value.has(r.edoor_room_type))
)

/* =========================
   FORMAT DATE
========================= */
function formatDate(date) {
  return moment(date).format("DD MMM YYYY")
}

/* =========================
   GET VALUE
========================= */
function getRestrictionValue(type, date, day = 1) {
  const key =
    moment(date).format("YYMM") +
    String(day).padStart(2, "0")

  const data = restrictionData.value?.[type] || {}

  return data[key] ?? (["Closed", "Cta", "Ctd"].includes(type) ? 0 : "-")
}

/* =========================
   BUILD SEGMENTS PER TYPE + ROOM
========================= */
function buildSegmentsByTypeAndRoom(type) {
  const segments = []

  let start = moment(start_date.value)
  const end = moment(end_date.value)

  let prev = getRestrictionValue(type, start)
  let cursor = start.clone().add(1, 'day')

  while (cursor.isSameOrBefore(end, 'day')) {

    const val = getRestrictionValue(type, cursor)

    if (val !== prev) {
      segments.push({
        from: start.clone(),
        to: cursor.clone().subtract(1, 'day'),
        value: prev
      })

      start = cursor.clone()
      prev = val
    }

    cursor = cursor.clone().add(1, 'day')
  }

  segments.push({
    from: start.clone(),
    to: end.clone(),
    value: prev
  })

  return segments
}

/* =========================
   FINAL GROUPING
========================= */
const groupedByRestriction = computed(() => {
  const result = {}

  _restrictionTypes.value.forEach(t => {

    const rows = []

    selectedRoomType.value.forEach(rt => {

      const segments = buildSegmentsByTypeAndRoom(
        t.restriction_type
      )

      segments.forEach(seg => {
        rows.push({
          room_type: rt.room_type_name,
          from: seg.from,
          to: seg.to,
          value: seg.value
        })
      })

    })

    result[t.restriction_type] = rows
  })

  return result
})

/* =========================
   EXPAND DEFAULT
========================= */
watch(_restrictionTypes, (val) => {
  const obj = {}
  val.forEach(t => {
    obj[t.restriction_type] = true
  })
  expanded.value = obj
}, { immediate: true })

/* =========================
   TOGGLE EXPAND
========================= */
function toggleExpand(type) {
  const key = String(type)

  expanded.value = {
    ...expanded.value,
    [key]: !expanded.value[key]
  }
}

/* =========================
   ROOM TYPE TOGGLE
========================= */
function onToggleRoomType(id) {
  const newSet = new Set(updateRoomTypes.value)

  if (newSet.has(id)) newSet.delete(id)
  else newSet.add(id)

  updateRoomTypes.value = newSet
}

/* =========================
   ALL TOGGLE
========================= */
function onEnableUpdateAllRoomType() {
  if (updateRoomTypes.value.size === roomTypes.value.length) {
    updateRoomTypes.value = new Set()
  } else {
    updateRoomTypes.value = new Set(
      roomTypes.value.map(x => x.edoor_room_type)
    )
  }
}
onMounted(() => {
  updateRoomTypes.value.add(roomTypes.value.find(x => x.selected).edoor_room_type)
  console.log("selectedRoomType", moment(startDate.value)) 
  start_date.value = moment(startDate.value).toDate()
end_date.value = moment(endDate.value).toDate()

})
</script>