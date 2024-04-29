<template>
    {{ rs.reservationStay?.inclusion_items || "No Package Found" }}
</template>
<script setup>
import {ref,inject} from "@/plugin"
const rs =inject("$reservation_stay")

</script>