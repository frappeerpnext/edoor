<template>
    <img v-if="icon == 'edoor'" :style="{'height' : height}" :class="class" :src="iconEdoorReservation"/>
    <img v-else-if="icon == 'frontdesk'" :style="{'height' : height}" :class="class" :src="frontdesk"/>
    <img v-else-if="icon == 'reservation'" :style="{'height' : height}" :class="class" :src="reservation"/>
    <img v-else-if="icon == 'iconBed'" :style="{'height' : height}" :class="class" :src="iconBed"/>
    <img v-else-if="icon == 'checkin'" :style="{'height' : height}" :class="class" :src="BtnCheckinIcon"/>
    <img v-else-if="icon == 'checkout'" :style="{'height' : height}" :class="class" :src="BtnCheckoutIcon"/>
    <img v-else-if="icon == 'BirthdayIcon'" :style="{'height' : height}" :class="class" :src="BirthdayIcon"/>
    <img v-else-if="icon == 'ViewDetailIcon'" :style="{'height' : height}" :class="class" :src="ViewDetailIcon"/>
    <img v-else-if="icon == 'iconOpenBrower'" :style="{'height' : height}" :class="class" :src="theme == 'estc' ? iconOpenBrower : iconOpenBrowerMicro"/>
    <img v-else-if="icon == 'iconNote'" :style="{'height' : height}" :class="class" :src="iconNote"/>
    <img v-else-if="icon == 'iconNoteBlue'" :style="{'height' : height}" :class="class" :src="theme == 'estc' ? iconNoteBlue : iconNoteMicro"/>
    <img v-else-if="icon == 'iconCrown'" :style="{'height' : height}" :class="class" :src="iconCrown"/>
    <img v-else-if="icon == 'iconCrownBlack'" :style="{'height' : height}" :class="class" :src="iconCrownBlack"/>
    <img v-else-if="icon == 'iconFIT'" :style="{'height' : height}" :class="class" :src="iconFIT"/>
    <img v-else-if="icon == 'iconUserGroup'" :style="{'height' : height}" :class="class" :src="iconUserGroup"/>
    <img v-else-if="icon == 'iconBedPurple'" :style="{'height' : height}" :class="class" :src="iconBedPurple"/>
    <img v-else-if="icon == 'iconBedWhite'" :style="{'height' : height}" :class="class" :src="iconBedWhite"/>
    <img v-else-if="icon == 'pushPin'" :style="{'height' : height}" :class="class" :src="pushPin"/>
    <img v-else-if="icon == 'pushPined'" :style="{'height' : height}" :class="class" :src="pushPined"/>
    <img v-else-if="icon == 'iconNoteWhite'" :style="{'height' : height}" :class="class" :src="iconNoteWhite"/>
    <img v-else-if="icon == 'userProfile'" :style="{'height' : height}" :class="class" :src="userProfile"/>
    <img v-else-if="icon == 'userGroupWhite'" :style="{'height' : height}" :class="class" :src="userGroupWhite"/>
    <img v-else-if="icon == 'userFitWhite'" :style="{'height' : height}" :class="class" :src="userFitWhite"/>
    <img v-else-if="icon == 'userGif'" :style="{'height' : height}" :class="class" :src="userGif"/>
    <img v-else-if="icon == 'NotDisturb'" :style="{'height' : height}" :class="class" :src="NotDisturb"/>
    <img v-else-if="icon == 'City'" :style="{'height' : height}" :class="class" :src="City"/>
    <img v-else-if="icon == 'checkin-black'" :style="{'height' : height}" :class="class" :src="BtnCheckinIconBlack"/>
    <img v-else-if="icon == 'checkoutBlack'" :style="{'height' : height}" :class="class" :src="BtnCheckoutIconBlack"/>
    <img v-else-if="icon == 'iconEditGrid'" :style="{'height' : height}" :class="class" :src="theme == 'estc' ? iconEditGrid : iconEditGridMicro"/>
    <img v-else-if="icon == 'iconAddNewGuest'" :style="{'height' : height}" :class="class" :src="iconAddNewGuest"/>
    <!-- default Icon -->
    <img v-else-if="icon == 'iconGeneralList'" :style="{'height' : height}" :class="class" :src="iconGeneralList"/>
    <img v-else-if="icon == 'BilltoMasterRoom'" :style="{'height' : height}" :class="class" :src="BilltoMasterRoom"/>
    <img v-else-if="icon == 'BilltoMasterRoomWhite'" :style="{'height' : height}" :class="class" :src="BilltoMasterRoomWhite"/>
    <img v-else-if="icon == 'IconBillToCompany'" :style="{'height' : height}" :class="class" :src="IconBillToCompany"/>
    <img v-else-if="icon == 'IconBillToCompanywhite'" :style="{'height' : height}" :class="class" :src="IconBillToCompanywhite"/>
    <img v-else-if="icon == 'IconBillToGuest'" :style="{'height' : height}" :class="class" :src="IconBillToGuest"/>
    <img v-else-if="icon == 'iconWeekCalendar'" :style="{'height' : height}" :class="class" :src="iconWeekCalendar"/>
    <img v-else-if="icon == 'broom'" :style="{'height' : height}" :class="class" :src="iconBroom"/>
    <img v-else-if="icon == 'icon14Day'" :style="{'height' : height}" :class="class" :src="icon14Day"/>
    <img v-else-if="icon == 'iconMonth'" :style="{'height' : height}" :class="class" :src="iconMonth"/>
    <img v-else-if="icon == 'roomRate'" :style="{'height' : height}" :class="class" :src="roomRate"/>
    <img v-else-if="icon == 'iconChangeStay'" :style="{'height' : height}" :class="class" :src="iconChangeStay"/>
    <img v-else-if="icon == 'iconSplit'" :style="{'height' : height}" :class="class" :src="iconSplit"/>
    <img v-else-if="icon == 'iconConflictRoom'" :style="{'height' : height}" :class="class" :src="iconConflictRoom"/>
    <img v-else-if="icon == 'iconCamera'" :style="{'height' : height}" :class="class" :src="iconCamera"/>
    <img v-else-if="icon == 'iconMoveStay'" :style="{'height' : height}" :class="class" :src="iconMoveStay"/>
    <img v-else-if="icon == 'iconWalkIn'" :style="{'height' : height}" :class="class" :src="iconWalkIn"/>
    <img v-else-if="icon == 'iconPackage'" :style="{'height' : height}" :class="class" :src="iconPackage"/>
    <img v-else-if="icon == 'iconArrival'" :style="{'height' : height}" :class="class" :src="iconArrival"/>
    <img v-else-if="icon == 'icondeparture'" :style="{'height' : height}" :class="class" :src="icondeparture"/>
    <img v-else-if="icon == 'iconstayover'" :style="{'height' : height}" :class="class" :src="iconstayover"/>
    <img v-else-if="icon == 'RoomBlockIcon'" :style="{'height' : height}" :class="class" :src="RoomBlockIcon"/>


    
</template>
<script setup>
const theme =window.theme
const props = defineProps({
    icon: {
        type: String,
        default: ''
    },
    class: {
        type: String,
        default: ''
    },
    height: String
})
import icondeparture from '@/assets/svg/departure-icon-white.svg'
import iconArrival from '@/assets/svg/arrival-icon-white.svg'
import iconstayover from '@/assets/svg/stayover-icon-white.svg'
import iconEdoorReservation from '@/assets/svg/icon-reservation.svg'
import reservation from '@/assets/svg/icon-reservation.svg'
import frontdesk from '@/assets/svg/icon-frontdesk.svg'
import iconBroom from '@/assets/svg/icon-broom-white.svg'
import iconBed from '@/assets/svg/icon-bed.svg'
import BtnCheckinIcon from '@/assets/svg/icon-check-in.svg'
import BtnCheckinIconBlack from '@/assets/svg/icon-check-in-black.svg'
import BtnCheckoutIcon from '@/assets/svg/icon-check-out.svg'
import BtnCheckoutIconBlack from '@/assets/svg/icon-check-out-black.svg'
import BirthdayIcon from '@/assets/svg/birthday-icon.svg'
import ViewDetailIcon from '@/assets/svg/change-room-icon.svg'
import iconOpenBrower from '@/assets/svg/icon-open-brower.svg'
import iconOpenBrowerMicro from '@/assets/svg/open-brower-new.svg'
import iconNote from '@/assets/svg/icon-note-paper-pen.svg'
import iconNoteMicro from '@/assets/svg/noted-macro-icon.svg'
import iconNoteBlue from '@/assets/svg/icon-note-paper-pen-blue.svg'
import iconCrown from '@/assets/svg/icon-crown.svg'
import iconCrownBlack from '@/assets/svg/icon-crown-black.svg'
import iconFIT from '@/assets/svg/user-icon-profile.svg'
import iconUserGroup from '@/assets/svg/icon-user-group.svg'
import pushPin from '@/assets/svg/push_pin.svg'
import pushPined from '@/assets/svg/push_pined.svg'
import iconBedPurple from '../assets/svg/icon-room-purple.svg'
import iconBedWhite from '../assets/svg/bed-icon-white.svg'
import iconNoteWhite from '@/assets/svg/icon-note-paper-white.svg'
import userProfile from '@/assets/svg/user-icon-profile.svg'
import userGroupWhite from '@/assets/svg/icon-user-group-white.svg'
import userFitWhite from '@/assets/svg/icon-user-fit.svg'
import userGif from '@/assets/svg/icon-user-group.svg'
import NotDisturb from '@/assets/svg/icon-do-not-disturb.svg'
import City from '@/assets/svg/icon-change-property.svg'
import iconGeneralList from '@/assets/svg/icon-general-list.svg'
import iconEditGrid from '@/assets/svg/icon-edit-grid.svg'
import iconEditGridMicro from '@/assets/svg/edit-grid-icon-macro.svg'
import iconAddNewGuest from '@/assets/svg/icon-add-guest-white.svg'
import BilltoMasterRoom from '@/assets/svg/icon-bill-to-master-room.svg'
import IconBillToCompany from '@/assets/svg/icon-bill-to-company.svg'
import IconBillToGuest from '@/assets/svg/icon-bill-to-guest.svg'
import iconWeekCalendar from '@/assets/svg/icon-week-calendar.svg'
import icon14Day from '@/assets/svg/icon-14day.svg'
import iconMonth from '@/assets/svg/icon-month-calendar.svg'
import roomRate from '@/assets/svg/icon-roomrate.svg'
import iconChangeStay from '@/assets/svg/icon-changestay.svg'
import BilltoMasterRoomWhite from '@/assets/svg/icon-BilltoMasterRoomWhite.svg'
import IconBillToCompanywhite from '@/assets/svg/IconBillToCompanywhite.svg'
import iconSplit from '@/assets/svg/icon-split-blue.svg'
import iconConflictRoom from '@/assets/svg/icon-conflict-room.svg'
import iconCamera from '@/assets/svg/icon-camera.svg'
import iconMoveStay from '@/assets/svg/icon-move_stay.svg'
import iconWalkIn from '@/assets/svg/walk-in-icon.svg'
import iconPackage from '@/assets/svg/package-icon.svg'
import RoomBlockIcon from '@/assets/svg/RoomBlockIcon.svg'


</script>
 