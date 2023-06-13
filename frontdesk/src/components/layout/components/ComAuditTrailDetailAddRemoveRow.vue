<template>
    <div>
        {{ data }}
        <div class="at-update-row">
            <table>
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Rows {{ type == 'added' ? 'Add' : 'Remove' }}</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(i, index) in data" :key="index">
                        <td>
                            {{ i.property }}
                        </td>
                        <td> 
                            <table  :class="type == 'added' ? 'bg-green-400' : 'bg-red-400'">
                                <tr v-for="(i, index) in i.value" :key="index">
                                    <td>{{ i.property }}</td>
                                    <td>{{ i.value }}</td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
    const props = defineProps({
        type: 'added',  // added or removed
        data: Array
    })
</script>
<style lang="">
    
</style>