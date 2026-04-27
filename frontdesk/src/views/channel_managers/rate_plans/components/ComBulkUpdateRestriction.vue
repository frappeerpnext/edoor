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

  <Fieldset v-if="restrictionType?.show_date_selection || restrictionType?.show_number_input || restrictionType?.show_reset_value">
    <template #legend>
        <div class="flex items-center pl-2">
            <span class="font-bold p-2">For all room types</span>
        </div>
    </template>
   <div class="flex gap-2 mb-3" v-if="restrictionType">
    <ComSelect v-if="restrictionType.show_date_selection" 
    class="w-full"  v-model="allRoomType.date_select"  :clear="false" 
    @onSelected="onSelectRestrictionDate($event, allRoomType)" 
    :placeholder="$t('Restriction Types')" 
    :options="selecteddayoptions" optionLabel="label" 
    optionValue="value"  isMultipleSelect /> 
    
    <InputNumber 
        v-model="allRoomType.value" 
        class="flex-1"
        placeholder="all room types value"
        :disabled="allRoomType.reset_value"
         v-if="restrictionType.show_number_input"
        :max="999"
      /> 
          <div class="flex align-items-center" 
         v-if="restrictionType.show_reset_value"
         >
       <Checkbox 
  v-model="allRoomType.reset_value"
  :binary="true" 
  inputId="checkbox_all_room_type"
  @change="onResetChange"
/>
        <label :for="`checkbox_all_room_type`" class="ml-2 cursor-pointer">Reset Value</label>
      </div>
       <Button
  label="Apply"
  icon="pi pi-download"
  @click="onApplyToAllRoomType()"
/>
    </div>
    
</Fieldset>
<!-- APPLY BUTTON TO All Room Type -->

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
                @click="onToggleRoomTypeToUpdate(rt)" v-for="rt in data?.room_types"
                :key="'rt_selection' + rt.edoor_room_type" :class="rt.selected ? 'p-chip-selected' : ''" class="cursor-pointer select-none"/>

        </div>

    <div>
    <!-- Header with Close all / Open all buttons -->
    <div v-if="restrictionType?.show_radio_input" class="flex justify-content-end align-items-center mb-1">
      <div class="flex gap-3">
        <Button 
          label="Close all" 
          icon="pi pi-times" 
          class="p-button-outlined border-none"
          @click="closeAll"
        />
        <Button 
          label="Open all" 
          icon="pi pi-check" 
          class="p-button-outlined border-none"
          @click="openAll"
        />
      </div>
    </div>

    <!-- Room Types List -->
    <div v-for="(rt, index) in data.room_types" :key="index" class="mb-3 p-3 surface-card border-round shadow-1">
      <div class="flex align-items-center justify-content-between flex-wrap gap-3">
        <!-- Room Type Label with Info Icon -->
        <div class="flex align-items-center gap-2">
          <span class="font-bold text-lg">{{ rt.room_type }}</span>
         
        </div>
      
        <!-- Radio Buttons for Close/Open -->
        <div class="flex gap-4">
        
          <div class="flex align-items-center"  v-if="restrictionType.show_radio_input">
            <RadioButton 
             v-model="rt.value" 
              inputId="close"
              :value="1"
              :disabled = "!rt.selected"
            />
            <label class="ml-2 cursor-pointer" :class="{ 'text-gray-400': !rt.selected }">Close</label>
          </div>
          <div class="flex align-items-center"  v-if="restrictionType.show_radio_input">
            <RadioButton 
              v-model="rt.value" 
              inputId="open"
          :value="0"
            :disabled = "!rt.selected"
            />
            <label class="ml-2 cursor-pointer" :class="{ 'text-gray-400': !rt.selected }"">Open</label>
          </div>

          <div class="flex gap-4">
 <div>
          <!-- Input Text -->
      <InputNumber 
        v-model="rt.value" 
        :disabled="!rt.selected || rt.reset_value"
        :class="{ 'surface-200': rt.reset_value }"
        class="flex-1"
        placeholder="Enter value"
        v-if="restrictionType.show_number_input"
         :max="999"
      />
  
        </div>
         <div class="flex align-items-center" 
         v-if="restrictionType.show_reset_value"
         >
        <Checkbox 
          v-model="rt.reset_value" 
          :binary="true" 
          :inputId="`checkbox${index}`"
          :disabled="!rt.selected"
        />
        <label :for="`checkbox${index}`" class="ml-2 cursor-pointer">Reset Value</label>
      </div>
<BlockUI :blocked="!rt.selected">
 <ComSelect
v-if="restrictionType.show_date_selection"

   v-tippy="{
    content: `
      <div style='max-width:120px;display: block;white-space: normal;text-align: center;word-break: break-word;'>
       Days : </br>
      ${rt.date_select}
      </div>
    `,
    allowHTML: true
  }"
    class="w-20rem"  v-model="rt.date_select"  :clear="false" @onSelected="onSelectRestrictionDate($event, rt)" :placeholder="$t('Restriction Types')" :options="selecteddayoptions" optionLabel="label" optionValue="value"  isMultipleSelect />
 </BlockUI>         
  </div>
         
        </div>
      </div>
    </div>
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
  roomRatesData,
  startDate,
  endDate,
  selectedDates,
  restrictionTypes
} = useRatePlan()
const dialogRef = inject("dialogRef");
const moment = inject('$moment')
const updateRoomTypes = ref(new Set())

const allRoomType = ref({
  value: null,
  reset_value: false,
  date_select:[]
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
  room_types: []
})

const isRoomTypeSelectAll = computed(()=>{
  return data.value.room_types.filter(x=>x.selected).length == data.value.room_types.length;
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

function onSelectRestrictionDate(values, rt) {
  // always reset to all "O"
  const current = Array(30).fill("O")

  const selected = Array.isArray(values) ? values : [values]

  selected.forEach(v => {
    const index = Number(v) - 1
    if (index >= 0 && index < 30) {
      current[index] = "C"
    }
  })

  rt.value = current.join("")
}

function onStartDateChange(d) {
  if (!d.start_date) return

  if (!d.end_date || d.start_date > d.end_date) {
    const newEnd = new Date(d.start_date)
    newEnd.setDate(newEnd.getDate() + 1)

    d.end_date = newEnd
  }
}

function setRestrictionPatternFromString(str) {
  if (!str || str.length !== 30) {
    restrictionPattern.value = Array(30).fill("O")
    return
  }

  restrictionPattern.value = str.split("")
}
function onToggleRoomTypeToUpdate(room_type) {
    room_type.selected = !room_type.selected
}
function onEnableUpdateAllRoomType() {
  const allSelected = data.value.room_types.every(rt => rt.selected)

  data.value.room_types.forEach(rt => {
    rt.selected = !allSelected
  })
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

async function onOk() {
  // pls do validation

  const saveData = JSON.parse(JSON.stringify(data.value))
  
  saveData.date_ranges.forEach(x => {
        x.start_date = moment(x.start_date).local().format("YYYY-MM-DD");
        x.end_date = moment(x.end_date).local().format("YYYY-MM-DD");
    })
    
  saveData.room_types = saveData.room_types.filter(x=>x.selected && (x.value !=null || x.reset_value ) )


  
  const l  =await window.showLoading("Save Restriction...")

  const res = await app.postApi("room_restriction.bulk_update_room_restriction",{
    data:saveData
  })
  if (res.data){
    dialogRef.value.close(true)
  }
  l.close();


}

function onResetChange() {
  if (allRoomType.value.reset_value) {
    allRoomType.value.value = null
  }
}
// onApplyToAllRoomType
function onApplyToAllRoomType() {
  data.value.room_types.filter(x=>x.selected).forEach(rt => {
    if (allRoomType.value.reset_value) {
      rt.value = null
      rt.reset_value = true
    }
    else if (allRoomType.value.date_select != null) {
      rt.value = allRoomType.value.value
      rt.reset_value = false
      rt.date_select = allRoomType.value.date_select
    }
    else {
      rt.value = allRoomType.value.value
      rt.reset_value = false
      
    }
  })
  allRoomType.value.value = null
  allRoomType.value.reset_value = false
  allRoomType.value.date_select = []
}


onMounted(async () => {
     
    restrictionType.value =restrictionTypes.find(x=>x.restriction_type == dialogRef.value.data.restriction_type)
    data.value.property = window.property_name
    data.value.rate_type = dialogRef.value.data.rate_type
    data.value.restriction_type = dialogRef.value.data.restriction_type


    if (selectedDates.value.size > 0) {
   
        const dates = app.utils.groupDatesToPeriods(selectedDates.value);
        data.value.date_ranges = dates.map(x => {
            return {
                start_date: moment(x.start_date).toDate(),
                end_date: moment(x.end_date).toDate()
            }
        })


    }
    
    roomTypes.value.forEach(rt=>{
     
      data.value.room_types.push({
        "room_type":rt.room_type_name,
        "room_type_id":rt.edoor_room_type,
        "selected": rt.selected,
        "value": rt.selected? restrictionType.default_value:null,
        "date_select": null,
      })
    })
    



})
// Close all rooms
const closeAll = () => {
 data.value.room_types.filter(x=>x.selected).forEach(rt => {
    rt.value = 1
  }
)
}

// Open all rooms
const openAll = () => {
 data.value.room_types.filter(x=>x.selected).forEach(rt => {
    rt.value =0
  })
}
</script>
<style scoped>
.p-fieldset .p-fieldset-content {
    padding: 0.5rem 1.25rem !important;
}
</style>