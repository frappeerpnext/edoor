<template>
  <div class="min-h-screen flex w-full">
    <div class="success-card w-full">
      <!-- Main Card -->
      <div class="w-full border-round-xl">
  
          <div class="flex flex-column align-items-center text-center p-4 p-md-6">
            <!-- Animated Success Icon -->
            <div class="success-icon-container mb-5">
              <div class="animated-circle">
                <i class="pi pi-check-circle success-icon"></i>
              </div>
            </div>

            <!-- Main Title -->
            <h1 class="text-4xl md:text-5xl font-bold text-900 mb-3">
              Congratulations!
            </h1>
            
            <!-- Subtitle -->
            <p class="text-xl text-600 mb-4 line-height-3">
              You have successfully uploaded all data to the <strong class="text-primary">Channel Manager</strong>.
            </p>

            <!-- Success Message Box -->
            <div class="success-message-box bg-blue-50 border-round-xl p-4 mb-5 w-full">
              <div class="flex align-items-center justify-content-center gap-3 flex-wrap">
                <i class="pi pi-sync text-blue-500 text-2xl"></i>
                <span class="text-blue-900 font-semibold text-lg">
                  From now on, any changes to reservations, rates, restrictions, or extra service prices will be automatically synchronized between the PMS and the Channel Manager in <strong>both directions</strong>.
                </span>
              </div>
            </div>

            <!-- Synchronization Features Grid -->
            <div class="grid mb-6 w-full gap-3">
              <div class="col-12 p-0">
                <div class="feature-card p-4 border-round-xl surface-card shadow-2">
                  <div class="flex align-items-center gap-3">
                    <div class="feature-icon bg-green-100 border-round-xl flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                      <i class="pi pi-calendar text-green-600 text-xl"></i>
                    </div>
                    <div class="text-left">
                      <h3 class="text-base font-semibold text-900 m-0">Reservations</h3>
                      <p class="text-sm text-500 m-0 mt-1">Real-time sync both ways</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 p-0">
                <div class="feature-card p-4 border-round-xl surface-card shadow-2">
                  <div class="flex align-items-center gap-3">
                    <div class="feature-icon bg-red-100 border-round-xl flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                     <i class="pi pi-sync text-red-600 text-xl"></i>
                    </div>
                    <div class="text-left">
                      <h3 class="text-base font-semibold text-900 m-0">Availability</h3>
                      <p class="text-sm text-500 m-0 mt-1">Real-time synchronization in both directions</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 p-0">
                <div class="feature-card p-4 border-round-xl surface-card shadow-2">
                  <div class="flex align-items-center gap-3">
                    <div class="feature-icon bg-indigo-100 border-round-xl flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                      <i class="pi pi-dollar text-indigo-600 text-xl"></i>
                    </div>
                    <div class="text-left">
                      <h3 class="text-base font-semibold text-900 m-0">Rates & Restrictions</h3>
                      <p class="text-sm text-500 m-0 mt-1">Instant updates</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 p-0">
                <div class="feature-card p-4 border-round-xl surface-card shadow-2">
                  <div class="flex align-items-center gap-3">
                    <div class="feature-icon bg-purple-100 border-round-xl flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                      <i class="pi pi-tag text-purple-600 text-xl"></i>
                    </div>
                    <div class="text-left">
                      <h3 class="text-base font-semibold text-900 m-0">Extra Service Prices</h3>
                      <p class="text-sm text-500 m-0 mt-1">Automatic adjustment</p>
                    </div>
                  </div>
                </div>
              </div>
              <div class="col-12 p-0">
                <div class="feature-card p-4 border-round-xl surface-card shadow-2">
                  <div class="flex align-items-center gap-3">
                    <div class="feature-icon bg-teal-100 border-round-xl flex align-items-center justify-content-center" style="width: 48px; height: 48px;">
                      <i class="pi pi-chart-line text-teal-600 text-xl"></i>
                    </div>
                    <div class="text-left">
                      <h3 class="text-base font-semibold text-900 m-0">Channel Manager</h3>
                      <p class="text-sm text-500 m-0 mt-1">Directional sync</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
 </div>
            <!-- Footer Action Buttons -->
           <div>
  <Button 
    @click="onChangeDataUploadStep(-1)" 
    
    icon="pi pi-arrow-left"
    :label="$t('Back')"
  />

  <Button 
    @click="onClose" 
    icon="pi pi-arrow-right"
    iconPos="right"
    :label="$t('Go to Channel Manager Dashboard')"
  />
</div>
         
        </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { useCMDashboard } from '../../../hooks/useCMDashboard';

const { onChangeDataUploadStep, onRefresh } = useCMDashboard();
const toast = useToast();

async function onClose() {
  try {
    const loading = await window.showLoading();
    await onRefresh(true);
    loading.close();
    
    // Optional: Show success toast
    toast.add({
      severity: 'success',
      summary: 'Success',
      detail: 'Redirecting to Channel Manager Dashboard...',
      life: 2000
    });
  } catch (error) {
    console.error('Error refreshing dashboard:', error);
    toast.add({
      severity: 'error',
      summary: 'Error',
      detail: 'Failed to refresh dashboard. Please try again.',
      life: 3000
    });
  }
}

async function markUploadAsComplete() {
  const loading = await window.showLoading();
  try {
    const res = await app.postApi(
      "edoor.channel_managers.utils.mark_channel_data_upload_as_complete",
      {
        property: window.property_name
      },
      "",
      false
    );
    
    if (res && res.success) {
      toast.add({
        severity: 'success',
        summary: 'Upload Complete',
        detail: 'All data has been successfully uploaded to Channel Manager',
        life: 3000
      });
    }
  } catch (error) {
    console.error('Error marking upload as complete:', error);
    toast.add({
      severity: 'error',
      summary: 'Upload Error',
      detail: 'There was an error completing the upload process',
      life: 3000
    });
  } finally {
    loading.close();
  }
}

onMounted(async () => {
  await markUploadAsComplete();
});
</script>

<style scoped>
.success-page {
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  min-height: 100vh;
}

.success-card :deep(.p-card) {
  border-radius: 1.5rem;
  overflow: hidden;
  backdrop-filter: blur(2px);
}

.success-card :deep(.p-card-content) {
  padding: 0;
}

/* Success Icon Animation */
.success-icon-container {
  position: relative;
}

.animated-circle {
  width: 90px;
  height: 90px;
  background: linear-gradient(145deg, #22c55e, #16a34a);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 25px -5px rgba(34, 197, 94, 0.3);
  animation: pulse 2s infinite;
}

.success-icon {
  font-size: 3.5rem;
  color: white;
  animation: checkmark 0.6s cubic-bezier(0.65, 0, 0.35, 1) forwards;
  transform: scale(0);
}

@keyframes pulse {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.4);
  }
  70% {
    box-shadow: 0 0 0 15px rgba(34, 197, 94, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
  }
}

@keyframes checkmark {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.2);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* Feature Cards */
.feature-card {
  background: white;
  transition: all 0.3s ease;
  cursor: default;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  transition: transform 0.2s ease;
}

.feature-card:hover .feature-icon {
  transform: scale(1.05);
}

/* Success Message Box */
.success-message-box {
  background: linear-gradient(120deg, #eff6ff 0%, #dbeafe 100%);
  border-left: 4px solid #3b82f6;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .success-card {
    margin: 0;
  }
  
  .animated-circle {
    width: 70px;
    height: 70px;
  }
  
  .success-icon {
    font-size: 2.5rem;
  }
  
  .feature-card {
    padding: 0.75rem;
  }
}
</style>