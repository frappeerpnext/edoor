<template>
    <div class="card">
        <Fieldset :legend="nameLegend" class="px-2">
            <div class="inner-fs">
                <slot></slot>
            </div>
        </Fieldset>
    </div>
</template>
<script setup>
const props = defineProps({
    nameLegend: String,
})
</script>
<style></style>