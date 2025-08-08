<template>
  <div class="table">
    <div class="row header">
      <div class="cell title">Message</div>
      <div class="cell num">Avg</div>
      <div class="cell num">Gain</div>
    </div>

    <button
      v-for="it in items"
      :key="it.id"
      class="row btn"
      :class="{ active: it.id === selectedId }"
      @click="$emit('select', it)"
    >
      <div class="cell title">{{ it.message }}</div>
      <div class="cell num">{{ it.avg }}</div>
      <div class="cell num">{{ it.gain }}</div>
    </button>
  </div>
</template>

<script setup>
defineProps({
  items: { type: Array, default: () => [] },
  selectedId: { type: [String, Number, null], default: null },
});
defineEmits(["select"]);
</script>

<style scoped>
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
  align-items: center;      /* vertical centering */
  justify-content: center;  /* horizontal centering */
}

.cell.title {
  justify-content: flex-start; /* keep message text left-aligned */
}
</style>
