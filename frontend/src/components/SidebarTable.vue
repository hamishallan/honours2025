<template>
  <div class="sidebar-wrapper">
    <h2 class="sidebar-title">Spectra List</h2>
    <div class="table">
      <div class="table">
        <div v-if="loading" class="loader-container">
          <Spinner :size="32" color="#00b4d8" />
        </div>

        <div v-else class="row header">
          <div class="cell title">Message</div>
          <div class="cell num">Avg</div>
          <div class="cell num">Gain</div>
        </div>

        <template v-if="!loading">
          <button
            v-for="it in items"
            :key="it.id"
            class="row btn"
            :class="{ active: (it.raw?.id ?? it.id) === selectedId }"
            @click="$emit('select', it.raw ?? it)"
          >
            <div class="cell title">{{ it.message }}</div>
            <div class="cell num">{{ it.avg }}</div>
            <div class="cell num">{{ it.gain }}</div>
          </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import Spinner from "./Spinner.vue";
defineProps({
  items: { type: Array, default: () => [] },
  selectedId: { type: [String, Number, null], default: null },
  loading: { type: Boolean, default: false },
});
defineEmits(["select"]);
</script>

<style scoped>
.sidebar-wrapper {
  display: flex;
  flex-direction: column;
}

.sidebar-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: #f0f0f0; /* off-white to match your theme */
  margin-bottom: 0.75rem;
  padding-left: 0.5rem;
}

.table {
  display: block;
  width: 100%;
  font-family: Consolas, Monaco, "Courier New", monospace;
  --cols: 2fr 1fr 1fr;
}

.row {
  display: grid;
  width: 100%;
  grid-template-columns: var(--cols);
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
}

.header {
  position: sticky;
  width: 100%;
  top: 0;
  background: #0f172a;
  border-bottom: 1px solid #22324b;
  font-weight: 700;
  opacity: 0.9;
  z-index: 1;
}

.header.row {
  grid-template-columns: var(--cols);
}

.btn {
  background: rgba(255, 255, 255, 0.05);
  border: 0;
  border-radius: 8px;
  width: 100%;
  text-align: left;
  color: inherit;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.06s ease;
  margin-top: 0.5rem;
  display: grid;
}
.btn:hover {
  background: #415a77;
  transform: translateY(-1px);
}
.btn.active {
  background: #00b4d8;
  color: #0b1220;
  font-weight: 700;
}

.cell {
  display: flex;
  align-items: center; /* vertical centering */
  justify-content: center; /* horizontal centering */
}

.cell.title {
  justify-content: flex-start; /* keep message text left-aligned */
}

.loader-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80px; /* ensures it's visible even with no rows */
  padding: 1rem;
}
</style>
