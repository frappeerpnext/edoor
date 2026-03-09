<template>
    <div><span>{{$t('Res. Date')}}:</span> <span class="font-semibold">{{ moment(data?.reservation_date).format("DD-MM-YYYY") }}</span></div>
    <div><span>{{$t('From')}}:</span> <span class="font-semibold">{{ moment(data?.arrival_date).format("DD-MM-YYYY") }} &#8594; {{ moment(data?.departure_date).format("DD-MM-YYYY") }}</span></div>
    <!-- {{ data }} -->
    <div class="flex gap-2">
        <template v-for="(m, index) in stayInfoItem" :key="index">
            <tippy :content="$t(m.title)" placement="bottom">
                <div class="flex gap-2 border-round py-1 px-2 align-items-center" style="width:fit-content"> 
                    <div>{{ m.field }}</div>
                    <div><ComIcon :icon="m.icon" style="width:16px"/></div>
                </div> 
            </tippy>
        </template>
    </div>
</template>
<script setup> 
import { inject } from '@/plugin';
const moment = inject("$moment")
const props = defineProps({
    data:Object
})

// console.log(props.data.room_nights)

const stayInfoItem = [
    {
        field: props.data.room_nights,
        icon: 'moonIcon',
        title: 'Nights'
    },
    {
        field: props.data.adult,
        icon: 'adultIcon',
        title: 'Adult(s)'
    },
    {
        field: props.data.child,
        icon: 'childIcon',
        title: 'Child(s)'
    },
]
</script>