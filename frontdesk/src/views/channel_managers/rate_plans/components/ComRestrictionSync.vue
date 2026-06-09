<template>
  <ComDialogContent
    @onOK="onOk"
    hideButtonClose
   
    titleButtonOK="Save"
    :hideIcon="false"
  >
 
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
    <div class="grid" v-for="(d, index) in data.date_ranges" :key="index">

      <!-- START -->
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
            v-if="data.date_ranges.length > 1"
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

<!-- APPLY BUTTON TO All Room Type -->
</Fieldset>
  <Fieldset class="cs-close-open-sale-fieldset">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">Room Type</span>
        </div>
    </template>
   <div class="flex gap-2 mb-3">
            <Chip label="All Room Types" @click="onEnableUpdateAllRoomType()"
                :icon="isRoomTypeSelectAll ? 'pi pi-check' : ''" :class="isRoomTypeSelectAll ? 'p-chip-selected' : ''" class="cursor-pointer select-none"></Chip>
            <Chip :label="rt.room_type" :icon="rt.selected ? 'pi pi-check' : ''"
                @click="onToggleRoomTypeToUpdate(rt)" v-for="rt in data?.room_types_select"
                :key="'rt_selection' + rt.edoor_room_type" :class="rt.selected ? 'p-chip-selected' : ''" class="cursor-pointer select-none"/>

        </div>
  </Fieldset>

  <Fieldset v-for="(d, index) in data?.room_types_select.filter(rt => rt.selected)" class="cs-close-open-sale-fieldset">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">{{ d?.room_type }}</span>
        </div>
    </template>
    
  <ComSelect
  v-model="data.room_type_restrictions[d.room_type_id]"
  :clear="false"
  @onSelected="onSelectRestrictionType"
  :placeholder="$t('Restriction Types')"
  :options="restrictionManageByCM"
  isMultipleSelect
  maxSelectedLabels="6"
/>   
  </Fieldset>
  </ComDialogContent>
</template>

<script setup>
import { ref, inject , onMounted, computed } from 'vue'
import { getApi } from '@/plugin';
import { useRatePlan } from '../hooks/useRatePlan'
import { useRestriction } from "@/views/channel_managers/rate_plans/hooks/useRestriction";
import BlockUI from 'primevue/blockui';
const restrictionPattern = ref(Array(30).fill("O"))
const restrictionPatternString = computed(() => {
  return restrictionPattern.value.join("")
})

const selecteddayoptions = Array.from({ length: 30 }, (_, i) => {
  const day = i + 1
  return {
    label: `${day} day`,
    value: day
  }
})
const {
  roomTypes,
  restrictionTypes,
  cm_info
} = useRatePlan()

const restrictionManageByCM = computed(()=>{
  const _data = []
  if (cm_info.value.closed==1){
    _data.push("Closed")
  }
  if (cm_info.value.cta==1){
    _data.push("Cta")
  }
  if (cm_info.value.ctd==1){
    _data.push("Ctd")
  }
  if (cm_info.value.minlos==1){
    _data.push("MinLos")
  }
  
  if (cm_info.value.maxlos==1){
    _data.push("MaxLos")
  }
  
  if (cm_info.value.minlosarrival==1){
    _data.push("MinLosArrival")
  }
  
  if (cm_info.value.maxlosarrival==1){
    _data.push("MaxLosArrival")
  }
  
  if (cm_info.value.minadvbooking==1){
    _data.push("MinAdvBooking")
  }
  
  if (cm_info.value.maxadvbooking==1){
    _data.push("MaxAdvBooking")
  }
  if (cm_info.value.fullpatternlos==1){
    _data.push("FullPatternLos")
  }


return _data



})
const dialogRef = inject("dialogRef");
const moment = inject('$moment')
const updateRoomTypes = ref(new Set())

const isRoomTypeSelectAll = computed(()=>{
  return data.value.room_types_select.filter(x=>x.selected).length == data.value.room_types_select.length;
})
const restrictionType = ref()

function isRangeValid(range) {
  if (!range.start_date || !range.end_date) return false

  const start = moment(range.start_date)
  const end = moment(range.end_date)

  const diffDays = end.diff(start, 'days') + 1

  return diffDays <= 366
}

const isValidAllRanges = computed(() => {
  return data.value.date_ranges.every(r => isRangeValid(r))
})
/* ---------------- DATA ---------------- */
const data = ref({
  date_ranges: [
    {
      start_date: moment().toDate(),
      end_date: moment().add(1, 'day').toDate(),
    }
  ],
  room_types_select: [],
  room_types: [],
  rate_types:[],
  room_type_restrictions: {}
})

const restrictionMenuItems = computed(() => {
  return restrictionTypes.value.map(item => ({
    label: item.restriction_type,
    value: item.restriction_type,
  }))
})

/* ADD DATE RANGE */
function onAddDateRange() {
  const last = data.value.date_ranges[data.value.date_ranges.length - 1]

  const start = last
    ? moment(last.end_date).add(1, 'day')
    : moment()

  const newRange = {
    start_date: start.toDate(),
    end_date: start.clone().add(1, 'day').toDate()
  }

  data.value.date_ranges.push(newRange)
}


function onStartDateChange(d) {
  if (!d.start_date) return

  if (!d.end_date || d.start_date > d.end_date) {
    const newEnd = new Date(d.start_date)
    newEnd.setDate(newEnd.getDate() + 1)

    d.end_date = newEnd
  }
}

/* DELETE */
function onDeleteDateRange(index) {
  data.value.date_ranges.splice(index, 1)
}

/* min start */
function getMinStartDate(index) {
  const prev = data.value.date_ranges[index - 1]

  if (prev) {
    return moment(prev.end_date).add(1, 'day').toDate()
  }

  return null
}

// end
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
function onToggleRoomTypeToUpdate(room_type) {
  room_type.selected = !room_type.selected

  // update selected room types list
  data.value.room_types = data.value.room_types_select
    .filter(rt => rt.selected)
    .map(rt => rt.room_type_id)

  // ❌ when unselect → clear restrictions
  if (!room_type.selected) {
    data.value.room_type_restrictions = {
      ...data.value.room_type_restrictions,
      [room_type.room_type_id]: []
    }
  }
}
function onEnableUpdateAllRoomType() {
  const allSelected = data.value.room_types_select.every(rt => rt.selected)

  data.value.room_types_select.forEach(rt => {
    rt.selected = !allSelected

    // 👇 handle restrictions sync
    if (!allSelected) {
      // selecting ALL → ensure key exists
      if (!data.value.room_type_restrictions[rt.room_type_id]) {
        data.value.room_type_restrictions[rt.room_type_id] = []
      }
    } else {
      // unselect ALL → clear all restrictions
      data.value.room_type_restrictions[rt.room_type_id] = []
    }
  })

  // update selected room types list
  data.value.room_types = data.value.room_types_select
    .filter(rt => rt.selected)
    .map(rt => rt.room_type_id)
}


async function onOk() {

  // ❌ validate before saving
  const invalid = data.value.date_ranges.some(r => !isRangeValid(r))

  if (invalid) {
    window.showError?.("Each date range must not exceed 366 days (1 year)")
    return
  }

  const saveData = JSON.parse(JSON.stringify(data.value))

  saveData.date_ranges.forEach(x => {
    x.start_date = moment(x.start_date).local().format("YYYY-MM-DD")
    x.end_date = moment(x.end_date).local().format("YYYY-MM-DD")
  })

  const roomTypesPayload = {}

  saveData.room_types_select
    .filter(rt => rt.selected)
    .forEach(rt => {
      roomTypesPayload[rt.room_type_id] =
        saveData.room_type_restrictions[rt.room_type_id] || []
    })

  const payload = {
    ...saveData,
    room_types: roomTypesPayload
  }

  const l = await window.showLoading("ReSync Restriction...")

  const res = await app.postApi(
    "room_restriction.resync_room_restriction",
    { data: payload }
  )

  if (res.data) {
    dialogRef.value.close(true)
  }

  l.close()
}



onMounted(async () => {
     
    data.value.property = window.property_name
    data.value.rate_types = [dialogRef.value.data.rate_type]
    
    data.value.room_types_select = []

roomTypes.value.forEach(rt => {
  data.value.room_types_select.push({
    room_type: rt.room_type_name,
    room_type_id: rt.edoor_room_type,
    selected: rt.selected,
  })
   data.value.room_type_restrictions[rt.edoor_room_type] = []
})

data.value.room_types = data.value.room_types_select
  .filter(rt => rt.selected)
  .map(rt => rt.room_type_id)
    



})

</script>
<style scoped>
.p-fieldset .p-fieldset-content {
    padding: 0.5rem 1.25rem !important;
}
</style>