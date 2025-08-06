<template>
  <div v-if="spectrum" class="prediction-card">
    <div class="prediction-header">
      <span class="title">Soil Organic Carbon (SOC)</span>
      <span :class="['status-badge', badgeClass]">{{ statusLabel }}</span>
    </div>

    <div class="prediction-main">
      <span class="value">{{ spectrum.predicted_value.toFixed(2) }}%</span>
      <p class="description">{{ description }}</p>
    </div>

    <div class="prediction-footer">
      <p class="info-text">
        SOC is a key indicator of soil health and fertility. Higher SOC levels usually mean better soil quality.
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  spectrum: Object
});

const predicted = computed(() => props.spectrum?.predicted_value ?? null);

const statusLabel = computed(() => {
  const val = predicted.value;
  if (val === null) return 'No Data';
  if (val < 1.5) return 'Low';
  if (val < 2.5) return 'Moderate';
  return 'High';
});

const badgeClass = computed(() => {
  const val = predicted.value;
  if (val === null) return 'badge-neutral';
  if (val < 1.5) return 'badge-low';
  if (val < 2.5) return 'badge-mid';
  return 'badge-high';
});

const description = computed(() => {
  const val = predicted.value;
  if (val === null) return 'Prediction not available for this spectrum.';
  if (val < 1.5) return 'This indicates poor soil health. Consider increasing organic matter.';
  if (val < 2.5) return 'This is a moderate SOC level. Further improvement may be beneficial.';
  return 'Excellent SOC levels. This soil is healthy and productive.';
});
</script>

<style scoped>
.prediction-card {
  background: #f9fafb;
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 500px;
  margin: 1.5rem auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  font-family: 'Segoe UI', Roboto, sans-serif;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.prediction-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 1.2rem;
  font-weight: 600;
  color: #1e293b;
}

.status-badge {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  color: #fff;
}

.badge-low {
  background-color: #e53935;
}

.badge-mid {
  background-color: #f9a825;
}

.badge-high {
  background-color: #43a047;
}

.badge-neutral {
  background-color: #9e9e9e;
}

.prediction-main {
  text-align: center;
}

.value {
  font-size: 3rem;
  font-weight: bold;
  color: #111827;
}

.description {
  font-size: 1rem;
  margin-top: 0.5rem;
  color: #374151;
}

.prediction-footer {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.info-text {
  font-size: 0.875rem;
  color: #6b7280;
  text-align: center;
}
</style>
