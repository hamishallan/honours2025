<template>
  <div v-if="spectrum" :class="['prediction-card', colourClass]">
    <div class="card-header">
      Predicted Soil Organic Carbon (SOC)
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
const props = defineProps({ spectrum: Object });

const colourClass = computed(() => {
  const val = props.spectrum?.predicted_value;
  if (val === null || val === undefined) return 'bg-neutral';
  if (val < 1.5) return 'bg-low';
  if (val < 2.5) return 'bg-mid';
  return 'bg-high';
});
</script>

<style scoped>
.prediction-card {
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  max-width: 400px;
  margin: 1rem auto;
  font-family: 'Segoe UI', Roboto, sans-serif;
  transition: background 0.3s ease;
  color: #1e293b;
}

.card-header {
  font-size: 1.1rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 1rem;
}

.card-body {
  display: flex;
  justify-content: center;
  align-items: baseline;
}

.prediction-value {
  font-size: 3rem;
  font-weight: 700;
}

.unit {
  font-size: 1.2rem;
  margin-left: 0.3rem;
}

.no-prediction {
  font-size: 1.2rem;
  color: #777;
  font-style: italic;
}

/* Colour classes */
.bg-low {
  background: #ffe5e0; /* red/orange for low SOC */
  color: #c62828;
}

.bg-mid {
  background: #fff9c4; /* yellow for moderate SOC */
  color: #f9a825;
}

.bg-high {
  background: #e0f2f1; /* green for high SOC */
  color: #2e7d32;
}

.bg-neutral {
  background: #eceff1;
  color: #455a64;
}
</style>
