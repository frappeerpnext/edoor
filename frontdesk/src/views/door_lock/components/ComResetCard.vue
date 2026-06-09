<template>
  <ComDialogContent hideButtonClose titleButtonOK="Reset Card Info Now" :hideIcon="false" @onOK="submit">
    <div class="reset-card">
      <div class="instruction-panel surface-card border-1 surface-border border-round shadow-1">
        <div class="image-wrap">
          <video autoplay muted loop playsinline aria-label="Reset key card instruction">
            <source src="@/assets/video/card.mp4" type="video/mp4" />
          </video>
        </div>

        <div class="instruction-content">
          <span class="instruction-badge">
            <i class="pi pi-refresh"></i>
            Reset Card
          </span>
          <h2 class="mb-3 mt-3 text-900">Erase Card Information</h2>
          <p class="text-600 line-height-3 mt-0 mb-3">
            Place the key card properly on the key card reader/writer. Then click
            <strong>Reset Card Info Now</strong>.
          </p>

          <div class="warning-box border-1 border-red-200 border-round">
            <i class="pi pi-exclamation-triangle"></i>
            <div>
              <h3 class="m-0 text-red-900">Warning: This action cannot be undone</h3>
              <p class="m-0 mt-2 text-red-800 line-height-3">
                Resetting the card will erase its access data. Make sure the correct card is on the reader before continuing.
              </p>
            </div>
          </div>

          <div class="field reason-field">
            <label class="field-label">Reset Reason</label>
            <div class="reason-list">
              <Chip
                v-for="reason in resetReasons"
                :key="reason"
                :label="reason"
                class="reason-chip"
                :class="{ selected: selectedReason == reason }"
                @click="selectedReason = reason"
              />
            </div>
          </div>

          <div class="field note-field mb-0">
            <label for="note-text" class="field-label">Note</label>
            <Textarea
              v-model="note"
              id="note-text"
              rows="4"
              cols="50"
              placeholder="Add reset reason or note"
              class="w-full"
            />
          </div>
        </div>
      </div>
    </div>
    <template #footer-right>
      <Button severity="warning" label="Check Card" @click="onCheckCard"></Button>
    </template>
 </ComDialogContent>
</template>

<script setup>
import { ref,inject } from "vue"
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
import ComCheckCard from "@/views/door_lock/components/ComCheckCard.vue"
/* ================= STATE ================= */

const note = ref("")
const selectedReason = ref("Lost Card")
const resetReasons = ref([
  "Guest Check Out",
  "Lost Card",
  "Stolen Card",
  "Damaged Card",
  "Card Not Working",
  "Guest Requested Replacement",
  "Guest Forgot Card in Room",
  "Card Returned by Guest",
  "Reservation Cancelled"
])
 
 
async function submit() {
   const isConfirm = await app.utils.onConfirm("Reset Card", "Are you sure you want to reset this card?")
  if (!isConfirm) return ;
  const l = await window.showLoading("Reset card info...");
 
    const res = await app.getApi(
      "edoor.integration.door_lock.china.integration.erase_card",
      {
        property: window.property_name,
        note: [selectedReason.value, note.value].filter(Boolean).join(" - ")
      }
    )
    l.close(); 

  
}
function onCheckCard(){
  app.utils.openDialog(ComCheckCard,"Check Card");
  dialogRef.value.close();
  
}
</script>

<style scoped>
.reset-card {
  margin: 0 auto;
}

.instruction-panel {
  display: grid;
  grid-template-columns: minmax(220px, 0.9fr) minmax(280px, 1.1fr);
  align-items: center;
  gap: 1.5rem;
  padding: 1.5rem;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.image-wrap {
  width: 100%;
  border-radius: 8px;
}

.image-wrap video {
  display: block;
  width: 100%;
  border-radius: 6px;
  object-fit: cover;
}

.instruction-content {
  min-width: 0;
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

.warning-box {
  display: flex;
  gap: 0.875rem;
  padding: 1rem;
  margin-bottom: 1rem;
  background: var(--red-50);
}

.warning-box > i {
  width: 2.5rem;
  height: 2.5rem;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: var(--red-700);
  background: var(--surface-card);
  font-size: 1.25rem;
}

.reason-field,
.note-field {
  padding-top: 0.25rem;
}

.reason-field {
  margin-bottom: 1rem;
}

.reason-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.reason-chip {
  cursor: pointer;
  border: 1px solid var(--surface-border);
  color: var(--text-color);
  background: var(--surface-card);
  font-weight: 600;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.reason-chip:hover {
  border-color: var(--red-200);
  color: var(--red-700);
  background: var(--red-50);
}

.reason-chip.selected {
  border-color: var(--red-600);
  color: var(--surface-card);
  background: var(--red-600);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
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

@media (max-width: 767px) {
  .instruction-panel {
    grid-template-columns: 1fr;
    padding: 1rem;
  }

  .warning-box {
    flex-direction: column;
  }
}
</style>
