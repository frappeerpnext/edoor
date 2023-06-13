<template>
    <img v-if="icon == 'edoor'" :class="class" :src="iconEdoorReservation"/>
    <img v-else-if="icon == 'frontdesk'" :class="class" :src="frontdesk"/>
    <img v-else-if="icon == 'reservation'" :class="class" :src="reservation"/>
    <img v-else-if="icon == 'iconBed'" :class="class" :src="iconBed"/>
    <img v-else-if="icon == 'checkin'" :class="class" :src="BtnCheckinIcon"/>
    <img v-else-if="icon == 'checkout'" :class="class" :src="BtnCheckoutIcon"/>
    <img v-else-if="icon == 'BirthdayIcon'" :class="class" :src="BirthdayIcon"/>
    <img v-else-if="icon == 'ViewDetailIcon'" :class="class" :src="ViewDetailIcon"/>
    <img v-else-if="icon == 'iconOpenBrower'" :class="class" :src="iconOpenBrower"/>
    <img v-else-if="icon == 'iconNote'" :class="class" :src="iconNote"/>
    <img v-else-if="icon == 'iconNoteBlue'" :class="class" :src="iconNoteBlue"/>
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
import BirthdayIcon from '@/assets/svg/birthday-icon.svg'
import ViewDetailIcon from '@/assets/svg/change-room-icon.svg'
import iconOpenBrower from '@/assets/svg/icon-open-brower.svg'
import iconNote from '@/assets/svg/icon-note-paper-pen.svg'
import iconNoteBlue from '@/assets/svg/icon-note-paper-pen-blue.svg'

</script>
 