<template>
  <section class="panel-card block">
    <h4>下一步</h4>
    <p>{{ archive.next_steps || "进入下一条路线，或针对重点章节做代码实践。" }}</p>
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
