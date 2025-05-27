<template>
  <div>
    <h2 v-if="spectrum">Spectrum for {{ spectrum.device_id }}</h2>
    <canvas v-if="spectrum" ref="rawCanvas"></canvas>
    <canvas v-if="spectrum" ref="snvCanvas" class="mt-4"></canvas>
  </div>
</template>

<script setup>
import { watch, ref, onMounted, nextTick } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  spectrum: Object
});

const rawCanvas = ref(null);
const snvCanvas = ref(null);
let rawChartInstance = null;
let snvChartInstance = null;

const createCharts = async () => {
  await nextTick();

  // Destroy previous charts if they exist
  rawChartInstance?.destroy();
  snvChartInstance?.destroy();

  const wavelengths = props.spectrum.data.map(p => p.wavelength);
  const intensities = props.spectrum.data.map(p => p.intensity);

  // SNV correction
  const mean = intensities.reduce((a, b) => a + b, 0) / intensities.length;
  const std = Math.sqrt(intensities.reduce((sum, val) => sum + (val - mean) ** 2, 0) / intensities.length);
  const snvIntensities = intensities.map(val => (val - mean) / std);

  // Raw Spectrum Chart
  const rawCtx = rawCanvas.value?.getContext("2d");
  if (!rawCtx) {
    console.error("Failed to get context for raw spectrum chart");
    return;
  }

  rawChartInstance = new Chart(rawCtx, {
    type: "line",
    data: {
      labels: wavelengths,
      datasets: [{
        label: "Raw Spectrum",
        data: intensities,
        borderColor: "blue",
        fill: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "Raw Spectrum"
        }
      }
    }
  });

  // SNV-Corrected Spectrum Chart
  const snvCtx = snvCanvas.value?.getContext("2d");
  if (!snvCtx) {
    console.error("Failed to get context for SNV corrected chart");
    return;
  }

  snvChartInstance = new Chart(snvCtx, {
    type: "line",
    data: {
      labels: wavelengths,
      datasets: [{
        label: "SNV Corrected Spectrum",
        data: snvIntensities,
        borderColor: "orange",
        fill: false
      }]
    },
    options: {
      responsive: true,
      plugins: {
        title: {
          display: true,
          text: "SNV Corrected Spectrum"
        }
      }
    }
  });
};

watch(() => props.spectrum, (newVal) => {
  if (newVal) {
    createCharts();
  }
});

onMounted(() => {
  if (props.spectrum) createCharts();
});
</script>

<style>
.mt-4 {
  margin-top: 1rem;
}
</style>
