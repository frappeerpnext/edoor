<template>
  <div class="wrapper">
    <div class="card">
      <!-- Header -->
      <div class="header">
        <div>
          <div class="text-4xl">{{$t('Initial Data Upload')}}</div>
          <p>{{$t('Channel Manager Integration')}}</p>
        </div>
        <span>{{$t('STEP')}} {{ activeIndex }} {{$t('OF')}} {{steps.length}}</span>
        
      </div>
      <!-- Stepper -->
      <div class="stepper">
        <div class="line"></div>
          <ComStepper v-for="step in steps" 
            :key="step.index"
            :title="step.title"
            :index="step.index"
            :activeIndex="activeIndex"
          />
      </div>  
      <template v-if="activeIndex === 1">
        <div class="info">
          <!-- <div class="info-icon">💡</div> -->
          <div class="text-center"> 
            <p class="font-semibold">{{$t('Welcome to the Channel Manager Integration Setup Wizard!')}}</p>
            <p class="mt-1">{{$t('This wizard will guide you through the process of uploading your initial data to the channel manager.')}}</p>
            <p class="mt-1">{{$t('Please click "Next" to proceed.')}}</p>
            <br />
            <div class="flex justify-center">
              <ComIcon icon="iconLightBulb" height="125px" />
            </div>
          </div>
        </div>
      </template>
      <com-data-overview v-if="activeIndex === 2" />
      <com-availability-upload v-if="activeIndex === 3" />
      <!-- Footer -->
      <div class="footer flex gap-2">
        <Button @click="goToPrevStep" class="btn-back" :disabled="activeIndex === 1">
            &#8592; {{ $t('Back') }} 
        </Button>
        <Button @click="goToNextStep" class="btn-next" :disabled="activeIndex === steps.length">
            {{ $t('Next') }} &#8594;
        </Button>
      </div>
      

    </div>
  </div>
</template>
<script setup>
import { ref } from '@/plugin'
import ComStepper from './ComStepper.vue';
import ComDataOverview from './ComDataOverview.vue';
import ComAvailabilityUpload from './ComAvailabilityUpload.vue';

const activeIndex = ref(1);
const steps = [
    { index: 1, title: 'WELCOME' },
    { index: 2, title: 'CREDENTIALS' },
    { index: 3, title: 'AVAILABILITY' },
    { index: 4, title: 'PRICES' },
    { index: 5, title: 'RESTRICTIONS' },
    { index: 6, title: 'REVIEW' }
];

function goToNextStep() {
    if (activeIndex.value < steps.length) {
        activeIndex.value++;
    }
}

function goToPrevStep() {
    if (activeIndex.value > 1) {
        activeIndex.value--;
    }
}
</script>
<style scoped>
.stepper {
    position: relative;
    display: flex;
    justify-content: space-between;
    margin: 30px 0;
}

.line {
    position: absolute;
    top: 18px;
    left: 0;
    right: 0;
    height: 2px;
    background: #e5e7eb;
    z-index: 0;
}


.wrapper {
  padding: 40px;
  display: flex;
  justify-content: center;
}

.card {
  width: 900px;
  background: #fff;
  border-radius: 20px;
  padding: 30px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.06);
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
}

.header h2 {
  margin: 0;
}

.header p {
  margin: 5px 0 0;
  color: #6b7280;
}

.header span {
  font-size: 12px;
  color: #9ca3af;
}

/* Info */
.info {
  /* display: flex; */
  gap: 15px;
  background: #eef2ff;
  padding: 18px;
  border-radius: 14px;
}

.info-icon {
  width: 36px;
  height: 36px;
  background: #6366f1;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Footer */
.footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}

button {
  /* background: linear-gradient(135deg, #6366f1, #4f46e5); */
  color: white;
  border: none;
  padding: 12px 26px;
  /* border-radius: 12px; */
  cursor: pointer;
  font-weight: 500;
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
}

button:hover {
  opacity: 0.9;
}
</style>