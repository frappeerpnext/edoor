<template>
    <div>
        <div class="at-update-row">
            <table class="w-full">
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
                        <td class="nth-2_td"> 
                            <table class="w-full" :style="type == 'added' ? 'background:var(--green-100)' : 'background:var(--red-100)'" style="border:0">
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
<style scoped>
.at-update-row table tbody tr td.nth-2_td{
    padding: 0;
}
td.nth-2_td table tr:first-child td{
    border-top: none;
}
td.nth-2_td table tr td:first-child{
    border-left: 0;
}
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