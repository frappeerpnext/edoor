<template>
	<main-layout/>
    <Toast/>
</template>


<script>
import MainLayout from './components/layout/MainLayout.vue';

export default {
    inject: ["$auth"],
    components: { MainLayout }
};
</script>
 <style>
    .p-menu {
        width: auto;
    }
</style>
