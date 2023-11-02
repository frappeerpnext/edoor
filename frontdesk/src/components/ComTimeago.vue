<template >
 
    <Timeago :datetime="date" long  v-tippy="date_string">
        <template #default="{ secondsElapsed, timeago }">
            {{ secondsElapsed <= 2700000 ? timeago : date_string }}
        </template>
    </Timeago>
</template>
<script setup>

import moment from "@/utils/moment";
import { Timeago } from 'vue2-timeago'
import { ref } from 'vue'

const props = defineProps(
    {
        date: Date
    }
)
let date_string = ref("")

if (props.date.toString().length<=10){
    date_string = moment(props.date).format('DD-MM-YYYY')
}else {
    date_string = moment(props.date).format("DD-MM-yy h:mm:ss A")
}






</script>