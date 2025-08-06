<template>
  <div v-if="spectrum">
    <h2>Predicted SOC</h2>
    <p v-if="spectrum.predicted_value !== null">
      <strong>{{ spectrum.predicted_value.toFixed(2) }}</strong>
    </p>
    <p v-else>
      No prediction available for this spectrum.
    </p>
  </div>
</template>

<script setup>
defineProps({
  spectrum: Object
});
</script>