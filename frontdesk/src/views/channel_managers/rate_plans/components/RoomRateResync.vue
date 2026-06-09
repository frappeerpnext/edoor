<template>
  <ComDialogContent
    @onOK="onOk"
    hideButtonClose
    titleButtonOK="Save"
  >
  <Message severity="warn">
    <p>
      <strong>Resync is used when data between PMS and Channel Manager becomes inconsistent.</strong>
      <br/>
This may happen due to connection issues, sync errors, or missed updates.
Use this only when needed, as full data upload should not be done frequently.
    </p>
  </Message>
 
    <!-- ================= VALIDITY ================= -->
    <Fieldset class="cs-close-open-sale-fieldset">
      <template #legend>
        <span class="font-bold p-2">Validity period</span>
      </template>

      <div class="grid">
        <div class="col-6 font-bold">Start Date</div>
        <div class="col-6 font-bold">End Date</div>
      </div>

      <div class="grid" v-for="(d, index) in data.date_ranges" :key="index">

        <div class="col-6">
          <Calendar
            v-model="d.start_date"
            dateFormat="dd-mm-yy"
            showIcon
            class="w-full"
            :minDate="getMinStartDate(index)"
            :maxDate="getMaxEndDate(index)"
            @date-select="onStartDateChange(d)"
          />
        </div>

        <div class="col-6 flex">
          <Calendar
            v-model="d.end_date"
            dateFormat="dd-mm-yy"
            showIcon
            class="w-full"
            :minDate="d.start_date"
            :maxDate="getMaxEndDate(index)"
          />

          <Button
            icon="pi pi-times"
            v-if="data.date_ranges.length > 1"
            severity="danger"
            text
            @click="onDeleteDateRange(index)"
          />
        </div>

      </div>

      <div class="flex justify-end">
        <Button label="Add Period" icon="pi pi-plus" text @click="onAddDateRange"/>
      </div>
    </Fieldset>

    <!-- ================= RATE TYPE ================= -->
    <Fieldset
      v-for="(rateType, rateTypeIndex) in rateplanlist?.rate_type_list || []"
      :key="rateType.rate_type_name"
      class="cs-close-open-sale-fieldset"
    >
      <template #legend>
        <span class="font-bold p-2">
          {{ rateType.rate_type_name }}
        </span>
      </template>

      <!-- ROOM TYPE SELECT -->
      <div class="flex gap-2 flex-wrap mb-3">
        <Chip
          label="All Room Types"
          class="cursor-pointer"
          :class="isAllRoomTypesSelected(rateTypeIndex) ? 'bg-primary text-white' : ''"
          @click="onToggleAllRoomTypes(rateTypeIndex)"
        />

        <Chip
          v-for="rt in getRoomTypesForRateType(rateTypeIndex)"
          :key="rt.room_type_id"
          :label="rt.room_type"
          class="cursor-pointer"
          :class="rt.selected ? 'bg-primary text-white' : ''"
          @click="onToggleRoomType(rateTypeIndex, rt)"
        />
      </div>

      <!-- OCCUPANCY -->
      <div
        v-for="rt in getSelectedRoomTypes(rateTypeIndex)"
        :key="rt.room_type_id"
        class="mb-3"
      >
        <div class="font-bold mb-1">
          {{ rt.room_type }}
        </div>

        <ComSelect
          :modelValue="rt.occupancies"
          @update:modelValue="(val) => updateOccupancies(rateTypeIndex, rt.room_type_id, val)"
          :clear="false"
          :options="getOccupancy(rt.room_type_id)"
          optionLabel="title"
          optionValue="occupancy_code"
          isMultipleSelect
          placeholder="Select Occupancy"
        />
      </div>
    </Fieldset>
  </ComDialogContent>
</template>

<script setup>
import { ref, inject, onMounted } from "vue"
import { useRatePlan } from "../hooks/useRatePlan"

const property = JSON.parse(localStorage.getItem("edoor_property"))
const dialogRef = inject("dialogRef")
const moment = inject("$moment")
const incomingRateType = dialogRef?.value?.data?.rate_type || []
const MAX_SELECTED_DAYS = 366

const { roomTypes } = useRatePlan()

/* ================= STATE ================= */
const rateplanlist = ref({
  rate_type_list: []
})

// Store room types selection per rate type
const rateTypeRoomSelections = ref([])

const data = ref({
  date_ranges: [
    {
      start_date: moment().toDate(),
      end_date: moment().add(1, "day").toDate(),
    }
  ],
  property: null,
})

/* ================= HELPER FUNCTIONS ================= */
function getRoomTypesForRateType(rateTypeIndex) {
  if (!rateTypeRoomSelections.value[rateTypeIndex]) {
    // Initialize if not exists
    rateTypeRoomSelections.value[rateTypeIndex] = []
    const map = new Map()
    
    roomTypes.value.forEach(rt => {
      if (!map.has(rt.edoor_room_type)) {
        map.set(rt.edoor_room_type, {
          room_type: rt.room_type_name,
          room_type_id: rt.edoor_room_type,
          selected: false,
          occupancies: []
        })
      }
    })
    
    rateTypeRoomSelections.value[rateTypeIndex] = Array.from(map.values())
  }
  
  return rateTypeRoomSelections.value[rateTypeIndex]
}

function getSelectedRoomTypes(rateTypeIndex) {
  const roomTypesList = getRoomTypesForRateType(rateTypeIndex)
  return roomTypesList.filter(rt => rt.selected)
}

function isAllRoomTypesSelected(rateTypeIndex) {
  const roomTypesList = getRoomTypesForRateType(rateTypeIndex)
  if (!roomTypesList.length) return false
  return roomTypesList.every(rt => rt.selected)
}

function onToggleAllRoomTypes(rateTypeIndex) {
  const roomTypesList = getRoomTypesForRateType(rateTypeIndex)
  const allSelected = isAllRoomTypesSelected(rateTypeIndex)
  
  roomTypesList.forEach(rt => {
    rt.selected = !allSelected
    if (!allSelected) {
      rt.occupancies = []
    }
  })
}

function onToggleRoomType(rateTypeIndex, rt) {
  rt.selected = !rt.selected
  if (!rt.selected) {
    rt.occupancies = []
  }
}

function updateOccupancies(rateTypeIndex, roomTypeId, occupancies) {
  const roomTypesList = getRoomTypesForRateType(rateTypeIndex)
  const roomType = roomTypesList.find(rt => rt.room_type_id === roomTypeId)
  if (roomType) {
    roomType.occupancies = occupancies
  }
}

/* ================= OCCUPANCY ================= */
function getOccupancy(room_type_id) {
  const room = roomTypes.value.find(
    r => r.edoor_room_type === room_type_id
  )

  return room
    ? room.occupancy_codes.map(o => ({
        title: o.title,
        occupancy_code: o.occupancy_code
      }))
    : []
}

/* ================= DATE ================= */
function onAddDateRange() {
  const last = data.value.date_ranges.at(-1)
  const start = last ? moment(last.end_date).add(1, "day") : moment()

  data.value.date_ranges.push({
    start_date: start.toDate(),
    end_date: start.clone().add(1, "day").toDate()
  })
}

function onStartDateChange(d) {
  if (!d.end_date || d.start_date > d.end_date) {
    d.end_date = moment(d.start_date).add(1, "day").toDate()
  }
}

function onDeleteDateRange(index) {
  data.value.date_ranges.splice(index, 1)
}

function getMinStartDate(index) {
  const prev = data.value.date_ranges[index - 1]
  return prev ? moment(prev.end_date).add(1, "day").toDate() : null
}

function getMaxEndDate(index) {
  const firstStartDate = data.value.date_ranges?.[0]?.start_date
  const globalMax = firstStartDate
    ? moment(firstStartDate).add(360, 'days').toDate()
    : null

  const next = data.value.date_ranges[index + 1]

  if (next?.start_date) {
    const nextMax = moment(next.start_date).subtract(1, 'day').toDate()

    return globalMax && nextMax > globalMax
      ? globalMax
      : nextMax
  }

  return globalMax
}

/* ================= API ================= */
async function getRatePlanList() {
  if (incomingRateType) {
    const l = await window.showLoading()
    rateplanlist.value.rate_type_list = [{"rate_type_name":incomingRateType}]

    l.close()
  } else {
    // if no rate type from dialog, load all rate types
    const l = await window.showLoading()

    const res = await app.getApi("rate_plan.get_rate_type_list", {
      property: property.name
    })

    if (res.data) {
      rateplanlist.value = {
        ...res.data,
        rate_type_list: (res.data.rate_type_list || []).filter(
          x => x.status === "Connected"
        )
      }
    }

    l.close()
  }
}

/* ================= SUBMIT ================= */
async function onOk() {
  const rate_types = []

  rateplanlist.value.rate_type_list.forEach((rateType, index) => {
    const daily_rate = []

    const selectedRoomTypesList = getSelectedRoomTypes(index)

    selectedRoomTypesList.forEach(rt => {
      if (rt.occupancies && rt.occupancies.length > 0) {

        daily_rate.push({
          
          room_type:rt.room_type_id,
          occupancy_codes:rt.occupancies
        })
      }
    })

    // only push if has data
    if (daily_rate.length > 0) {
      rate_types.push({
        rate_type:rateType.rate_type_name,
        room_types:  daily_rate
      })
    }
  })

  const saveData = {
    rate_types: rate_types,
    date_ranges: data.value.date_ranges.map(x => ({
      start_date: moment(x.start_date).format("YYYY-MM-DD"),
      end_date: moment(x.end_date).format("YYYY-MM-DD")
    })),
    property: data.value.property
  }

  // console.log(saveData)
  // return

 

  const l = await window.showLoading("Resync Room Rates...")

  const res = await app.postApi("rate_plan.resync_room_rate", {
    data: saveData
  })

  if (res.data) {
    dialogRef.value.close(true)
  }

  l.close()
}

/* ================= INIT ================= */
onMounted(() => {
  data.value.property = window.property_name
  getRatePlanList()
})
</script>
