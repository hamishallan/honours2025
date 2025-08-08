<template>
  <aside class="sidebar" :style="{ width: width + 'px' }">
    <h2>Available Spectra</h2>

    <div v-if="loading" class="spinner-container">
      <div class="spinner"></div>
      <span>Loading...</span>
    </div>

    <div v-else class="table">
      <div class="header row">
        <div class="cell title">Message</div>
        <div class="cell">Avg</div>
        <div class="cell">Gain</div>
        <!-- <div class="cell">Apo</div> -->
      </div>

      <SpectrumRow
        v-for="s in spectra"
        :key="s.id"
        :spectrum="s"
        :active="s.id === selectedSpectrum?.id"
        @select="$emit('select', s)"
      />
    </div>

    <!-- Resize handle -->
    <div class="resize-handle" @mousedown="startResize"></div>
  </aside>
</template>

<script setup>
import { onBeforeUnmount } from "vue";
import SpectrumRow from "./SpectrumRow.vue";

const props = defineProps({
  spectra: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  selectedSpectrum: { type: Object, default: null },
  width: { type: Number, default: 260 }               // NEW
});
const emit = defineEmits(["select", "update:width"]);  // NEW

let isResizing = false;

function startResize() {
  isResizing = true;
  document.addEventListener("mousemove", resize);
  document.addEventListener("mouseup", stopResize);
}
function resize(e) {
  if (!isResizing) return;
  const newWidth = Math.min(Math.max(200, e.clientX), 500); // clamp 200–500
  emit("update:width", newWidth);                           // NEW
}
function stopResize() {
  isResizing = false;
  document.removeEventListener("mousemove", resize);
  document.removeEventListener("mouseup", stopResize);
}
onBeforeUnmount(stopResize);
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  background: linear-gradient(180deg, #1b263b, #0d1b2a);
  padding: 1.5rem 1rem;
  border-right: 1px solid rgba(255, 255, 255, 0.08);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sidebar h2 {
  font-size: 1.2rem;
  margin-bottom: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.table { display: block; }
.header {
  position: sticky;
  top: 0;
  z-index: 1;
  background: linear-gradient(180deg, #1b263b, #0d1b2a);
  margin-bottom: 0.5rem;
  padding: 0.6rem 0.8rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
  border-radius: 8px;
}
.header.row {
  display: grid;
  grid-template-columns: 2fr 0.5fr 0.5fr;
  gap: 0.5rem;
}
.header .cell { font-weight: 700; opacity: 0.9; }
.header .cell.title { text-transform: uppercase; letter-spacing: .5px; font-size: .9rem; }

/* Resize handle */
.resize-handle {
  position: absolute;
  top: 0;
  right: 0;
  width: 6px;
  height: 100%;
  cursor: ew-resize;
  background: transparent;
}
.resize-handle:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Spinner */
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  color: #a9bcd0;
}
.spinner {
  border: 4px solid rgba(255, 255, 255, 0.1);
  border-top: 4px solid #00b4d8;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  animation: spin 1s linear infinite;
  margin-bottom: 0.5rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
