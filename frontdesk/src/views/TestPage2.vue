<template>
    <div>
        <TestPage :list="msg" :test="test">
            <template v-slot="slotProps">
                <div class="text-red-400">{{ slotProps.data }}</div>
            </template>
        </TestPage>
        <Button type="button" @click="onClick">click</Button>
    </div>
</template>
<script setup> 
import {ref} from 'vue'
import TestPage from './TestPage.vue'
var msg = ref(['A','B','C'])
const test = ref('v')
function onClick(){
    test.value = 'ww'
}
</script>
<style scoped>

</style>