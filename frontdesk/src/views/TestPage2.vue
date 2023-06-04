<template>
    <ComIcon icon="frontdesk"/>
    <div class="card flex justify-content-center">
        <Button type="button" icon="pi pi-image" label="Image" @click="toggle" />
   <br/>
    <Button type="button" icon="pi pi-image" label="Image" @click="toggle($event, 12)" />
        <OverlayPanel ref="op">
xxxx
        </OverlayPanel>
    </div>
</template>

<script setup>
import { ref, useRoute } from "@/plugin";

const route = useRoute()
alert(route.name)


const op = ref();
const toggle = ($event, num) => {
    alert(num)
    op.value.toggle($event);
}
</script>