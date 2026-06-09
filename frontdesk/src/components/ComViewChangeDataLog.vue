<template>
  <ComDialogContent hideButtonClose titleButtonOK="Ok" :hideIcon="false" :hideButtonOK="true">
    <!-- Header -->
     <div class="grid gap-2">
        <div class=" col">
          <span class="label">{{ $t('Posting Date') }}</span>
          <span class="flex gap-2 flex-wrap card_value">{{ data?.posting_date }}</span>
        </div>
        <div class="col">
          <span class="label">{{ $t('Rate Type') }}</span>
          <span class="flex gap-2 flex-wrap card_value">{{ data?.rate_type }}</span>
        </div>
         <div v-if="data?.restriction_type" class=" col ">
          <span class="label">{{ $t('Restriction') }}</span>
          <span class="flex gap-2 flex-wrap card_value">{{ data?.restriction_type }}</span>
        </div>
    </div>
    <div v-if="dateRanges" class="grid mt-2 gap-2">
        <div class=" col">
      <span class="label">  <b>{{ $t('Date Ranges') }}</b></span> 
      <div class="flex gap-2 flex-wrap card_value">
<Chip
      v-for="(item, index) in dateRanges"
      :key="index"
      :label="`${moment(item.start_date).format('DD-MM-yyyy') || '—'} → ${moment(item.end_date).format('DD-MM-yyyy') || '—'}`"
    />
      </div> 
        </div>
     
    </div>
    
  <DataTable v-if="data?.transaction_type =='Prices update'" :value="matrix.rows" class="p-datatable-sm">
  <!-- Room Type -->
  <Column field="room_type_name" header="Room Type" frozen />

  <!-- Dynamic columns -->
  <Column
    v-for="col in matrix.columns"
    :key="col"
    :field="col"
    :header="matrix.titles.get(col)"
    bodyClass="text-center"
    headerClass="text-center"
  />
</DataTable>
        <DataTable 
  v-if="data?.transaction_type =='Restriction update'" :value="parsedData?.room_types" class="p-datatable-sm">
      
      <Column field="room_type" header="Room Type" />
 
    <Column
  header="Value"
  headerClass="text-center"
  bodyClass="text-center"
>
  <template #body="{ data }">
    <div class="flex justify-content-center">
      <Tag   v-if="!data.value" value="Reset" severity="warning" class="border-round" />
      <div v-else>
        {{ data.value }}
      </div>
    </div>
  </template>
</Column>

    </DataTable>
    <!-- Date Range -->
    <div class="mb-3">
     
      <div v-for="(d, i) in data?.date_ranges" :key="i">
        {{ d?.start_date }} → {{ d?.end_date }}
      </div>
    </div>
   </ComDialogContent>
</template>
<script setup>
import { onMounted, ref, inject,computed } from 'vue';
import Tag from 'primevue/tag';

 const data  = ref()
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
 
async function getData() {
  const l = await window.showLoading()
  const res = await app.getDoc("Change Data Log", dialogRef.value.data.docname)

  if (res.data) {
    data.value = res.data
  }
  l.close();

}
const parsedData = computed(() => {
  try {
    return JSON.parse(data.value?.data) || {}
  } catch (e) {
    console.error('Invalid JSON', e)
    return {}
  }
})

const roomTypes = computed(() => {
  const raw = parsedData.value?.room_type

  if (!raw) return []

  return raw
    .split(',')
    .map(t => t.trim())
    .filter(Boolean)
})
const matrix = computed(() => {
  const rooms = parsedData.value?.room_types ?? []

  // collect unique occupancy titles safely
  const columns = new Map()

  rooms.forEach(room => {
    const occ = room?.occupancy_codes ?? []

    occ.forEach(o => {
      if (o?.occupancy_code) {
        columns.set(o.occupancy_code, o.title || o.occupancy_code)
      }
    })
  })

  const columnKeys = Array.from(columns.keys())

  const rows = rooms.map(room => {
    const occ = room?.occupancy_codes ?? []

    const row = {
      room_type_name: room?.room_type_name ?? '-'
    }

    columnKeys.forEach(code => {
      const found = occ.find(o => o?.occupancy_code === code)
      row[code] = found?.rate ?? '-'
    })

    return row
  })

  return {
    columns: columnKeys,
    titles: columns,
    rows
  }
})
const dateRanges = computed(() => {
  return parsedData?.value?.date_ranges ?? parsedData?.value?.date_range ?? []
})
onMounted(async () => {

  await getData()


})
</script> 
<style scoped>
/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.info-card {
  background: #f9fafb;
  padding: 12px;
  border-radius: 10px;
}

.label {
  font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 6px;
}

.value {
  font-weight: bold;
}

.value.danger {
  color: #ef4444;
}
.card_value{
  font-size: 1rem;
    font-weight: 500;
    color: #0f172a;
    background: #fafcff;
    padding: 8px 0;
    border-bottom: 1px dashed #e2e8f0;
    padding-left: 3px;
}

</style>