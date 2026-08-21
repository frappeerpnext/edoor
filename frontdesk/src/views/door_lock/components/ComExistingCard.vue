<template>
  <ComDialogContent
    hideButtonOK
    :hideButtonClose="true"
  >
    <section
      class="surface-card border-1 surface-border border-round shadow-1 p-4"
    >
      <div
        class="flex align-items-center justify-content-between gap-3 mb-4"
      >
        <div>
          <div class="text-xs font-bold text-500 uppercase tracking-wider">
            Door Lock Activity
          </div>

          <div class="text-sm text-600 mt-1">
            Select one card access log and assign it to this reservation
          </div>

          <div
            v-if="doc?.name"
            class="text-xs text-primary font-bold mt-2"
          >
            Reservation Stay: {{ doc.name }}
          </div>

          <div
            v-if="doc?.guest_name"
            class="text-xs text-600 mt-1"
          >
            Guest: {{ doc.guest_name }}
          </div>

          <div
            v-if="doc?.rooms"
            class="text-xs text-600 mt-1"
          >
            Room: {{ doc.rooms }}
          </div>
        </div>

        <div class="flex align-items-center gap-2">
          <Button
            icon="pi pi-refresh"
            severity="secondary"
            text
            rounded
            aria-label="Refresh"
            :loading="loading"
            @click="getData"
          />

          <Button
            label="Assign Reservation"
            icon="pi pi-link"
            severity="primary"
            :disabled="!selectedLog || loading"
            :loading="loading"
            @click="onSave"
          />
        </div>
      </div>

      <div
        v-if="selectedLog"
        class="bg-primary-50 border-1 border-primary-200 border-round-lg p-3 mb-3"
      >
        <div class="flex align-items-center gap-3">
          <div
            class="bg-primary text-white border-round-lg flex align-items-center justify-content-center"
            style="width: 2.5rem; height: 2.5rem"
          >
            <i class="pi pi-check"></i>
          </div>

          <div class="flex-1">
            <div class="text-xs text-500">
              Selected Card Access Log
            </div>

            <div class="font-bold text-primary">
              {{ selectedLog.name }}
            </div>

            <div class="text-sm text-700 mt-1">
              Card:
              <b>{{ selectedLog.card_id || "-" }}</b>
            </div>
          </div>

          <Button
            icon="pi pi-times"
            severity="secondary"
            text
            rounded
            @click="selectedLog = null"
          />
        </div>
      </div>

      <div
        v-if="data.length"
        class="flex flex-column gap-3"
      >
        <div
          v-for="item in data"
          :key="item.name"
          class="surface-50 border-1 border-round-xl p-3 cursor-pointer"
          :class="
            selectedLog?.name === item.name
              ? 'border-primary bg-primary-50'
              : 'surface-border'
          "
          @click="selectLog(item)"
        >
          <div class="flex align-items-start gap-3">
            <div
              class="border-round-xl flex align-items-center justify-content-center flex-shrink-0"
              :class="
                selectedLog?.name === item.name
                  ? 'bg-primary text-white'
                  : 'surface-200 text-500'
              "
              style="width: 3rem; height: 3rem"
            >
              <i
                :class="
                  selectedLog?.name === item.name
                    ? 'pi pi-check'
                    : 'pi pi-credit-card'
                "
                style="font-size: 1.2rem"
              ></i>
            </div>

            <div class="flex-1 min-w-0">
              <div
                class="flex align-items-start justify-content-between gap-3"
              >
                <div>
                  <div class="font-bold text-900">
                    {{ item.status || "Unknown" }}
                  </div>

                  <div class="text-xs text-500 mt-1">
                    Log: {{ item.name }}
                  </div>

                  <div class="text-xs text-500 mt-1">
                    {{
                      item.creation
                        ? moment(item.creation).format(
                            "DD-MM-YYYY hh:mm A"
                          )
                        : "-"
                    }}
                  </div>
                </div>

                <div
                  class="text-xs font-bold px-2 py-1 border-round bg-green-50 text-green-700"
                >
                  Success
                </div>
              </div>

              <div
                class="surface-card border-1 surface-border border-round-lg p-3 mt-3"
              >
                <div class="flex align-items-center gap-3">
                  <div
                    class="bg-primary-50 text-primary border-round-lg flex align-items-center justify-content-center flex-shrink-0"
                    style="width: 2.5rem; height: 2.5rem"
                  >
                    <i class="pi pi-credit-card text-lg"></i>
                  </div>

                  <div class="flex-1 min-w-0">
                    <div class="text-xs text-500">
                      Card
                    </div>

                    <div
                      class="font-bold text-900 white-space-nowrap overflow-hidden text-overflow-ellipsis"
                    >
                      {{ item.card_id || "-" }}
                    </div>

                    <div
                      v-if="item.card_type"
                      class="text-xs text-600 mt-1"
                    >
                      {{ item.card_type }}
                    </div>
                  </div>
                </div>
              </div>

              <div class="grid mt-1">
                <div class="col-12 md:col-4">
                  <div class="text-xs text-500 mb-1">
                    Room
                  </div>

                  <div class="font-bold text-900">
                    {{ item.room || "-" }}
                  </div>

                  <div class="text-xs text-500 mt-1">
                    Lock: {{ item.lock_no || "-" }}
                  </div>
                </div>

                <div class="col-12 md:col-3">
                  <div class="text-xs text-500 mb-1">
                    Building
                  </div>

                  <div class="font-bold text-900">
                    {{ item.building || "-" }}
                  </div>
                </div>

                <div class="col-12 md:col-5">
                  <div class="text-xs text-500 mb-1">
                    Expire
                  </div>

                  <div class="font-bold text-900">
                    {{
                      item.expire
                        ? moment(item.expire).format(
                            "DD-MM-YYYY hh:mm A"
                          )
                        : "-"
                    }}
                  </div>
                </div>
              </div>

              <div
                v-if="item.fail_note || item.note"
                class="border-top-1 surface-border mt-2 pt-3"
              >
                <div class="text-xs text-500 mb-1">
                  Note
                </div>

                <div
                  class="text-sm"
                  :class="
                    item.fail_note
                      ? 'text-red-600'
                      : 'text-600'
                  "
                >
                  {{ item.fail_note || item.note }}
                </div>
              </div>

              <div
                class="flex align-items-center gap-2 text-xs text-500 mt-3"
              >
                <i class="pi pi-clock"></i>

                <ComTimeago
                  :date="item.creation"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div
        v-else
        class="surface-50 border-1 surface-border border-round min-h-10rem flex align-items-center justify-content-center gap-3 p-4 text-center"
      >
        <i
          class="pi pi-credit-card text-primary bg-primary-50 border-round flex align-items-center justify-content-center"
          style="
            width: 3rem;
            height: 3rem;
            font-size: 1.5rem;
          "
        ></i>

        <div>
          <h3 class="m-0 text-900 text-base font-bold">
            No card access log
          </h3>

          <p class="m-0 mt-2 text-600">
            No successful unassigned card access activity
            was found for this room.
          </p>
        </div>
      </div>
    </section>
  </ComDialogContent>
</template>

<script setup>
import { onMounted,ref,inject,createUpdateDoc } from '@/plugin';

const dialogRef = inject("dialogRef")
const moment = inject("$moment")

const doc = ref({})
const data = ref([])
const selectedLog = ref(null)
const loading = ref(false)

const serverUrl =
  window.location.protocol +
  "//" +
  window.location.hostname +
  ":" +
  window.setting.backend_port

async function getData() {
  loading.value = true

  try {
    const roomIds = [
      ...new Set(
        (doc.value?.stays || [])
          .map(stay => stay.room_id)
          .filter(Boolean)
      )
    ]

    if (!roomIds.length) {
      data.value = []
      return
    }

    const results = await Promise.all(
      roomIds.map(roomId =>
        app.getDocList("Door Lock Log", {
          fields: [
            "name",
            "creation",
            "status",
            "reservation_stay",
            "guest.customer_name_en as guest",
            "room.room_number as room",
            "room as room_id",
            "building",
            "note",
            "fail_note",
            "lock_no",
            "card_type.card_type as card_type",
            "expire",
            "card_id"
          ],

          filters: [
            ["property", "=", window.property_name],
            ["status", "=", "Success"],
            ["reservation_stay", "is", "not set"],
            ["room", "=", roomId],
            ["card_type", "=", "06"]
          ],

          orderBy: {
            field: "creation",
            order: "desc"
          }
        })
      )
    )

    const logs = results.flatMap(
      result => result.data || []
    )

    const uniqueLogs = [
      ...new Map(
        logs.map(item => [item.name, item])
      ).values()
    ]

    uniqueLogs.sort(
      (a, b) =>
        new Date(b.creation) -
        new Date(a.creation)
    )

    data.value = uniqueLogs
    selectedLog.value = null

  } catch (error) {
    console.error(
      "Failed to load Door Lock Log:",
      error
    )

    data.value = []

  } finally {
    loading.value = false
  }
}
function selectLog(item) {
  if (selectedLog.value?.name === item.name) {
    selectedLog.value = null
    return
  }

  selectedLog.value = item
}
function onSave() {
  loading.value = true

  if (!selectedLog.value) {
    loading.value = false
    return
  }

  if (!doc.value?.name) {
    loading.value = false
    return
  }

  const doorLockLog = {
    name: selectedLog.value.name,
    reservation_stay: doc.value.name,
    guest: doc.value?.guest,
  }

  createUpdateDoc(
    "Door Lock Log",
    doorLockLog,
  )
    .then((r) => {
      dialogRef.value.close(r)
      loading.value = false
      
    })
    .catch((er) => {
      console.error(
        "Failed to assign reservation:",
        er
      )

      loading.value = false
    })
    
}


onMounted(async () => {
  if (dialogRef?.value?.data) {
    doc.value = dialogRef.value.data
  }

  await getData()
})

defineExpose({
  getData
})
</script>