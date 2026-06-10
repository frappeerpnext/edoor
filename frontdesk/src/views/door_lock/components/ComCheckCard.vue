<template>
  <ComDialogContent hideButtonClose titleButtonOK="Check Card Info Now" :hideIcon="false" @onOK="submit">
    <div class="check-card grid">
      <div class="col-12 lg:col-7">
        <div class="check-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="panel-header">
            <div>
              <div class="text-sm text-500 font-medium mb-1">Card Reader</div>
              <h2 class="m-0 text-900">Check Card Info</h2>
            </div>
            <i class="pi pi-credit-card header-icon"></i>
          </div>

          <div v-if="data?.card_type == 'UNKNOWN' || data?.cart_type == 'UNKNOWN'" class="blank-card-state border-1 border-yellow-200 border-round">
            <i class="pi pi-info-circle"></i>
            <div>
              <h3 class="m-0 text-900">Blank Card</h3>
              <p class="m-0 mt-2 text-600 line-height-3">
                This card has no guest or check-out information.
              </p>
            </div>
          </div>

          <div v-else-if="data?.card_type || data?.cart_type" class="card-info">
            <div class="status-strip border-round">
              <div>
                <span class="status-label">Card Type</span>
                <strong>{{ data?.card_type || data?.cart_type || "-" }}</strong>
              </div>
              <span class="status-badge">
                <i class="pi pi-check-circle"></i>
                {{ data?.room_number ? "Room " + data.room_number : "Card Found" }}
              </span>
            </div>

            <div class="info-grid surface-50 border-1 surface-border border-round">
              <div class="info-item">
                <span>Reservation Stay</span>
                <strong>{{ data?.reservation_stay || "-" }}</strong>
              </div>
              <div class="info-item">
                <span>Card ID</span>
                <strong>{{ data?.ID || "-" }}</strong>
              </div>
              <div class="info-item">
                <span>Guest</span>
                <strong v-if="data?.guest || data?.guest_name">{{ data?.guest || "-" }} - {{ data?.guest_name || "-" }}</strong>
                <strong v-else>-</strong>
              </div>
              <div class="info-item">
                <span>Room</span>
                <strong>{{ data?.room_number || "-" }}</strong>
              </div>
              <div class="info-item">
                <span>Arrival</span>
                <strong v-if="data?.arrival_date">{{ moment(data.arrival_date).format("DD-MM-YYYY") }}</strong>
                <strong v-else>-</strong>
              </div>
              <div class="info-item">
                <span>Departure</span>
                <strong v-if="data?.departure_date || data?.departure_time">
                  {{ data?.departure_date ? moment(data.departure_date).format("DD-MM-YYYY") : "-" }}
                  {{ data?.departure_time ? moment(data.departure_time, "HH:mm:ss.SSSSSS").format("HH:mm") : "" }}
                </strong>
                <strong v-else>-</strong>
              </div>
              <div class="info-item">
                <span>Business Source</span>
                <strong>{{ data?.business_source || "-" }}</strong>
              </div>
            </div>

            <div v-if="data?.note" class="note-box border-1 surface-border border-round">
              <span>Note</span>
              <p class="m-0 mt-2 text-700 line-height-3">{{ data.note }}</p>
            </div>
          </div>

          <div v-else class="empty-state surface-50 border-1 surface-border border-round">
            <i class="pi pi-credit-card"></i>
            <h3 class="m-0 text-900">No card data yet</h3>
            <p class="m-0 text-600 line-height-3">
              Place the card on the reader, then click <strong>Check Card Info Now</strong>.
            </p>
          </div>
        </div>
      </div>

      <div class="col-12 lg:col-5">
        <div class="instruction-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="image-wrap">
            <video autoplay muted loop playsinline aria-label="Reset key card instruction">
            <source src="@/assets/video/card.mp4" type="video/mp4" />
          </video>
          </div>

          <div class="instruction-content">
            <span class="instruction-badge">
              <i class="pi pi-key"></i>
              Key Writer
            </span>
            <h2 class="mb-3 mt-3 text-900">Read Guest Card</h2>
            <p class="text-600 line-height-3 m-0">
              Place the key card properly on the key card reader/writer.
              Then click <strong>Check Card Info Now</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
     <template #footer-right>
      <Button severity="warning" label="Reset Card" @click="onResetCard"></Button>
    </template>
  </ComDialogContent>
</template>

<script setup>
import { ref,inject } from "vue"
import ComResetCard from "@/views/door_lock/components/ComResetCard.vue"
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
/* ================= STATE ================= */
const data = ref({})
 
 
 
async function submit() {
  const l = await window.showLoading("Checking card info...");
 
    const res = await app.getApi(
      "edoor.integration.door_lock.china.integration.read_card",
      {
        property: window.property_name
      }
    )
    l.close();
    if (res.data){
      data.value = res.data;

    }

  
}
function onResetCard(){
  dialogRef.value.close();
  app.utils.openDialog(ComResetCard,"Reset Card");
}
</script>

<style scoped>
.check-card {
  margin: 0 auto;
}

.check-panel,
.instruction-panel {
  height: 100%;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.check-panel {
  padding: 1.5rem;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--surface-border);
}

.header-icon {
  width: 2.75rem;
  height: 2.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 1.25rem;
}

.card-info {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.blank-card-state {
  min-height: 20rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  color: var(--yellow-900);
  background: var(--yellow-50);
}

.blank-card-state > i {
  width: 3.25rem;
  height: 3.25rem;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--yellow-700);
  background: var(--surface-card);
  font-size: 1.5rem;
}

.status-strip {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  color: var(--primary-color);
  background: var(--primary-50);
}

.status-label,
.info-item span,
.raw-header {
  display: block;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-strip strong {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-color);
  font-size: 1.1rem;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  background: var(--surface-card);
  font-size: 0.875rem;
  font-weight: 700;
  white-space: nowrap;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  overflow: hidden;
}

.info-item {
  min-height: 4.25rem;
  padding: 0.875rem 1rem;
  border-right: 1px solid var(--surface-border);
  border-bottom: 1px solid var(--surface-border);
}

.info-item:nth-child(2n),
.info-item:last-child {
  border-right: 0;
}

.info-item:nth-last-child(-n + 2) {
  border-bottom: 0;
}

.info-item strong {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-color);
  font-size: 0.95rem;
  font-weight: 600;
  word-break: break-word;
}

.raw-response {
  overflow: hidden;
}

.raw-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--surface-50);
  border-bottom: 1px solid var(--surface-border);
}

.raw-text {
  max-height: 8rem;
  overflow: auto;
  padding: 1rem;
  color: var(--text-color);
  font-family: Consolas, Monaco, "Courier New", monospace;
  font-size: 0.8rem;
  line-height: 1.5;
  word-break: break-all;
}

.note-box {
  padding: 1rem;
  background: var(--surface-50);
}

.note-box span {
  display: block;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.empty-state {
  min-height: 20rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 2rem;
  text-align: center;
}

.empty-state > i {
  width: 3rem;
  height: 3rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 1.5rem;
}

.instruction-panel {
  min-height: 100%;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1.25rem;
  text-align: center;
}

.image-wrap {
  width: 100%;
  border-radius: 8px;
}

.image-wrap img {
  display: block;
  width: 100%;
  border-radius: 6px;
  object-fit: cover;
}

.instruction-content {
  margin: 0 auto;
}

.instruction-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.65rem;
  border-radius: 6px;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 0.8rem;
  font-weight: 600;
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

@media (max-width: 575px) {
  .check-panel,
  .instruction-panel {
    padding: 1rem;
  }

  .status-strip {
    align-items: flex-start;
    flex-direction: column;
  }

  .info-grid {
    grid-template-columns: 1fr;
  }

  .info-item,
  .info-item:nth-child(2n),
  .info-item:last-child {
    border-right: 0;
    border-bottom: 1px solid var(--surface-border);
  }

  .info-item:last-child {
    border-bottom: 0;
  }

  .blank-card-state {
    align-items: center;
    flex-direction: column;
    text-align: center;
  }
}
</style>
