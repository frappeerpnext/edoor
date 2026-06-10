<template>
  <ComDialogContent hideButtonClose titleButtonOK="Write Guest Card Now" :hideIcon="false" @onOK="submit">
    <div class="write-guest-card grid">
      <div class="col-12 lg:col-7">
        <div class="write-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="panel-header">
            <div>
              <div class="text-sm text-500 font-medium mb-1">Reservation</div>
              <h2 class="m-0 text-900">Guest Card Details</h2>
            </div>
            <i class="pi pi-id-card header-icon"></i>
          </div>

          <div class="grid formgrid p-fluid">
            <div class="col-12">
              <label class="field-label">Reservation Stay</label>
              <ComAutoComplete
                v-model="doc.reservation"
                placeholder="Select Reservation"
                doctype="Reservation Stay"
                class="w-full mb-4"
                :filters="reservation_filter"
                @onSelected="onReservationSelected"
              />
            </div>
            <div class="col-12">
              <div class="reason-box surface-50 border-1 surface-border border-round">
                <label class="field-label">Write Card Reason</label>
                <div class="reason-list">
                  <Chip
                    v-for="c in ['Guest Checked In','Additional Guest Card','Change Room','Extend Stay']"
                    :key="c"
                    :label="c"
                    class="reason-chip"
                    :class="{ selected: selectedReason == c }"
                    @click="selectedReason = c"
                  />
                </div>
              </div>
            </div>

            <div class="col-12">
              <div class="guest-summary surface-50 border-1 surface-border border-round">
                <div class="summary-item">
                  <span>Guest</span>
                  <strong>{{ doc?.guest_name || "-" }}</strong>
                </div>
                <div class="summary-item">
                  <span>Business Source</span>
                  <strong>{{ doc?.business_source || "-" }}</strong>
                </div>
                <div class="summary-item">
                  <span>Arrival</span>
                  <strong v-if="doc?.arrival_date">{{ moment(doc?.arrival_date).format("DD-MM-YYYY") }}</strong>
                  <strong v-else>-</strong>
                </div>
                <div class="summary-item">
                  <span>Departure</span>
                  <strong v-if="doc?.departure_date">{{ moment(doc?.departure_date).format("DD-MM-YYYY")}}</strong>
                  <strong v-else>-</strong>
                </div>
                <div class="summary-item">
                  <span>Departure Time</span>
                  <strong>{{ doc?.departure_time || "-" }}</strong>
                </div>
              </div>
            </div>

            <div v-if="doc" class="col-12">
              <div v-if="doc?.stays?.length > 0" class="field">
                <label class="field-label">Room</label>
                <div class="room-list">
                  <Button
                    v-for="r in doc.stays"
                    :key="r.room_id"
                    :severity="selectedRoom == r.room_id ? 'warning' : 'secondary'"
                    :label="r.room_number"
                    :outlined="selectedRoom != r.room_id"
                    class="room-button"
                    @click="onSelectRoom(r.room_id)"
                  ></Button>
                </div>
              </div>

              <div class="field">
                <label class="field-label">Departure Time</label>
                <Calendar selectOtherMonths class="w-full" v-model="doc.departure_time" timeOnly />
              </div>

              <div class="field mb-0">
                <label for="note-text" class="field-label">Reason</label>
                <Textarea
                  v-model="doc.note"
                  id="note-text"
                  rows="4"
                  cols="50"
                  placeholder="Note"
                  class="w-full"
                />
              </div>
            </div>
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
            <h2 class="mb-3 mt-3 text-900">Issue Guest Card</h2>
            <p class="text-600 line-height-3 m-0">
              Select the guest room and place the key card properly on the key card reader/writer.
              Then click <strong>Write Guest Card Now</strong>.
            </p>
          </div>
        </div>
      </div>
    </div>
      <template #footer-right>
      <ComCheckCardButton />
    </template>
  </ComDialogContent>
</template>

<script setup>
import { ref,inject,onMounted  } from "vue"
import ComCheckCardButton from "@/views/door_lock/components/ComCheckCardButton.vue"
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
/* ================= STATE ================= */
 

const doc = ref({})
const selectedRoom = ref("");
const selectedReason = ref("Guest Checked In")
const reservation_filter = ref({
  reservation_status: ["in",["Reserved","In-house"]],
  property:window.property_name

  
})
 
function onSelectRoom(room_id){
  selectedRoom.value = room_id;
}
 

async function onReservationSelected(val) {
  if (val.value){
    const res = await app.getDoc("Reservation Stay", val.value)
    doc.value = res.data
    doc.value.departure_time =  moment(doc.value.departure_date + " " + doc.value.departure_time).toDate();
   selectedRoom.value = doc.value.stays[0].room_id;


  }else {
    doc.value = {}
  }
  
}

 
async function submit() {
  const isConfirm = await app.utils.onConfirm("Write Card", "Are you sure you want to issue this card?")
  if (!isConfirm) return ;

  const l = await window.showLoading("Writing guest card...");
 
    const res = await app.postApi(
      "edoor.integration.door_lock.china.integration.write_guest_card",
      {
        "property":window.property_name,
        "stay_data": {
          
          "reservation_stay":doc.value.name,
          "room_id":selectedRoom.value,
          "departure_time":moment(doc.value.departure_time).format('YYYY-MM-DD HH:mm:ss'),
          "note":selectedReason.value + " " + (doc.value.note || "")

        }
      }
    )
    l.close();
     

  
}
onMounted(()=>{
    if(dialogRef.value.data){
      doc.value = dialogRef.value.data
      if (doc.value.stays){
        selectedRoom.value =  doc.value.stays[0].room_id;
        doc.value.departure_time =  moment(doc.value.departure_date + " " + doc.value.departure_time).toDate();
        
      }
    }
    
  
})
</script>

<style scoped>
.write-guest-card {
  
  margin: 0 auto;
}

.write-panel,
.instruction-panel {
  height: 100%;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.write-panel {
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

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.875rem;
  font-weight: 600;
}

.reason-box {
  padding: 1rem;
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
  border-color: var(--primary-200);
  background: var(--primary-50);
  color: var(--primary-color);
}

.reason-chip.selected {
  border-color: var(--primary-color);
  color: var(--primary-color-text);
  background: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.guest-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0;
  overflow: hidden;
}

.summary-item {
  min-height: 4rem;
  padding: 0.875rem 1rem;
  border-right: 1px solid var(--surface-border);
  border-bottom: 1px solid var(--surface-border);
}

.summary-item:nth-child(2n),
.summary-item:last-child {
  border-right: 0;
}

.summary-item:last-child {
  border-bottom: 0;
}

.summary-item span {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.summary-item strong {
  display: block;
  color: var(--text-color);
  font-size: 0.95rem;
  font-weight: 600;
  word-break: break-word;
}

.room-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.room-button {
  min-width: 4.25rem;
}

.instruction-panel {
  min-height: 100%;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
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

@media (max-width: 575px) {
  .write-panel,
  .instruction-panel {
    padding: 1rem;
  }

  .guest-summary {
    grid-template-columns: 1fr;
  }

  .summary-item,
  .summary-item:nth-child(2n),
  .summary-item:last-child {
    border-right: 0;
    border-bottom: 1px solid var(--surface-border);
  }

  .summary-item:last-child {
    border-bottom: 0;
  }
}
</style>
