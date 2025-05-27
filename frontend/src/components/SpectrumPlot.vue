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

const createChart = () => {
  if (chartInstance) {
    chartInstance.destroy();
  }

  const wavelengths = props.spectrum.data.map((p) => p.wavelength);
  const intensities = props.spectrum.data.map((p) => p.intensity);

  chartInstance = new Chart(canvas.value, {
    type: "line",
    data: {
      labels: wavelengths,
      datasets: [
        {
          label: "Intensity",
          data: intensities,
          fill: false,
        },
      ],
    },
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
