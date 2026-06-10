<template>
  <ComDialogContent hideButtonClose titleButtonOK="Write Staff Card Now" :hideIcon="false" @onOK="submit">
    
    <div class="write-staff-card grid">
      <div class="col-12 lg:col-8">
        <div class="write-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="panel-header">
            <div>
              <div class="text-sm text-500 font-medium mb-1">Hotel Staff Access</div>
              <h2 class="m-0 text-900">Write Staff Key Card</h2>
            </div>
            <i class="pi pi-id-card header-icon"></i>
          </div>

          <div class="grid formgrid p-fluid">
            <div class="col-12 md:col-7">
              <label class="field-label">Employee</label>
              <ComAutoComplete
                v-model="employee"
                placeholder="Select Employee"
                doctype="Employee"
                class="w-full"
                @onSelected="onSelectEmployee"
              />
            </div>

            <div class="col-12 md:col-5">
              <label class="field-label">Expire Date & Time</label>
              <Calendar
                v-model="expireDate"
                class="w-full"
                showTime
                showSeconds
                hourFormat="24"
                dateFormat="dd-mm-yy"
                showIcon
              />
            </div>

            <div class="col-12">
              <div class="card-type-box surface-50 border-1 surface-border border-round">
                <label class="field-label">Chip Card Type</label>
                <div class="chip-list">
                  <Chip
                    v-for="card in cardTypes"
                    :key="card.value"
                    :label="card.label"
                    :icon="card.icon"
                    class="select-chip"
                    :class="{ selected: selectedCardType == card.value }"
                    @click="selectCardType(card.value)"
                  />
                </div>
              </div>
            </div>

            <div class="col-12">
              <div class="access-box surface-50 border-1 surface-border border-round">
                <div class="access-header">
                  <div>
                    <label class="field-label mb-1">Access Scope</label>
                    <div class="text-sm text-500">{{ accessHelpText }}</div>
                  </div>
                  <span class="scope-badge">
                    <i class="pi pi-lock-open"></i>
                    {{ selectedCardLabel }}
                  </span>
                </div>

                <div class="grid formgrid p-fluid">
                  <div class="col-12 md:col-4">
                    <label class="field-label">Area</label>
                    <InputNumber
                      v-model="area"
                      placeholder="Enter Area"
                      class="w-full"
                      :min="0"
                      :useGrouping="false"
                      :disabled="isEmergencyCard || isMasterCard"
                    />
                  </div>

                  <div class="col-12 md:col-4">
                    <label class="field-label">Building</label>
                    <InputNumber
                      v-model="building"
                      placeholder="Enter Building"
                      class="w-full"
                      :min="0"
                      :useGrouping="false"
                      :disabled="disableBuildingAndFloor"
                    />
                  </div>

                  <div class="col-12 md:col-4">
                    <label class="field-label">Floor</label>
                    <InputNumber
                      v-model="floor"
                      placeholder="Enter Floor"
                      class="w-full"
                      :min="0"
                      :useGrouping="false"
                      :disabled="disableBuildingAndFloor || isBuildingCard"
                    />
                  </div>
                </div>
              </div>
            </div>

            <div class="col-12">
              <label for="staff-card-note" class="field-label">Note</label>
              <Textarea
                v-model="note"
                id="staff-card-note"
                rows="3"
                cols="50"
                placeholder="Optional note for staff card writing"
                class="w-full"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 lg:col-4">
        <div class="employee-panel surface-card border-1 surface-border border-round shadow-1">
          <div class="employee-profile">
            <div v-if="data?.photo" class="employee-photo">
              <img :src="data.photo" :alt="data.employee_name || 'Employee photo'" />
            </div>
            <div v-else class="employee-avatar">
              <i class="pi pi-user"></i>
            </div>

            <div class="min-w-0">
              <div class="text-sm text-500 font-medium mb-1">Selected Employee</div>
              <h3 class="m-0 text-900">{{ data?.employee_name || "No employee selected" }}</h3>
              <div class="text-sm text-600 mt-2">{{ data?.employee_code || data?.name || "-" }}</div>
            </div>
          </div>

          <div class="employee-summary">
            <div class="summary-item">
              <span>Gender</span>
              <strong>{{ data?.gender || "-" }}</strong>
            </div>
            <div class="summary-item">
              <span>Position</span>
              <strong>{{ data?.position || "-" }}</strong>
            </div>
          </div>

          <div class="holding-section">
            <div class="holding-header">
              <label class="field-label m-0">Current Card Holding</label>
              <span class="holding-count">{{ currentCardHolding.length }}</span>
            </div>

            <div v-if="currentCardHolding.length > 0" class="holding-list">
              <div
                v-for="(card, index) in currentCardHolding"
                :key="`${card.card_type}-${index}`"
                class="holding-card border-1 surface-border border-round"
              >
                <div class="holding-card-header">
                  <span class="card-name">{{ card.card_type || "-" }}</span>
                  <span class="status-chip" :class="getStatusClass(card.status)">
                    {{ card.status || "-" }}
                  </span>
                </div>
                <div class="holding-meta">
                  <span v-if="card.buiding || card.building">
                    <strong>Building</strong>
                    {{ card.buiding || card.building }}
                  </span>
                  <span v-if="card.floor">
                    <strong>Floor</strong>
                    {{ card.floor }}
                  </span>
                  <span>
                    <strong>Expire</strong>
                    {{ formatDateTime(card.expire) }}
                  </span>
                </div>
              </div>
            </div>

            <div v-else class="empty-holding surface-50 border-1 surface-border border-round">
              <i class="pi pi-credit-card"></i>
              <span>No active staff cards found.</span>
            </div>
          </div>

          <div class="writer-help surface-50 border-1 surface-border border-round">
            <span class="instruction-badge">
              <i class="pi pi-key"></i>
              Key Writer
            </span>
            <p class="text-600 line-height-3 m-0 mt-3">
              Select the employee, choose the staff card type and access scope, then place the chip card on the writer.
            </p>
          </div>
        </div>
      </div>
    </div>
  </ComDialogContent>
</template>

<script setup>
import { computed, inject, ref, watch } from "vue"

const moment = inject("$moment")

const cardTypes = [
  { label: "Emergency Card", value: "A", icon: "pi pi-exclamation-triangle" },
  { label: "Master Card", value: "B", icon: "pi pi-shield" },
  { label: "Floor Card", value: "D", icon: "pi pi-building" },
  { label: "Building Card", value: "C", icon: "pi pi-home" },
  { label: "Area Card", value: "08", icon: "pi pi-map-marker" }
]

const employee = ref("")
const area = ref(null)
const building = ref(null)
const floor = ref(null)
const note = ref("")
const expireDate = ref(moment().add(1, "year").toDate())
const selectedCardType = ref("B")
const data = ref({})

const currentCardHolding = computed(() => data.value?.current_card_holding || [])
const selectedCard = computed(() => cardTypes.find(card => card.value == selectedCardType.value) || cardTypes[0])
const selectedCardLabel = computed(() => selectedCard.value.label)
const isEmergencyCard = computed(() => selectedCardType.value == "A")
const isMasterCard = computed(() => selectedCardType.value == "B")
const isAreaCard = computed(() => selectedCardType.value == "08")
const isBuildingCard = computed(() => selectedCardType.value == "C")
const disableBuildingAndFloor = computed(() => isEmergencyCard.value || isMasterCard.value || isAreaCard.value)
const accessHelpText = computed(() => {
  if (isEmergencyCard.value) return "Emergency cards do not require area, building, or floor selection."
  if (isMasterCard.value) return "Master cards do not require area, building, or floor selection."
  if (isAreaCard.value) return "Area card selected. Building and floor are disabled."
  if (isBuildingCard.value) return "Building card selected. Floor is disabled."
  return "Floor card selected. Choose building and floor access."
})

watch(selectedCardType, () => {
  if (isEmergencyCard.value || isMasterCard.value) {
    area.value = null
    building.value = null
    floor.value = null
  }

  if (isAreaCard.value) {
    building.value = null
    floor.value = null
  }

  if (isBuildingCard.value) {
    floor.value = null
  }
})

function selectCardType(cardType) {
  selectedCardType.value = cardType
}

function formatDateTime(value) {
  if (!value) return "-"
  return moment(value).format("DD-MM-YYYY HH:mm:ss")
}

function getStatusClass(status) {
  const normalizedStatus = (status || "").toLowerCase()
  if (normalizedStatus == "issue" || normalizedStatus == "issued") return "issue"
  if (normalizedStatus == "release" || normalizedStatus == "released") return "release"
  return ""
}

async function onSelectEmployee(val) {
  if (val.value) {
    const res = await app.getApi("edoor.integration.door_lock.utils.get_employee_info", {
      property: window.property_name,
      employee: val.value,
      emplopyee: val.value
    })
    data.value = res.data || {}
  } else {
    data.value = {}
  }
}

function getWritePayload() {
  return {
    employee: data.value?.name || employee.value,
    card_type: selectedCardType.value,
    card_type_name: cardTypes.find(x=>x.value==selectedCardType.value).label,
    area: area.value ?? "",
    building: building.value ?? "",
    floor: floor.value ?? "",
    expire: moment(expireDate.value).format("YYYY-MM-DD HH:mm:ss"),
    note: note.value || ""
  }
}

function validateAccessScope() {
  if (isAreaCard.value && area.value == null) {
    app.utils.showWarning("Area Required", "Please enter area.")
    return false
  }

  if (isBuildingCard.value && building.value == null) {
    app.utils.showWarning("Building Required", "Please enter building.")
    return false
  }

  if (selectedCardType.value == "D" && floor.value == null) {
    app.utils.showWarning("Floor Required", "Please enter floor.")
    return false
  }

  return true
}

async function submit() {
  if (!data.value?.name && !employee.value) {
    app.utils.showWarning("Employee Required","Please select an employee.")
    return
  }
  
  if (!selectedCardType.value) {
    app.utils.showWarning("Card Type Required","Please select card type.")
    return
  }

  if (!validateAccessScope()) return

  const isConfirm = await app.utils.onConfirm("Write Staff Card", "Are you sure you want to issue this staff card?")
  if (!isConfirm) return

  const l = await window.showLoading("Writing staff card...")
  await app.postApi(
    "edoor.integration.door_lock.china.integration.write_employee_card",
    {
      property: window.property_name,
      data: getWritePayload()
    }
  )
  l.close()
}
</script>

<style scoped>
.write-staff-card {
  margin: 0 auto;
}

.write-panel,
.employee-panel {
  height: 100%;
}

.write-panel,
.employee-panel {
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

.card-type-box,
.access-box,
.writer-help {
  padding: 1rem;
}

.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.select-chip {
  cursor: pointer;
  border: 1px solid var(--surface-border);
  color: var(--text-color);
  background: var(--surface-card);
  font-weight: 700;
  transition: background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
}

.select-chip:hover {
  border-color: var(--primary-200);
  background: var(--primary-50);
  color: var(--primary-color);
}

.select-chip.selected {
  border-color: var(--primary-color);
  color: var(--primary-color-text);
  background: var(--primary-color);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.access-header,
.holding-header,
.holding-card-header,
.employee-profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.access-header {
  margin-bottom: 1rem;
}

.scope-badge,
.holding-count,
.instruction-badge,
.status-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
}

.scope-badge,
.instruction-badge {
  padding: 0.35rem 0.65rem;
  color: var(--primary-color);
  background: var(--primary-50);
}

.employee-panel {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.employee-profile {
  justify-content: flex-start;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--surface-border);
}

.employee-photo,
.employee-avatar {
  width: 4.5rem;
  height: 4.5rem;
  flex: 0 0 auto;
  overflow: hidden;
  border-radius: 8px;
  background: var(--surface-100);
}

.employee-photo img {
  width: 100%;
  height: 100%;
  display: block;
  object-fit: cover;
}

.employee-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-color);
  background: var(--primary-50);
  font-size: 2rem;
}

.employee-summary {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  overflow: hidden;
  border: 1px solid var(--surface-border);
  border-radius: 6px;
}

.summary-item {
  min-height: 4rem;
  padding: 0.875rem 1rem;
  border-right: 1px solid var(--surface-border);
}

.summary-item:last-child {
  border-right: 0;
}

.summary-item span {
  display: block;
  margin-bottom: 0.25rem;
  color: var(--text-color-secondary);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.summary-item strong {
  display: block;
  color: var(--text-color);
  font-size: 0.95rem;
  font-weight: 700;
  word-break: break-word;
}

.holding-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.holding-count {
  min-width: 1.75rem;
  height: 1.75rem;
  justify-content: center;
  color: var(--primary-color);
  background: var(--primary-50);
}

.holding-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.holding-card {
  padding: 0.75rem;
  background: var(--surface-card);
}

.card-name {
  color: var(--text-color);
  font-weight: 800;
}

.status-chip {
  padding: 0.2rem 0.45rem;
  color: var(--text-color-secondary);
  background: var(--surface-100);
}

.status-chip.issue {
  color: var(--green-700);
  background: var(--green-50);
}

.status-chip.release {
  color: var(--purple-700);
  background: var(--purple-50);
}

.holding-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.85rem;
  margin-top: 0.65rem;
  color: var(--text-color-secondary);
  font-size: 0.8rem;
}

.holding-meta strong {
  margin-right: 0.25rem;
  color: var(--text-color);
}

.empty-holding {
  min-height: 7rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 1rem;
  color: var(--text-color-secondary);
  text-align: center;
}

.empty-holding i {
  color: var(--primary-color);
  font-size: 1.25rem;
}

h2 {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: 0;
}

h3 {
  font-size: 1.05rem;
  font-weight: 800;
  letter-spacing: 0;
}

@media (max-width: 767px) {
  .write-panel,
  .employee-panel {
    padding: 1rem;
  }

  .panel-header,
  .access-header {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (max-width: 575px) {
  .employee-summary {
    grid-template-columns: 1fr;
  }

  .summary-item {
    border-right: 0;
    border-bottom: 1px solid var(--surface-border);
  }

  .summary-item:last-child {
    border-bottom: 0;
  }
}
</style>
