<template>
    <div class="flex gap-2 align-items-center w-100">
        <div>
            <Avatar v-if="data?.photo" :image="data?.photo" class="mr-2 border-circle" size="large" shape="circle" />
            <div v-else class="mr-3 bg-gray-300 border-circle p-1 border-2">
                <ComIcon  icon="userProfile" ></ComIcon>
            </div>
        </div>
        <div>
            <div class="flex gap-2">
                <div class="font-semibold">{{ data?.guest_name }}</div>
                <div class="flex gap-2">
                    <div @click="onOpenLink('view_reservation_stay_detail', data?.name)" class="link_line_action overflow-hidden" style="width: fit-content;">{{ data?.name }}</div> 
                    <div>|</div>
                    <div @click="onOpenLink('view_reservation_detail', data?.reservation)" class="link_line_action overflow-hidden" style="width: fit-content;">{{ data?.reservation }}</div>
                </div>
            </div>
            <div class="text-500">{{ data?.guest_email }} <span v-if="data?.guest_phone_number">| {{ data?.guest_phone_number }}</span></div>
            
            <div class="font-italic text-500" v-if="data?.reference_number">
                Ref. No: {{ data?.reference_number }}
            </div>
            <div class="flex gap-2">
                <div class="text-white px-2" v-if="data?.reservation_color_code" :style="{background:data?.reservation_color,width:'fit-content',borderRadius:'50px'}">{{ data?.reservation_color_code }}</div>
            </div>
        </div>
        
    </div>
</template>
<script setup>
const props = defineProps({
    data:Object
})

function onOpenLink(action, name) {
    window.postMessage(action + '|' + name, '*')
}
</script>