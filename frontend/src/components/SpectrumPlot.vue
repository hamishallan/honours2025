<template>
  <div>
    <h2 v-if="spectrum">Plots</h2>
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

  const commonScales = {
    x: {
      type: "linear",
      min: 800,
      max: 2600,
      title: { display: true, text: "Wavelength" }
    },
    y: {
      type: "linear",
      title: { display: true, text: "Intensity" }
    }
  };

  // Raw Spectrum Chart
  const rawCtx = rawCanvas.value?.getContext("2d");
  if (!rawCtx) {
    console.error("Failed to get context for raw spectrum chart");
    return;
  }

  rawChartInstance = new Chart(rawCtx, {
    type: "line",
    data: {
      datasets: [{
        label: "Raw Spectrum",
        data: wavelengths.map((w, i) => ({ x: w, y: intensities[i] })),
        borderColor: "blue",
        fill: false
      }]
    },
    options: {
      responsive: true,
      scales: commonScales,
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

  // Copy common scales but change the Y-axis label for SNV
  const snvScales = JSON.parse(JSON.stringify(commonScales));
  snvScales.y.title.text = "SNV Intensity";

  snvChartInstance = new Chart(snvCtx, {
    type: "line",
    data: {
      datasets: [{
        label: "SNV Corrected Spectrum",
        data: wavelengths.map((w, i) => ({ x: w, y: snvIntensities[i] })),
        borderColor: "orange",
        fill: false
      }]
    },
    options: {
      responsive: true,
      scales: snvScales,
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
