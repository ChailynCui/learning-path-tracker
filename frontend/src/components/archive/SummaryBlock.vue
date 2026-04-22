<template>
  <section class="panel-card block">
    <h4>这次主要学了什么</h4>
    <p>{{ archive.what_i_learned || "完成了完整路线并形成结构化理解。" }}</p>
  </section>
</template>

<script setup>
defineProps({
  archive: { type: Object, required: true }
});
</script>

<style scoped>
.block {
  padding: 16px;
}
p {
  margin: 0;
  color: var(--muted);
}
</style>
