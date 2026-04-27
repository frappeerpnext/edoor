<template>
  <ComDialogContent
    @onOK="onOk"
    hideButtonClose
   
    titleButtonOK="Save"
    :hideIcon="false"
  >
  {{ data }}
 
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
  

  
  </ComDialogContent>
</template>

<script setup>
import { ref, inject , onMounted, computed } from 'vue'
import { useRatePlan } from '../hooks/useRatePlan'
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
  restrictionTypes
} = useRatePlan()
const dialogRef = inject("dialogRef");
const moment = inject('$moment')
const updateRoomTypes = ref(new Set())

const isRoomTypeSelectAll = computed(()=>{
  return data.value.room_types_select.filter(x=>x.selected).length == data.value.room_types_select.length;
})
const restrictionType = ref()

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
  rate_type:[],
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
  const next = data.value.date_ranges[index + 1]

  if (next) {
    return moment(next.start_date).add(-1, 'day').toDate()
  }

  return null
}

function onToggleRoomTypeToUpdate(room_type) {
    room_type.selected = !room_type.selected
  data.value.room_types = data.value.room_types_select
    .filter(rt => rt.selected)
    .map(rt => rt.room_type_id)
}
function onEnableUpdateAllRoomType() {
  const allSelected = data.value.room_types_select.every(rt => rt.selected)
  data.value.room_types_select.forEach(rt => {
    rt.selected = !allSelected
  })
  data.value.room_types = data.value.room_types_select
    .filter(rt => rt.selected)
    .map(rt => rt.room_type_id)

}


async function onOk() {
  // pls do validation
  
  const saveData = JSON.parse(JSON.stringify(data.value))
  
  saveData.date_ranges.forEach(x => {
        x.start_date = moment(x.start_date).local().format("YYYY-MM-DD");
        x.end_date = moment(x.end_date).local().format("YYYY-MM-DD");
    })
  console.log("Selected Room Types for Update:", saveData)  
  const l  =await window.showLoading("Save Restriction...")
  const res = await app.postApi("room_restriction.resync_room_restriction",{
    data:saveData
  })
  if (res.data){
    dialogRef.value.close(true)
  }
  l.close();


}



onMounted(async () => {
     
    data.value.property = window.property_name
    data.value.rate_type = [dialogRef.value.data.rate_type]
    
    data.value.room_types_select = []

roomTypes.value.forEach(rt => {
  data.value.room_types_select.push({
    room_type: rt.room_type_name,
    room_type_id: rt.edoor_room_type,
    selected: rt.selected,
  })
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