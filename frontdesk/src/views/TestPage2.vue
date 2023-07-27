<template>
    <div>
        <TestPage :list="msg">
            <template v-slot="slotProps">
                <div class="text-red-400">{{ slotProps.data }}</div>
            </template>
        </TestPage>
    </div>
</template>
<script setup> 
import {ref} from 'vue'
import TestPage from './TestPage.vue'
var msg = ref(['A','B','C'])

</script>
<style scoped>

</style>