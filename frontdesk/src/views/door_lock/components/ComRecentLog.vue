<template>
  <section class="recent-log surface-card border-1 surface-border border-round shadow-1">
    <div class="recent-log-header">
      <div>
        <div class="text-xs font-bold text-500 uppercase tracking-wider mb-1">Door Lock Activity</div>
        <h2 class="m-0 text-900">Recent Log</h2>
      </div>
      <div class="header-actions">
        <Button icon="pi pi-refresh" severity="secondary" text rounded aria-label="Refresh" @click="getData" />
        <Button label="View all log" icon="pi pi-list" severity="secondary" outlined @click="onViewAllLog" />
      </div>
    </div>

    <DataTable
      v-if="data?.length > 0"
      :value="data"
      class="recent-log-table"
      responsiveLayout="scroll"
      stripedRows
      size="small"
    >
      <Column header="Status" style="width: 8rem">
        <template #body="{ data: item }">
          <span class="status-badge" :class="item.status == 'Success' ? 'success' : 'failed'">
            <i :class="item.status == 'Success' ? 'pi pi-check-circle' : 'pi pi-times-circle'"></i>
            {{ item.status || "-" }}
          </span>
        </template>
      </Column>

      <Column header="Card">
        <template #body="{ data: item }">
          <div class="table-main-text">{{ item.card_type || "Door Lock Card" }}</div>
          <div class="table-sub-text">{{ item.card_id || "-" }}</div>
        </template>
      </Column>

      <Column header="Reservation">
        <template #body="{ data: item }">
          <div class="table-main-text">
            <Button class="link_line_action1" @click="onOpenLink('view_reservation_stay_detail', item.reservation_stay)" link>
            {{ item.reservation_stay || "-" }}

            </Button>

            </div>
          <div class="table-sub-text">Guest {{ item.guest || "-" }}</div>
        </template>
      </Column>

      <Column header="Room">
        <template #body="{ data: item }">
          <div class="table-main-text">{{ item.room || item.room_number || "-" }}</div>
          <div class="table-sub-text">Lock {{ item.lock_no || "-" }}</div>
        </template>
      </Column>

      <Column header="Building" field="building" style="width: 7rem">
        <template #body="{ data: item }">
          {{ item.building || "-" }}
        </template>
      </Column>

      <Column header="Expire">
        <template #body="{ data: item }">
          <span v-if="item.expire">{{ moment(item.expire).format("DD-MM-YYYY hh:mm A") }}</span>
          <span v-else>-</span>
        </template>
      </Column>

      <Column header="Created">
        <template #body="{ data: item }">
          
          <ComTimeago :date="item.creation" />
        </template>
      </Column>

      <Column header="Note">
        <template #body="{ data: item }">
          <span class="note-text">{{ item.fail_note || item.note || "-" }}</span>
        </template>
      </Column>
    </DataTable>

    <div v-else class="empty-log surface-50 border-1 surface-border border-round">
      <i class="pi pi-history"></i>
      <div>
        <h3 class="m-0 text-900">No recent log</h3>
        <p class="m-0 mt-2 text-600">Door lock activity will appear here after card operations.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { inject, onMounted, ref } from 'vue';
const moment = inject("$moment")
const serverUrl = window.location.protocol + "//" + window.location.hostname + ":" + window.setting.backend_port;
async function getData(){
  const res = await app.getDocList("Door Lock Log",
  {fields:[
      "creation",
      "name",
      "status",
      "reservation_stay",
      "guest.customer_name_en as guest",
      "room.room_number as room",
      "building",
      "note",
      "lock_no",
      "card_type.card_type as card_type",
      "expire",
      "card_id"
  ], 
  filters:[["property","=",window.property_name]],
  orderBy: {
    field: 'creation',
    order: 'desc',
  }
}
)
    if (res.data){
      data.value = res.data
    }
}
const data = ref([])
function onViewAllLog() {
  window.open(serverUrl + "/app/door-lock-log")
}

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}

defineExpose({
  getData
})
onMounted(()=>{
  getData();
})
</script>

<style scoped>
.recent-log {
  padding: 1.25rem;
}

.recent-log-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;
}

.tracking-wider {
  letter-spacing: 0.05em;
}

h2 {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0;
}

h3 {
  font-size: 1rem;
  font-weight: 700;
}

.header-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 700;
  white-space: nowrap;
}

.status-badge.success {
  color: var(--green-700);
  background: var(--green-50);
}

.status-badge.failed {
  color: var(--red-700);
  background: var(--red-50);
}

.table-main-text {
  color: var(--text-color);
  font-weight: 700;
  white-space: nowrap;
}

.table-sub-text,
.note-text {
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.note-text {
  display: block;
  max-width: 16rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-log-table :deep(.p-datatable-thead > tr > th) {
  background: var(--surface-50);
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.recent-log-table :deep(.p-datatable-tbody > tr > td) {
  vertical-align: middle;
}

.empty-log {
  min-height: 10rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  text-align: center;
}

.empty-log > i {
  width: 3rem;
  height: 3rem;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 1.5rem;
}

@media (max-width: 575px) {
  .recent-log {
    padding: 1rem;
  }

  .recent-log-header,
  .empty-log {
    align-items: flex-start;
    flex-direction: column;
  }

  .empty-log {
    text-align: left;
  }
}
</style>
