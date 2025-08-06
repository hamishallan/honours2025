<template>
  <div v-if="spectrum" class="prediction-card">
    <div class="card-header">
      <span>Predicted Soil Organic Carbon (SOC)</span>
    </div>

    <div class="card-body">
      <div v-if="spectrum.predicted_value !== null" class="prediction-value">
        {{ spectrum.predicted_value.toFixed(2) }}
        <span class="unit">%</span>
      </div>
      <div v-else class="no-prediction">
        No prediction available.
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  spectrum: Object
});
</script>

<style scoped>
.prediction-card {
  background: linear-gradient(135deg, #edf2f7, #e0f7fa);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  margin: 1rem auto;
  font-family: 'Segoe UI', Roboto, sans-serif;
  transition: all 0.3s ease;
}

.card-header {
  font-size: 1.1rem;
  font-weight: 600;
  color: #37474f;
  margin-bottom: 1rem;
  text-align: center;
}

.card-body {
  display: flex;
  justify-content: center;
  align-items: baseline;
}

.prediction-value {
  font-size: 3rem;
  font-weight: 700;
  color: #00796b;
}

.unit {
  font-size: 1.2rem;
  margin-left: 0.3rem;
  color: #004d40;
}

.no-prediction {
  font-size: 1.2rem;
  color: #777;
  font-style: italic;
}
</style>
