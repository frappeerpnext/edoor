<template>
  <div> 
    <div class="connection-wrapper">
    <div class="connection-title">{{ $t('CONNECTION') }}</div>
 <!-- 1. LOADING MESSAGE -->
  <StatusMessage 
    :show="apiCheck.loading"
    status="In Progress"
    :title="$t('Verifying Credentials')"
  >
    {{ $t('Please wait while we establish a secure connection with the Channel Manager API...') }}
  </StatusMessage>

  <!-- 2. ERROR MESSAGE (If any credential is not authenticated) -->
  <StatusMessage 
    :show="credentailData?.find(x => !x.isAuthenticated) && !apiCheck.loading"
    status="Pending"
    :title="$t('Action Required')"
  >
    {{ $t('Please review and verify the Channel Manager integration details, including the URL, property code, username, and password. Kindly ensure all information is correct before proceeding.') }}
  </StatusMessage>

  <!-- 3. SUCCESS MESSAGE (If all are authenticated) -->
  <StatusMessage 
    :show="!credentailData?.find(x => !x.isAuthenticated) && !apiCheck.loading && apiCheck.reachable"
    status="Complete"
    :title="$t('Connection Successful')"
  >
    {{ $t('Your credentials have been verified. You can now safely proceed to the next step of the data upload.') }}
    <Button 
    @click="getData" 
 :loading="apiCheck.loading"
severity="info" 
style="height: 1px;"
    :label="$t('Revalidate Credential')"
  text/>
  </StatusMessage>
    <ComCMCredential 
      v-for="value in credentailData" 
      :key="value.title" 
      :label="value.label" 
      :value-data="value.value"
      :status="value.status" 
      :loading="apiCheck.loading"
      :is-authenticated="value.isAuthenticated" 
    />

  </div>

  
      <!-- Footer -->
    <div class="footer flex gap-2">

  <Button 
    @click="onBack" 
    class="btn-back" 
    :disabled="activeStepIndex === 1"
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <Button 
    @click="onChangeDataUploadStep(1)" 
    class="btn-next" 
    :disabled="credentailData?.find(x=>!x.isAuthenticated)"
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Next')"
  />
</div>
  </div>
</template>
<script setup>


import { ref, onMounted, inject, computed , watch } from '@/plugin'
import { i18n } from '@/i18n';
import ComDataUpload from '@/views/channel_managers/channel_manager/components/ComDataUpload.vue';
import ComCMCredential from '@/views/channel_managers/channel_manager/components/ComCMCredential.vue';
import { useCMDashboard } from "@/views/channel_managers/channel_manager/hooks/useCMDashboard";
import StatusMessage from '@/views/channel_managers/channel_manager/components/StatusMessage.vue'
const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem('edoor_property'))
const data = ref({})
const response = ref({})

data.value = {
  room_types: 0,
  rate_plans: 0
}
const {
    channelManagerData,
    dataUploadSteps,
    onChangeDataUploadStep
} = useCMDashboard()
const apiCheck = ref({
  reachable: false,
  status: null,
  loading: false,
  codeerror: null
})

function onBack(){
  dataUploadSteps.value[1].is_validate = false;
  onChangeDataUploadStep(-1)
}
async function getData() {
  try {
    apiCheck.value.loading = true

    const res = await app.getApi(
      "edoor.channel_managers.exely.property_info.send_connection_test",
      {
        property: property.name
      }
    )

    const result = res.data || {}
    response.value = result
    // =========================
    // SUCCESS / FAIL
    // =========================
    apiCheck.value.reachable = result.success || false
    apiCheck.value.status = result.message || "No response"

    // =========================
    // ERROR CODE DETECTION (SAFE)
    // =========================
    let code = null

    if (result.raw) {
      const raw = result.raw.toLowerCase()

      if (raw.includes("450")) code = 450
      else if (raw.includes("401") || raw.includes("unauthorized")) code = 401
      else if (raw.includes("invalid hotelcode")) code = 400
    }else {
      code = result.message.includes("404") ? 404 : null
    }

    apiCheck.value.codeerror = code

    apiCheck.value.loading = false
    response.value = result

  } catch (e) {
    apiCheck.value.reachable = false
    apiCheck.value.status = e.message
    apiCheck.value.codeerror =
      e.response?.status ||   // 404, 500
      e.code ||               // network
      "NETWORK_ERROR"
 
    apiCheck.value.loading = false
    
  }
  dataUploadSteps.value[1].is_validate = true
}
const credentailData = computed(() => {
  const { loading, codeerror, status } = apiCheck.value

  const isAuthError = [401, 403, 450].includes(codeerror)
  const isReady = !loading
  const isAuthenticated = isReady && !isAuthError

  return [
    {
      label: $t('API Endpoint'),
      value: channelManagerData.value.api_url || 'Not Set',
      status: loading ? $t('checking...') : status || '-',
      isAuthenticated: isReady && codeerror !== 404
    },
    {
      label: $t('Username'),
      value: channelManagerData.value.username || 'Not Set',
      status: isAuthenticated ? $t('Authenticated') : $t('Not Verified'),
      isAuthenticated
    },
    {
      label: $t('Password'),
      value: channelManagerData.value.password ? '********' : 'Not Set',
      status: isAuthenticated ? $t('Authenticated') : $t('Fix before upload'),
      isAuthenticated
    },
    {
      label: $t('Hotel Code'),
      value: channelManagerData.value.property_code || 'Not Set',
      status: isAuthenticated ? $t('Verified') : $t('Invalid / Not Checked'),
      isAuthenticated: isReady && codeerror !== 450
    }
  ]
})

 
 
onMounted(async () => {
  if (!dataUploadSteps.value[1].is_validate )
{
  await getData();
}
  
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