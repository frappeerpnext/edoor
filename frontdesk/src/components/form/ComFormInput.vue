<template>
    {{ field.fieldtype }}
    <div v-if="field.fieldtype=='Check'">
        <Checkbox
                                 
                                    v-model="model[field.fieldname]" :binary="true" :trueValue="1"
                                     :falseValue="0" />
    </div>
    
    <div v-else-if="field.fieldtype=='Small Text'">
        <Textarea v-model="model[field.fieldname]" rows="5" :placeholder="$t(field.label)" cols="30"
        class="w-full border-round-xl" />
    </div>

</template>
<script setup>
const props = defineProps({
    field:Object,
    model:Object
})
</script>