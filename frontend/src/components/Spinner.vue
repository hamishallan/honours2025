<template>
  <div class="spinner" :style="spinnerStyle"></div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  size: { type: Number, default: 32 },
  color: { type: String, default: "#00b4d8" }
});

const spinnerStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  borderWidth: `${props.size / 8}px`,
  borderStyle: 'solid',
  borderColor: 'rgba(255, 255, 255, 0.2)',
  borderTopColor: props.color
}));
</script>

<style scoped>
.spinner {
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
