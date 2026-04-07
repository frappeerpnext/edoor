<template>
    <com-confirm-message 
        label="Verify Availability" 
        text="Please review and verify the availability details below before proceeding."/>
    <div class="availability-wrapper">
    <div class="availability-title">{{ $t('AVAILABILITY') }}</div>
        <com-availability 
            v-for="(roomType, index) in roomTypeInfo" 
            :key="index"
            :room-type-name="roomType.roomTypeName"
            :room-type-code="roomType.roomTypeCode"
            :total-room="roomType.totalRoom"
            :day-cover="roomType.dayCover"
            :is-room-mapping="roomType.isRoomMapping"
        />
    </div>
</template>
<script setup>
import ComAvailability from '@/views/channel_managers/channel_manager/components/ComAvailability.vue';

const roomTypeInfo = [
    {
        roomTypeName: 'Standard STD',
        roomTypeCode: '56456',
        totalRoom: 5,
        dayCover: 365,
        isRoomMapping: true
    },
    {
        roomTypeName: 'Deluxe DLX',
        roomTypeCode: '31565',
        totalRoom: 3,
        dayCover: 200,
        isRoomMapping: false
    },
    {
        roomTypeName: 'Suite STE',
        roomTypeCode: '78985',
        totalRoom: 2,
        dayCover: 100,
        isRoomMapping: true
    }
]
</script>
<style scoped>
.availability-wrapper {
  margin-top: 20px;
  /* padding: 20px; */
  border-radius: 16px;
  /* background: #ffffff; */
  /* box-shadow: 0 10px 30px rgba(0,0,0,0.05); */
  font-family: 'Segoe UI', sans-serif;
}

.availability-title {
  font-size: 14px;
  font-weight: 600;
  color: #7b8190;
  margin-bottom: 15px;
  letter-spacing: 0.5px;
}


</style>