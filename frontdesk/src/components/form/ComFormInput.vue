<template>
    
    <div v-if="field.fieldtype=='Check'">
        <div class="flex item-center gap-2">
            <label class="cursor-pointer" :for="field.fieldname">
               {{ field.label }} 
            </label>
             
        <Checkbox :inputId="field.fieldname"
                                 
                                    v-model="model[field.fieldname]" :binary="true" :trueValue="1"
                                     :falseValue="0" />
        </div>
    </div>
    <div v-else-if="field.fieldtype=='Small Text'">
        {{ field.label }}
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