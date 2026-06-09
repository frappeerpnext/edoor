<template> 
    <div class="resource-item">
        <div class="value">{{value || 0}}</div>
        <div class="label">{{ $t(label) || $t("No Label") }}</div>
    </div>
</template>
<script setup>
const props = defineProps({
    label: String,
    value: Number
})
</script>
<style scoped>
.resource-item{
    position:relative;
    overflow:hidden;
    border-radius:26px;
    padding:15px 20px;
    color:white;
    background:linear-gradient(135deg,#4f8cff,#2563eb);
    box-shadow:
        0 12px 24px rgba(37,99,235,0.25),
        inset 0 1px 1px rgba(255,255,255,0.25);
    transition:0.3s ease;
    cursor:pointer;

    /* ADD THESE */
    min-height:100px;
    display:flex;
    flex-direction:column;
    justify-content:space-between;
}

.resource-item:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow:
        0 18px 30px rgba(37, 99, 235, 0.35),
        inset 0 1px 1px rgba(255, 255, 255, 0.25);
}

.resource-item::before {
    content: '';
    position: absolute;
    width: 140px;
    height: 140px;
    background: rgba(255, 255, 255, 0.12);
    border-radius: 50%;
    top: -60px;
    right: -40px;
}

.resource-item::after {
    content: '';
    position: absolute;
    width: 80px;
    height: 80px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 50%;
    bottom: -30px;
    left: -20px;
}

.value {
    font-size: 52px;
    font-weight: 800;
    line-height: 1;
    margin-bottom: 18px;
    position: relative;
    z-index: 2;
}

.label {
    font-size: 16px;
    font-weight: 600;
    opacity: 0.95;
    position: relative;
    z-index: 2;
}
</style>