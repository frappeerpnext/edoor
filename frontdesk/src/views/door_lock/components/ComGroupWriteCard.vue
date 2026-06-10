<template>
  <ComDialogContent hideButtonClose hideButtonOK  :hideIcon="false">
    <div class="group-write-card grid">
      <div class="col-12 lg:col-8">
      <div class="group-panel surface-card border-1 surface-border border-round shadow-1">
        <div class="panel-header">
          <div>
            <div class="text-sm text-500 font-medium mb-1">Group Reservation</div>
            <h2 class="m-0 text-900">Issue Guest Cards</h2>
          </div>
          <span class="reservation-count">
            <i class="pi pi-users"></i>
            {{ data?.length || 0 }}
          </span>
        </div>

        <div class="grid formgrid p-fluid">
          <div class="col-12 md:col-8">
            <label class="field-label">Reservation</label>
            <ComAutoComplete
              v-model="doc.reservation"
              placeholder="Select Reservation"
              doctype="Reservation"
              class="w-full"
              :filters="reservation_filter"
              @onSelected="onReservationSelected"
            />
          </div>

          <div class="col-12 md:col-4">
            <label class="field-label">Group Departure Time</label>
            <Calendar selectOtherMonths class="w-full" v-model="departureTime" timeOnly />
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
            <label for="note-text" class="field-label">Note</label>
            <Textarea
              v-model="note"
              id="note-text"
              rows="3"
              cols="50"
              placeholder="Optional note for card writing"
              class="w-full"
            />
          </div>
        </div>

        <div v-if="data?.length > 0" class="reservation-list">
          <div
            v-for="stay in data"
            :key="stay.name"
            class="reservation-card border-1 surface-border border-round"
            :class="{ issued: stay.issue_card }"
          >
            <div class="reservation-card-header">
              <div class="min-w-0">
                <div class="flex align-items-center gap-2 flex-wrap">
                  <h3 class="m-0 text-900">{{ stay.name }}</h3>
                  <span
                    v-if="stay.reservation_status"
                    class="reservation-status-chip"
                    :style="{ color: stay.status_color || 'var(--primary-color)', backgroundColor: getStatusBackground(stay.status_color) }"
                  >
                    {{ stay.reservation_status }}
                  </span>
                  <span v-if="stay.issue_card" class="issued-badge">
                    <i class="pi pi-check-circle"></i>
                    Issued
                  </span>
                  <span
                    v-if="getCardStatus(stay)"
                    class="card-status-chip"
                    :class="getCardStatus(stay) == 'Release' ? 'release' : 'issue'"
                  >
                    {{ getCardStatus(stay) }}
                  </span>
                  <span v-else class="pending-badge">
                    <i class="pi pi-clock"></i>
                    Pending
                  </span>
                </div>
                <div class="text-600 mt-1">
                  {{ stay.guest || "-" }} - {{ stay.guest_name || "-" }}
                </div>
              </div>

              <div class="card-actions">
                <div v-if="stay?.stays?.length > 0" class="room-list compact">
                  <div v-for="room in stay.stays" :key="room.room_id" class="room-choice">
                    <Button
                      :label="room.room_number"
                      :severity="stay.selected_room == room.room_id ? 'warning' : 'secondary'"
                      :outlined="stay.selected_room != room.room_id"
                      class="room-button"
                      size="small"
                      @click="onSelectRoom(stay, room.room_id)"
                    />
                    <span v-if="isRoomIssued(stay, room)" class="room-issued-label">
                      <i class="pi pi-check-circle"></i>
                      Issued
                    </span>
                  </div>
                </div>

                <Button
                  label="Issue Guest Card"
                  icon="pi pi-key"
                  :severity="stay.issue_card ? 'warning' : 'primary'"
                  :loading="stay.writing"
                  size="small"
                  @click="writeCard(stay)"
                />
                <Button
                  label="Check Out Card"
                  icon="pi pi-sign-out"
                  severity="secondary"
                  :loading="stay.checkoutWriting"
                  size="small"
                  outlined
                  @click="writeCheckOutCard(stay)"
                />
              </div>
            </div>

            <div v-if="stay.issue_card" class="issued-info surface-50 border-1 surface-border border-round">
              <i class="pi pi-credit-card"></i>
              <span>{{ getIssueCardLabel(stay.issue_card) }}</span>
            </div>

            <div class="stay-meta">
              <span>
                <strong>Arrival</strong>
                {{ stay.arrival_date ? moment(stay.arrival_date).format("DD-MM-YYYY") : "-" }}
              </span>
              <span>
                <strong>Departure</strong>
                {{ stay.departure_date ? moment(stay.departure_date).format("DD-MM-YYYY") : "-" }}
              </span>
              <span>
                <strong>Time</strong>
                {{ formatTime(stay.departure_time) }}
              </span>
            </div>

          </div>
        </div>

        <div v-else class="empty-state surface-50 border-1 surface-border border-round">
          <i class="pi pi-id-card"></i>
          <div>
            <h3 class="m-0 text-900">No reservation stays selected</h3>
            <p class="m-0 mt-2 text-600">Select a group reservation to see guest stays and issue cards.</p>
          </div>
        </div>
      </div>
      </div>

      <div class="col-12 lg:col-4">
        <div class="instruction-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="image-wrap">
            <img src="@/assets/images/key_card.jpg" alt="Guest key card" />
          </div>

          <div class="instruction-content">
            <span class="instruction-badge">
              <i class="pi pi-key"></i>
              Group Key Writer
            </span>
            <h2 class="mb-3 mt-3 text-900">Issue Group Cards</h2>
            <p class="text-600 line-height-3 m-0">
              Select a group reservation, choose the room for each stay, and place the key card on the reader/writer before writing.
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
import { ref, inject, onMounted } from "vue"
import ComCheckCardButton from "@/views/door_lock/components/ComCheckCardButton.vue"
const moment = inject("$moment")
const dialogRef = inject("dialogRef");

const data = ref([])
const doc = ref({})
const note = ref("")
const departureTime = ref(null)
const selectedReason = ref("Guest Checked In")
const reservation_filter = ref({
  property: window.property_name
})

function onSelectRoom(stay, room_id) {
  stay.selected_room = room_id
}

function normalizeStay(stay) {
  return {
    ...stay,
    selected_room: stay.selected_room || stay.stays?.[0]?.room_id || "",
    writing: false,
    checkoutWriting: false
  }
}

function setDefaultDepartureTime(stays) {
  const firstTime = stays?.find(stay => stay.departure_time)?.departure_time
  if (firstTime) {
    departureTime.value = moment(firstTime, "HH:mm:ss.SSSSSS").toDate()
  }
}

function formatTime(value) {
  if (!value) return "-"
  return moment(value, "HH:mm:ss.SSSSSS").format("HH:mm")
}

function getIssueCardLabel(issueCard) {
  if (!issueCard) return "-"
  if (typeof issueCard == "string") return issueCard
  return issueCard.card_id || issueCard.name || issueCard.card_type || "Card already issued"
}

function getCardStatus(stay) {
  if (!stay.issue_card || typeof stay.issue_card != "object") return ""
  return stay.issue_card.status || ""
}

function getStatusBackground(color) {
  if (!color) return "var(--primary-50)"
  return `${color}1a`
}

function isRoomIssued(stay, room) {
  const issueCard = stay.issue_card
  if (!issueCard) return false

  if (Array.isArray(issueCard)) {
    return issueCard.some(card => card.room_id == room.room_id || card.room == room.room_id || card.room_number == room.room_number)
  }

  if (typeof issueCard == "object") {
    if (issueCard.room_id || issueCard.room || issueCard.room_number) {
      return issueCard.room_id == room.room_id || issueCard.room == room.room_id || issueCard.room_number == room.room_number
    }
  }

  return stay.stays?.length == 1
}

function getDepartureDateTime(stay) {
  const time = departureTime.value
    ? moment(departureTime.value).format("HH:mm:ss")
    : stay.departure_time

  return moment(`${stay.departure_date} ${time}`).format("YYYY-MM-DD HH:mm:ss")
}

function getNote() {
  return [selectedReason.value, note.value].filter(Boolean).join(" ")
}

async function onReservationSelected(val) {
  if (val.value) {
    await getData(val.value);
  } else {
    data.value = []
  }
}

async function writeCard(stay) {
  if (!stay?.selected_room) {
    app.toast?.add({ severity: "warn", summary: "Room Required", detail: "Please select a room.", life: 3000 })
    return
  }

  stay.writing = true
  const l = await window.showLoading("Writing guest card...");
  const res = await app.postApi(
    "edoor.integration.door_lock.china.integration.write_guest_card",
    {
      property: window.property_name,
      stay_data: {
        reservation_stay: stay.name,
        room_id: stay.selected_room,
        departure_time: getDepartureDateTime(stay),
        note: getNote()
      }
    }
  )
  l.close();
  stay.writing = false

  if (res.data) {
    stay.issue_card = typeof res.data == "object"
      ? { ...res.data, room_id: res.data.room_id || stay.selected_room }
      : { name: res.data, room_id: stay.selected_room }
    stay.departure_time = departureTime.value
      ? moment(departureTime.value).format("HH:mm:ss")
      : stay.departure_time
    if (doc.value.reservation) {
      await getData(doc.value.reservation)
    }
  }
}

async function writeCheckOutCard(stay) {
  if (!stay?.selected_room) {
    app.toast?.add({ severity: "warn", summary: "Room Required", detail: "Please select a room.", life: 3000 })
    return
  }

  stay.checkoutWriting = true
  const l = await window.showLoading("Writing check out card...");
  const res = await app.postApi(
    "edoor.integration.door_lock.china.integration.write_check_out_card",
    {
      property: window.property_name,
      stay_data: {
        reservation_stay: stay.name,
        room_id: stay.selected_room,
        note: getNote()
      }
    }
  )
  l.close();
  stay.checkoutWriting = false

  if (res.data && doc.value.reservation) {
    await getData(doc.value.reservation)
  }
}

 
async function getData(reservation) {
  const res = await app.getApi("edoor.integration.door_lock.log.get_reservation_stay_for_group_write_card", {
    property: window.property_name,
    reservation: reservation
  })
  if (res.data) {
    data.value = res.data.map(normalizeStay)
    setDefaultDepartureTime(data.value)
  }
}

onMounted(async () => {
  if (dialogRef.value.data?.reservation) {
    doc.value.reservation = dialogRef.value.data.reservation
    await getData(dialogRef.value.data.reservation)
  }
})
</script>

<style scoped>
.group-write-card {
  margin: 0 auto;
}

.group-panel,
.instruction-panel {
  height: 100%;
}

.group-panel {
  padding: 1.5rem;
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

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-bottom: 1.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--surface-border);
}

.reservation-count {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.45rem 0.75rem;
  border-radius: 6px;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 0.875rem;
  font-weight: 700;
  white-space: nowrap;
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

.reason-list,
.room-list {
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

.reservation-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 1rem;
}

.reservation-card {
  padding: 0.75rem;
  background: var(--surface-card);
}

.reservation-card.issued {
  border-color: var(--green-200);
  background: linear-gradient(0deg, var(--green-50), var(--surface-card) 55%);
}

.reservation-card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.card-actions {
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
  max-width: 55%;
}

.issued-badge,
.pending-badge,
.reservation-status-chip,
.card-status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.2rem 0.45rem;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 700;
}

.reservation-status-chip {
  border: 1px solid currentColor;
}

.issued-badge {
  color: var(--green-700);
  background: var(--green-50);
}

.card-status-chip.issue {
  color: var(--blue-700);
  background: var(--blue-50);
}

.card-status-chip.release {
  color: var(--purple-700);
  background: var(--purple-50);
}

.pending-badge {
  color: var(--orange-700);
  background: var(--orange-50);
}

.issued-info {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.55rem;
  margin-bottom: 0.5rem;
  color: var(--green-700);
  font-size: 0.8rem;
  font-weight: 700;
}

.stay-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-bottom: 0.5rem;
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.stay-meta strong {
  margin-right: 0.25rem;
  color: var(--text-color);
  font-weight: 700;
}

.room-button {
  min-width: 3.5rem;
  padding-top: 0.35rem;
  padding-bottom: 0.35rem;
}

.room-list.compact {
  justify-content: flex-end;
  gap: 0.35rem;
}

.room-choice {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
}

.room-issued-label {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.4rem;
  border-radius: 6px;
  color: var(--green-700);
  background: var(--green-50);
  font-size: 0.7rem;
  font-weight: 700;
}

.empty-state {
  min-height: 12rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
  margin-top: 1.25rem;
  text-align: center;
}

.empty-state > i {
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
  .group-panel,
  .instruction-panel {
    padding: 1rem;
  }

  .panel-header,
  .reservation-card-header,
  .empty-state {
    align-items: flex-start;
    flex-direction: column;
  }

  .card-actions {
    max-width: 100%;
    justify-content: flex-start;
  }

  .empty-state {
    text-align: left;
  }
}
</style>
