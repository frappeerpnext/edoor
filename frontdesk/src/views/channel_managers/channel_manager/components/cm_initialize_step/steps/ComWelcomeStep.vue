<template>
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
<script setup> 

</script>
<style scoped>

.info {
  background: #eef2ff;
  padding: 18px;
  border-radius: 14px;
}
</style>