<template>
    <div>
        <div class="changed">
            <h2 class="h-title mb-3">Child Changed</h2>
            <table class="w-full" border="1">
                <thead>
                    <tr>
                        <th>Property</th>
                        <th>Row</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in data.row_changed" :key="index">
                        <td>{{item.property}}</td>
                        <td>
                            <table class="w-full" border="1">
                                <thead>
                                    <tr>
                                        <th>Property</th>
                                        <th>Original Value</th>
                                        <th>New Value</th>
                                    </tr>
                                </thead>
                                <tbody> 
                                    <tr v-for="(c, index) in item.rows" :key="index">
                                        <td>{{ c.feilds[0][0] }}</td>
                                        <td style="background:var(--red-100);"><div v-html="c.feilds[0][1]"></div></td>
                                        <td style="background:var(--green-100);"><div v-html="c.feilds[0][2]"></div></td>
                                    </tr>
                                </tbody>
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
    data:Object
})
</script>
<style scoped>
    .h-title{
        font-weight: 600;
        font-size: 1.125rem;
    }
    table {
        border-collapse: collapse;
        border: 1px solid rgba(204, 204, 204, 0.3);
        width: 100%;
    }
    th, td {
        padding: 10px;
        text-align: left;
        border-bottom: 1px solid rgba(204, 204, 204, 0.3);
    }
    th {
        border-top: 1px solid rgba(204, 204, 204, 0.3);
        border-bottom: 2px solid rgba(204, 204, 204, 0.3);
        border-left: 1px solid rgba(204, 204, 204, 0.3);
        font-weight: normal;
    }
    td{
        border-top: 1px solid rgba(204, 204, 204, 0.3);
        border-bottom: 1px solid rgba(204, 204, 204, 0.3);
        border-left: 1px solid rgba(204, 204, 204, 0.3);
        vertical-align: baseline;
    }
    tr:last-of-type td {
        border-bottom: none;
    }
</style>