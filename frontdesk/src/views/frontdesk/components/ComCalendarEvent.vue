<template>

    <div class="group relative h-full p-1" :class="event.extendedProps.type + ' ' + (event.extendedProps.reservation_stay || '')" style="height: 36px ">
        <div :style="event.extendedProps.group_color ? 'padding-right:16px' : ''" :class="(event.extendedProps.type=='room_type_event' || event.extendedProps.type=='property_summary') ? 'flex justify-content-center' : 'flex'">
            <span class="ml-1 display-block stay-identify-position border-1" :style="{backgroundColor:event.extendedProps.group_color}" v-if="event.extendedProps.group_color">
                <!-- GIT/FIT Color -->
            </span>
            <span class="wrp-statu-icon">
                <span v-if="event.extendedProps.is_master" class="stay-bar-status mr-1">
                    <img :src="iconCrown" style="height: 12px"/>
                </span>
                <span v-if="event.extendedProps.reservation_type=='GIT'" class="stay-bar-status mr-1">
                    <img :src="iconUserGroup" style="height: 12px"/>
                </span>
                <span v-if="event.extendedProps.stay_rooms && event.extendedProps.stay_rooms.split(',').length > 1" class="stay-bar-status mr-1">
                    <img :src="iconSplitRoom" style="height: 12px"/>
                </span>
            </span>
            
            <div class="guest-title">
                <template v-if="event.extendedProps.type=='room_type_event'">
                    <span :style="event.extendedProps.room_available < 0 ? 'color:#FFF' : 'color:#000'">{{event.extendedProps.room_available}}</span>
                    <span :style="event.extendedProps.room_available < 0 ? 'color:#ffb0b0' : 'color:#dee2e6'"> | </span>
                    <span :style="event.extendedProps.room_available < 0 ? 'color:#FFF' : 'color:#000'">{{event.extendedProps.unassign_room}}</span>
                </template>
                <template v-else-if="event.extendedProps.type=='property_summary'">
                    <span class="text-white">{{event.extendedProps.room_available}}</span>
                    <span style="color:rgba(0, 0, 0, 0.15 )"> | </span>
                    <span class="text-white">{{event.extendedProps.unassign_room}}</span>
                </template>
                <template v-else>
                    {{event.title}} 
                    
                    <span v-if="show_additional_guest_name_in_room_chart_calendar==1 && event.extendedProps.additional_guest_name">
                        / {{ event.extendedProps.additional_guest_name }}
                    </span>
                </template>
            </div>
        </div>
    </div>
</template>
<script setup>
import iconCrown from '@/assets/svg/icon-crown.svg'
import iconUserGroup from '@/assets/svg/icon-user-group.svg'
import iconSplitRoom from '@/assets/svg/icon-split-blue.svg'

const props = defineProps({
    event:Object
})

const show_additional_guest_name_in_room_chart_calendar = window.setting.show_additional_guest_name_in_room_chart_calendar
</script>