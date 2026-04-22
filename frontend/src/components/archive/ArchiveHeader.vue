<template>
  <section class="panel-card panel">
    <h3>{{ archive.path_title }}</h3>
    <p>
      类型：{{ archive.path_type === "tutorial" ? "教程学习" : "开源项目学习" }} ·
      完成率：{{ archive.completed_units }}/{{ archive.total_units }}
    </p>
    <a v-if="archive.source_url" :href="archive.source_url" target="_blank" rel="noreferrer">
      {{ archive.source_url }}
    </a>
    <p v-else>来源链接：未填写</p>
  </section>
</template>

<script setup>
defineProps({
  archive: { type: Object, required: true }
});
</script>

<style scoped>
.panel {
  padding: 16px;
}
h3 {
  margin: 0 0 8px;
}
p,
a {
  margin: 0;
  color: var(--muted);
}
</style>
