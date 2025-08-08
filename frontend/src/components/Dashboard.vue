<template>
  <div
    class="dashboard"
    ref="dashEl"
    :style="{ '--sidebar-width': sidebarWidth + 'px' }"
  >
    <aside class="sidebar" ref="sidebarEl">
      <SidebarTable
        :items="items"
        :selected-id="selected?.id ?? null"
        :loading="loading"
        @select="selected = $event"
      />
      <!-- Drag handle -->
      <div class="resize-handle" @mousedown.prevent="startResize" />
    </aside>

    <section class="main">
      <MainContent :selectedSpectrum="selected" v-model:showPlot="showPlot" />
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from "vue";
import SidebarTable from "./SidebarTable.vue";
import MainContent from "./MainContent.vue";
import { API_BASE_URL } from "../config/api";
import { parseDeviceMeta } from "../utils/deviceMeta";

const sidebarWidth = ref(550);
const items = ref([]);
const selected = ref(null);
const showPlot = ref(false);
const loading = ref(true);

async function fetchSpectra() {
  try {
    loading.value = true;
    const res = await fetch(`${API_BASE_URL}/spectra/`);
    const spectra = await res.json();

    // Map API spectra -> table items
    items.value = (spectra || []).map((s) => {
      const name = s?.device?.name ?? s?.device_name ?? s?.device_id ?? "";
      const meta = parseDeviceMeta(name);
      return {
        id: s.id ?? s.spectrum_id ?? name, // fallback id
        message: meta.msg || meta.deviceName || "Untitled spectrum",
        avg: meta.avg ?? "—",
        gain: meta.gain ?? "—",
        raw: s,
      };
    });

    // Auto-select first item (optional)
    if (!selected.value && items.value.length) {
      selected.value = items.value[0].raw;
    }
  } catch (err) {
    console.error("Failed to load spectra", err);
    items.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(fetchSpectra);

let isResizing = false;

function startResize(e) {
  isResizing = true;
  document.addEventListener("mousemove", onDrag);
  document.addEventListener("mouseup", stopResize);
  document.body.style.userSelect = "none";
}

const dashEl = ref(null);

function onDrag(e) {
  if (!isResizing || !dashEl.value) return;
  const rect = dashEl.value.getBoundingClientRect();
  const x = e.clientX - rect.left; // width relative to the dashboard's left edge
  const min = 200;
  const max = 1000;
  sidebarWidth.value = Math.min(Math.max(x, min), max);
}

function stopResize() {
  isResizing = false;
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopResize);
  document.body.style.userSelect = "";
}

onBeforeUnmount(() => {
  // Clean up if component unmounts mid-drag
  document.removeEventListener("mousemove", onDrag);
  document.removeEventListener("mouseup", stopResize);
  document.body.style.userSelect = "";
});
</script>

<style scoped>
.dashboard {
  display: grid;
  grid-template-columns: var(--sidebar-width, 280px) 1fr; /* sidebar | main */
  grid-template-rows: 100%;
  height: 100vh;
  width: 100vw;
  min-width: 0;
  background: #0d1220;
  color: #e6edf3;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Inter, Arial,
    sans-serif;
}

/* Sidebar column */
.sidebar {
  position: relative;
  background: #0f172a;
  border-right: 1px solid #22324b;
  overflow: auto;
  padding: 1rem 1rem;
  min-width: 200px; /* matches JS clamp */
}

/* Drag handle hugs the right edge of the sidebar */
.resize-handle {
  position: absolute;
  top: 0;
  right: 0; /* was -3px */
  width: 8px; /* was 6px */
  height: 100%;
  cursor: ew-resize;
  background: transparent;
  z-index: 10; /* ensure it's clickable */
}
.resize-handle:hover {
  background: rgba(255, 255, 255, 0.08);
}

/* Main column */
.main {
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: #0b1220;
}

.main-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #22324b;
}

.main-body {
  flex: 1;
  overflow: auto;
  padding: 1rem 1.25rem;
}
</style>
