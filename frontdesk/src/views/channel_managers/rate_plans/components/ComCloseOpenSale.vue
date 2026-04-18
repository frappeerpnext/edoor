<template>
  <ComDialogContent
    @onOK="onOk"
    hideButtonClose
   :disabledBtnOk="updateRoomTypes.size === 0"
    titleButtonOK="Save"
    :hideIcon="false"
  >
  <Fieldset class="cs-close-open-sale-fieldset">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">Action</span>
        </div>
    </template>
        <!-- STATUS -->
    <div class="flex gap-4 mb-3">
      <label class="flex items-center gap-2 cursor-pointer">
        <Checkbox
          :modelValue="data.action === 'close'"
          @change="() => setStatus('close')"
          binary
        />
        <span>Close Sales</span>
      </label>

      <label class="flex items-center gap-2 cursor-pointer">
        <Checkbox
          :modelValue="data.action === 'open'"
          @change="() => setStatus('open')"
          binary
        />
        <span>Open</span>
      </label>
    </div>
</Fieldset>

  <Fieldset class="cs-close-open-sale-fieldset">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">Validity period</span>
        </div>
    </template>
    

    <!-- HEADER -->
    <div class="grid">
      <div class="col-6 font-bold">Start Date</div>
      <div class="col-6 font-bold">End Date</div>
    </div>

    <!-- DATE RANGE -->
    <div class="grid" v-for="(d, index) in data.date_range" :key="index">

      <!-- START -->
      <div class="col-6">
        <Calendar
          v-model="d.start_date"
          dateFormat="dd-mm-yy"
          showIcon
          class="w-full"
          :minDate="getMinStartDate(index)"
          :maxDate="d.end_date"
        />
      </div>

      <!-- END -->
      <div class="col-6">
        <div class="flex">
          <Calendar
            v-model="d.end_date"
            dateFormat="dd-mm-yy"
            showIcon
            class="w-full"
            :minDate="d.start_date"
            :maxDate="getMaxEndDate(index)"
          />

          <!-- DELETE (FIRST LOCKED) -->
          <Button
            icon="pi pi-times"
            v-if="index !== 0"
            severity="danger"
            text
            @click="onDeleteDateRange(index)"
          />
        </div>
      </div>

    </div>

    <!-- ADD PERIOD -->
   <div class="flex justify-end">
  <Button
  label="Add Period"
  icon="pi pi-plus"
  text
  @click="onAddDateRange"
/>
</div>
</Fieldset>

  <Fieldset class="cs-close-open-sale-fieldset">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">Room Type</span>
        </div>
    </template>
   <div class="flex gap-2 mb-3">
            <Chip label="All Room Types" @click="onEnableUpdateAllRoomType()"
                :icon="(updateRoomTypes.size == roomTypes.length) ? 'pi pi-check' : ''" :class="(updateRoomTypes.size == roomTypes.length) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"></Chip>
            <Chip :label="rt.room_type_name" :icon="(updateRoomTypes.has(rt.edoor_room_type)) ? 'pi pi-check' : ''"
                @click="onToggleRoomTypeToUpdate(rt.edoor_room_type)" v-for="rt in roomTypes"
                :key="'rt_selection' + rt.edoor_room_type" :class="(updateRoomTypes.has(rt.edoor_room_type)) ? 'p-chip-selected' : ''" class="cursor-pointer select-none"/>

        </div>
</Fieldset>

   

  </ComDialogContent>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'

const moment = inject('$moment')
const updateRoomTypes = ref(new Set())
/* ---------------- STATUS ---------------- */

function setStatus(type) {
  data.value.action = type
}

/* ---------------- DATA ---------------- */
const data = ref({
  action: 'close',
  date_range: [
    {
      start_date: moment().toDate(),
      end_date: moment().add(1, 'day').toDate(),
    }
  ],
  room_types: []
})

/* ADD DATE RANGE */
function onAddDateRange() {
  const last = data.value.date_range[data.value.date_range.length - 1]

  const start = last
    ? moment(last.end_date).add(1, 'day')
    : moment()

  const newRange = {
    start_date: start.toDate(),
    end_date: start.clone().add(1, 'day').toDate()
  }

  data.value.date_range.push(newRange)
}


function onToggleRoomTypeToUpdate(room_type) {
    if (updateRoomTypes.value.has(room_type)) {
        updateRoomTypes.value.delete(room_type)
    } else {
        updateRoomTypes.value.add(room_type)
    }
    data.value.room_types = Array.from(updateRoomTypes.value)
}
function onEnableUpdateAllRoomType(room_type) {
    if (updateRoomTypes.value.size == roomTypes.value.length) {
        // remove 
        updateRoomTypes.value = new Set()
    } else {
        roomTypes.value.forEach(x => {
            updateRoomTypes.value.add(x.edoor_room_type)
        })
    }
    data.value.room_types = Array.from(updateRoomTypes.value)
}

/* DELETE */
function onDeleteDateRange(index) {
  if (index === 0) return
  data.value.date_range.splice(index, 1)
}

/* min start */
function getMinStartDate(index) {
  const prev = data.value.date_range[index - 1]

  if (prev) {
    return moment(prev.end_date).add(1, 'day').toDate()
  }

  return null
}

// end
function getMaxEndDate(index) {
  const next = data.value.date_range[index + 1]

  if (next) {
    return moment(next.start_date).add(-1, 'day').toDate()
  }

  return null
}
const {
  roomTypes,
  roomRatesData,
  startDate,
  endDate
} = useRatePlan()

function onOk() {
  console.log('SAVE DATA:', {
    action: data.value.action,
    ranges: data.value.date_range
  })
}
</script>
<style scoped>
.p-fieldset .p-fieldset-content {
    padding: 0.5rem 1.25rem !important;
}
</style>