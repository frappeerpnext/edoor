<template>
  <com-confirm-message label="Verify Credentials" text="Please ensure that all credentials are accurate and up to date before initiating the connection to the channel manager."/>

  <!-- Stats -->
  <div class="connection-wrapper">
    <div class="connection-title">{{ $t('CONNECTION') }}</div>
    <ComCMCredential 
      v-for="value in credentailData" 
      :key="value.title" 
      :label="value.label" 
      :value-data="value.value"
      :status="value.status" 
      :is-authenticated="value.isAuthenticated" 
    />
    <Message severity="warn" class="mt-4" style="border-radius: 12px;">
      <div>
        <div class="font-semibold text-lg">{{ $t('Action Required') }}</div>
        <p>{{ $t('Please update your password in the credentials section to ensure a successful upload.') }}</p>
      </div>
    </Message>

  </div>
</template>
<script setup>
import { ref, onMounted, inject, computed } from '@/plugin'
import { i18n } from '@/i18n';
import ComDataUpload from '@/views/channel_managers/channel_manager/components/ComDataUpload.vue';
import ComCMCredential from '@/views/channel_managers/channel_manager/components/ComCMCredential.vue';
const frappe = inject('$frappe')
const { t: $t } = i18n.global;
const db = frappe.db();
const property = JSON.parse(localStorage.getItem('edoor_property'))
const data = ref({})

data.value = {
  room_types: 0,
  rate_plans: 0
}

const credentailData = computed(() => [
  {
    label: $t('API Endpoint'),
    value: 'https://api.channelmanager.com/v1',
    status: $t('reachable'),
    isAuthenticated: true
  },
  {
    label: $t('Username'),
    value: 'hotel_admin',
    status: $t('authenticated'),
    isAuthenticated: true
  },
  {
    label: $t('Password'),
    value: 'Not Set',
    status: $t('Fix before upload'),
    isAuthenticated: false
  },
  {
    label: $t('Hote Code'),
    value: '123456',
    status: $t('Verified'),
    isAuthenticated: true
  }
])

const filter = [
  ['property', '=', property.name],
  ['disabled', '=', 0]
]

const getTotalRoomTypes = async () => {
  await db.getCount('Room Type', filter)
    .then((count) => {
      data.value.room_types = count
    })
}

const getTotalRatePlans = async () => {
  await db.getCount('Rate Type', filter)
    .then((count) => {
      data.value.rate_plans = count
    })
}

onMounted(() => {
  getTotalRoomTypes();
  getTotalRatePlans();
})
</script>
<style scoped>
/* Stats */
.stats {
  display: flex;
  gap: 20px;
  margin: 25px 0;
}

.progress-footer {
  display: flex;
  justify-content: space-between;
  color: #6b7280;
}

/* Progress */
.progress-card {
  background: #f9fafb;
  padding: 18px;
  border-radius: 14px;
}

.bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 10px;
  margin: 10px 0;
}

.fill {
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, #6366f1, #4f46e5);
  border-radius: 10px;
}

.connection-wrapper {
  margin-top: 20px;
  /* padding: 20px; */
  border-radius: 16px;
  background: #ffffff;
  /* box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05); */
}

.connection-title {
  font-size: 14px;
  font-weight: 600;
  color: #7b8190;
  margin-bottom: 15px;
  letter-spacing: 0.5px;
}
</style>