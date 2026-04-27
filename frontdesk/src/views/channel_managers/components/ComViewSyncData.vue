<template>
  <ComDialogContent hideButtonClose titleButtonOK="Ok" :hideIcon="false" :hideButtonOK="true">
  

    <div class="sync-modal">

      <!-- Header -->
      <div class="sync-header">
        <div class="left flex gap-2">
          <span class="text-xl font-bold">{{ log?.title }}</span>
          <Tag class="border-round" :severity="statusSeverity" :value="log?.status" />
        </div>
        <div class="right">
          {{ log?.title }} at {{ moment(log?.creation).format("DD-MM-YYYY hh:mm A") }}
        </div>
      </div>

      <!-- Info Cards -->
      <div class="info-grid">
        <div class="info-card">
          <span class="label">{{ $t('Provider') }}</span>
          <span class="value">{{ log?.provider }}</span>
        </div>

        <div class="info-card">
          <span class="label">{{ $t('Property') }}</span>
          <span class="value">{{ log?.property }}</span>
        </div>

        <div class="info-card" v-if="log?.sync_action">
          <span class="label">{{ $t('Sync Action') }}</span>
          <span class="value danger">{{ log?.sync_action || '' }}</span>
        </div>

        <div class="info-card" v-if="log?.title == 'Delay Sync'">
          <span class="label">{{ $t('Delay until') }}</span>
          <span class="value">{{ moment(log?.sync_until).format("DD-MM-YYYY hh:mm A") }}</span>
        </div>
      </div>

      <!-- Alert -->
      <Message v-if="log?.response_text" severity="warn" icon="pi pi-exclamation-triangle">
        <div class="font-medium mb-2">
          Channel Manager Response
        </div>

        <div class="font-mono text-sm">
          {{ log?.response_text }}
        </div>

      </Message>
      <hr />

      <!-- Table -->
      <div class="table-container mt-5">
        <template v-if="log?.title == 'Prices update'">


          <h3 class="text-xl font-bold">Rates Detail</h3>

          <DataTable :value="log?.data" stripedRows responsiveLayout="scroll">



            <Column field="room_type" header="Room Type" />

            <Column field="period" header="Periods">
              <template #body="slotProps">

                <span class="font-medium">
                  <div v-for="d in slotProps.data.period">
                    {{ moment(d.start_date).format("DD-MM-YYYY") }} to {{ moment(d.end_date).format("DD-MM-YYYY") }}
                  </div>

                </span>

              </template>
            </Column>
            <Column field="rate" header="Rate">
              <template #body="slotProps">

                <span class="font-medium">
                  <div v-for="r in slotProps.data.rates">

                    <CurrencyFormat :value="r.rate"></CurrencyFormat> / {{ r.title }}
                  </div>

                </span>

              </template>
            </Column>

          </DataTable>
        </template>
        <template v-if="log?.title == 'Restriction update'">


          <h3 class="text-xl font-bold">Restriction Detail</h3>

          <DataTable :value="log?.data" stripedRows responsiveLayout="scroll">



            <Column field="restriction_type" header="Restriction Type" />
            <Column field="room_type" header="Room Type" />

            <Column header="Periods">
              <template #body="slotProps">
                <span class="font-medium">
                  
                    {{ moment(slotProps.data.start_date).format("DD-MM-YYYY") }} to {{ moment(slotProps.data.end_date).format("DD-MM-YYYY") }}
                  

                </span>

              </template>
            </Column>
            <Column field="value" header="Value">
              <template #body="slotProps">

                <span class="font-medium">
                  <template v-if="['Closed','Cta','Ctd'].includes(slotProps.data.restriction_type)">
                    <Chip label="Closed" v-if="slotProps.data.value === '1'" icon="pi pi-times" :class="'bg-red-200' " />
                    <Chip label="Opened" icon="pi pi-check" :class="'bg-green-200'" v-else />
                  </template>
                  <template v-else>
                    {{ slotProps.data.value }}
                  </template>
                  
                </span>

              </template>
            </Column>

          </DataTable>
        </template>
      </div>

    </div>

    <template #footer-right>

      <Button label="Retry Sync" v-if="log?.sync_action == 'Stop Sync' && log?.is_retry_sync == 0" icon="pi pi-sync"
        @click="onRetrySync" />
    </template>
  </ComDialogContent>
</template>
<script setup>
import { onMounted, ref, inject, computed } from 'vue';

import Tag from 'primevue/tag';

import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const log = ref()

const statusSeverity = computed(() => {

  if (log.value?.status === "Success")
    return "success";

  if (log.value?.status === "Warning")
    return "warning";

  if (log.value?.status === "Error")
    return "danger";

  return "info";

});


async function getLog() {

  const res = await app.getApi("edoor.channel_managers.utils.get_cm_sync_log_data", {
    docname: dialogRef.value.data.docname
  })
  if (res.data) {
    log.value = res.data
  }


}

function onRetrySync() {
  dialogRef.value.close({ retry_sync: true })
}
onMounted(async () => {

  await getLog()


})
</script>
<style scoped>
.sync-modal {
  /* margin: 30px auto; */
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08);
  padding: 20px;
}

/* Header */
.sync-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.sync-header h2 {
  margin: 0;
}

.status {
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 12px;
  margin-right: 10px;
}

.status.success {
  background: #e6f7ec;
  color: #22c55e;
}

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
  display: block;
  font-size: 12px;
  color: #888;
}

.value {
  font-weight: bold;
}

.value.danger {
  color: #ef4444;
}

/* Alert */
.alert {
  background: #fff4e5;
  color: #b45309;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
}

/* Table */
.table-container h3 {
  margin-bottom: 10px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  font-size: 13px;
  color: #666;
  border-bottom: 1px solid #eee;
  padding-bottom: 8px;
}

td {
  padding: 12px 0;
  border-bottom: 1px solid #f1f1f1;
  vertical-align: top;
}

td strong {
  font-size: 14px;
  color: #111;
}
</style>