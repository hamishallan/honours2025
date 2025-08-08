<template>
  <div
    :class="['row', { active }]"
    role="button"
    tabindex="0"
    @click="$emit('select')"
    @keydown.enter="$emit('select')"
    @keydown.space.prevent="$emit('select')"
    :aria-pressed="active ? 'true' : 'false'"
  >
    <div class="cell title">{{ meta.msg || meta.deviceName || 'Untitled spectrum' }}</div>
    <div class="cell">{{ meta.avg ?? '—' }}</div>
    <div class="cell">{{ meta.gain ?? '—' }}</div>
    <!-- <div class="cell">{{ meta.apo ?? '—' }}</div> -->
  </div>
</template>

<script setup>
import { computed } from "vue";
import { parseDeviceMeta } from "../utils/deviceMeta";

const props = defineProps({
  spectrum: { type: Object, required: true },
  active: { type: Boolean, default: false }
});
defineEmits(["select"]);

const meta = computed(() => {
  const name =
    props.spectrum?.device?.name ??
    props.spectrum?.device_name ??
    props.spectrum?.device_id ??
    "";
  return parseDeviceMeta(name);
});
</script>

<style scoped>
.row {
  display: grid;
  grid-template-columns: 2fr 0.5fr 0.5fr; /* flexible widths */
  gap: 0.5rem;
  padding: 0.6rem 0.8rem;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color .2s ease, transform .06s ease;
  background-color: rgba(255,255,255,0.05);
  margin-bottom: 0.5rem;
}
.row:hover { background-color: #415a77; transform: translateY(-1px); }
.row.active { background-color: #00b4d8; color: #0d1b2a; font-weight: 600; }
.cell.title { font-weight: 700; word-break: break-word; }
</style>