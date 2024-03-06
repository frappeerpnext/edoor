<template>
    <div class="mx-1 my-4">
        <div class="grid">
            <div class="col-6" v-for="(d, index) in data" :key="index">
                <span class="px-3 me-2" :style="{ background: d.color }"></span>{{ $t(d.name) }}
            </div>
        </div>
    </div>
</template>
<script setup>
import { ref,getDocList } from '@/plugin';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const data = ref([])
    getDocList('Reservation Status', {
        fields: ['name', 'color'],
        orderBy: {
            field: 'sort_order',
            order: 'asc',
        },
    })
    .then((docs) => {
        data.value = docs
    })
</script>