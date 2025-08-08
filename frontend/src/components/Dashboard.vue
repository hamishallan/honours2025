<template>
  <div class="dashboard" :style="{ '--sidebar-width': sidebarWidth + 'px' }">
    <Sidebar
      :spectra="spectra"
      :loading="loading"
      :selectedSpectrum="selectedSpectrum"
      :width="sidebarWidth"
      @update:width="val => (sidebarWidth = val)"
      @select="selectedSpectrum = $event"
    />

    <MainContent
      :selectedSpectrum="selectedSpectrum"
      v-model:showPlot="showPlot"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import Sidebar from "./Sidebar.vue";
import MainContent from "./MainContent.vue";
import { API_BASE_URL } from "../config/api.js";

const spectra = ref([]);
const selectedSpectrum = ref(null);
const showPlot = ref(false);
const loading = ref(true);
const sidebarWidth = ref(260);

async function fetchSpectra() {
  loading.value = true;
  try {
    const res = await fetch(`${API_BASE_URL}/spectra/`);
    spectra.value = await res.json();
  } catch (err) {
    console.error("Failed to load spectra", err);
  } finally {
    loading.value = false;
  }
}

onMounted(fetchSpectra);
</script>

<style scoped>
.dashboard {
  display: flex;
  height: 100vh;
  background-color: #0d1b2a;
  color: #e0e1dd;
  font-family: 'Inter', sans-serif;
}
</style>
