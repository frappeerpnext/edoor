<template>
    <div>
        <div v-if="isLoading" class="popover-loading">Loading...</div>
        <div v-else>
            <!-- {{ data }} -->
            {{ date }} =>{{ rate_type }} {{ room_type_id }}  
            {{ data }}
        </div>
    </div>
</template>
<script setup>
import { onMounted, ref } from 'vue';
const props = defineProps({
    date: Object,
    rate_type: String,
    room_type_id: String
})
const data = ref()
const isLoading = ref(true)

async function getRoomRateDetail() {
    isLoading.value = true
    const res = await app.getApi("rate_plan.get_room_rate_detail", {
        property: window.property_name,
        rate_type: props.rate_type,
        date: props.date
    })
    if (res.data) {
        data.value = res.data
    }
    isLoading.value = false;
}
onMounted(async () => {
    setTimeout(async () => {
        await getRoomRateDetail();
    }, 1000);

})
</script>