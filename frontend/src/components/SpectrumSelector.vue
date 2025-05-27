<template>
  <div>
    <h2>Select a Spectrum</h2>
    <div v-if="loading">Loading spectra...</div>
    <div v-else>
      <select v-model="selectedId" @change="onSelect">
        <option disabled value="">Available spectra...</option>
        <option
          v-for="spectrum in spectra"
          :key="spectrum.id"
          :value="spectrum.id"
        >
          {{ spectrum.device_id }} ({{
            new Date(spectrum.timestamp).toLocaleString()
          }})
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const spectra = ref([]);
const selectedId = ref("");
const loading = ref(true);

const emit = defineEmits(["selected"]);

const fetchSpectra = async () => {
  try {
    const res = await fetch(
      "https://rekehtm1f0.execute-api.us-east-1.amazonaws.com/dev/spectra/"
    );
    const data = await res.json();
    spectra.value = data;
  } catch (error) {
    console.error("Error fetching spectra:", error);
  } finally {
    loading.value = false;
  }
};

const onSelect = () => {
  const selectedSpectrum = spectra.value.find((s) => s.id === selectedId.value);
  emit("selected", selectedSpectrum);
};

onMounted(fetchSpectra);
</script>
