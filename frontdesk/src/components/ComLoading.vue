<template>
  <Teleport to="body">
    <div v-if="visible" class="loading-overlay">
      <div class="loading-box">
        <div class="spinner"></div>
        <p class="message">{{ message }}</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, defineExpose } from "vue"

const visible = ref(false)
const message = ref("Loading...")

function open(msg = "Loading...") {
  message.value = msg
  visible.value = true
}

function close() {
  visible.value = false
}

defineExpose({
  open,
  close
})
</script>

<style scoped>
.loading-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(2px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-box {
  background: white;
  padding: 24px 32px;
  border-radius: 10px;
  text-align: center;
  min-width: 220px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #ddd;
  border-top-color: #409eff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 12px;
}

.message {
  font-size: 14px;
  color: #333;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>