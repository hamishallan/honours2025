<!-- src/components/SpectrumPlot.vue -->
<template>
  <div>
    <h2 v-if="spectrum">Spectrum for {{ spectrum.device_id }}</h2>
    <canvas v-if="spectrum" ref="canvas"></canvas>
  </div>
</template>

<script setup>
import { watch, ref, onMounted } from "vue";
import Chart from "chart.js/auto";

const props = defineProps({
  spectrum: Object,
});

const canvas = ref(null);
let chartInstance = null;

import { nextTick } from "vue";

const createChart = async () => {
  await nextTick();

  if (chartInstance) {
    chartInstance.destroy();
  }

  const ctx = canvas.value?.getContext("2d");
  if (!ctx) {
    console.error("Failed to create chart: can't acquire context from the given item");
    return;
  }

  const wavelengths = props.spectrum.data.map(p => p.wavelength);
  const intensities = props.spectrum.data.map(p => p.intensity);

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: wavelengths,
      datasets: [{
        label: "Intensity",
        data: intensities,
        fill: false,
        borderColor: "blue"
      }]
    }
  });
};


watch(
  () => props.spectrum,
  (newVal) => {
    if (newVal) {
      createChart();
    }
  }
);

onMounted(() => {
  if (props.spectrum) createChart();
});
</script>
