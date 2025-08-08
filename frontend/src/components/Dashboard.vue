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
        @select="selected = $event"
      />
      <!-- Drag handle -->
      <div class="resize-handle" @mousedown.prevent="startResize" />
    </aside>

    <section class="main">
      <header class="main-header">
        <strong>{{ selected ? selected.message : "Select a spectrum" }}</strong>
      </header>
      <div class="main-body">
        <!-- PredictionCard / Plot will go here later -->
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onBeforeUnmount } from "vue";
import SidebarTable from "./SidebarTable.vue";

/* Grid column width for the sidebar (left column) */
const sidebarWidth = ref(500);

/* Temporary local data */
const items = ref([
  {
    id: 1,
    message: "bt_test 5mm, screws",
    avg: 100,
    gain: "High",
    apo: "NortonBeerStrong",
  },
  { id: 2, message: "soil core A", avg: 50, gain: "Low", apo: "Hamming" },
  { id: 3, message: "field sample B", avg: 80, gain: "High", apo: "Blackman" },
]);

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
  const x = e.clientX - rect.left;       // width relative to the dashboard's left edge
  const min = 200;
  const max = 520;
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
  right: 0;                 /* was -3px */
  width: 8px;               /* was 6px */
  height: 100%;
  cursor: ew-resize;
  background: transparent;
  z-index: 10;              /* ensure it's clickable */
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
