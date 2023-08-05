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
    <img v-else-if="icon == 'iconCrown'" :class="class" :src="iconCrown"/>
    <img v-else-if="icon == 'iconFIT'" :class="class" :src="iconFIT"/>
    <img v-else-if="icon == 'iconUserGroup'" :class="class" :src="iconUserGroup"/>
    <img v-else-if="icon == 'iconBedPurple'" :class="class" :src="iconBedPurple"/>
    <img v-else-if="icon == 'pushPin'" :class="class" :src="pushPin"/>
    <img v-else-if="icon == 'pushPined'" :class="class" :src="pushPined"/>
    <img v-else-if="icon == 'iconNoteWhite'" :class="class" :src="iconNoteWhite"/>
    <img v-else-if="icon == 'userProfile'" :class="class" :src="userProfile"/>
    <img v-else-if="icon == 'userGroupWhite'" :class="class" :src="userGroupWhite"/>
    <img v-else-if="icon == 'userFitWhite'" :class="class" :src="userFitWhite"/>
    <img v-else-if="icon == 'userGif'" :class="class" :src="userGif"/>
    <img v-else-if="icon == 'NotDisturb'" :class="class" :src="NotDisturb"/>
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
import iconCrown from '@/assets/svg/icon-crown.svg'
import iconFIT from '@/assets/svg/user-icon-profile.svg'
import iconUserGroup from '@/assets/svg/icon-user-group.svg'
import pushPin from '@/assets/svg/push_pin.svg'
import pushPined from '@/assets/svg/push_pined.svg'
import iconBedPurple from '../assets/svg/icon-room-purple.svg'
import iconNoteWhite from '@/assets/svg/icon-note-paper-white.svg'
import userProfile from '@/assets/svg/user-icon-profile.svg'
import userGroupWhite from '@/assets/svg/icon-user-group-white.svg'
import userFitWhite from '@/assets/svg/icon-user-fit.svg'
import userGif from '@/assets/svg/icon-user-group.svg'
import NotDisturb from '@/assets/svg/icon-do-not-disturb.svg'


</script>
 