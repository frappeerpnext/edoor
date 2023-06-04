<template>
    <img v-if="icon == 'edoor'" :class="class" :src="iconEdoorReservation"/>
    <img v-else-if="icon == 'frontdesk'" :class="class" :src="frontdesk"/>
    <img v-else-if="icon == 'reservation'" :class="class" :src="reservation"/>
    <img v-else-if="icon == 'iconBed'" :class="class" :src="iconBed"/>
    <img v-else-if="icon == 'checkin'" :class="class" :src="BtnCheckinIcon"/>
    <img v-else-if="icon == 'checkout'" :class="class" :src="BtnCheckoutIcon"/>
</template>
<script setup>
const props = defineProps({
    icon: {
        type: String,
        default: ''
    },
    class: {
        type: String,
        default: ''
    },
})
import iconEdoorReservation from '../assets/svg/icon-reservation.svg'
import reservation from '../assets/svg/icon-reservation.svg'
import frontdesk from '../assets/svg/icon-frontdesk.svg'
import iconBed from '../assets/svg/icon-bed.svg'
import BtnCheckinIcon from '@/assets/svg/icon-check-in.svg'
import BtnCheckoutIcon from '@/assets/svg/icon-check-out.svg'
</script>
 