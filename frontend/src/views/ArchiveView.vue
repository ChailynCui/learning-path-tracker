<template>
  <div class="grid" v-if="archives.length">
    <article v-for="item in archives" :key="item.id" class="stack">
      <ArchiveHeader :archive="item" />
      <SummaryBlock :archive="item" />
      <KeyPointsBlock :archive="item" />
      <NextStepBlock :archive="item" />
    </article>
  </div>
  <section v-else class="panel-card empty">暂无归档，完成一条路线后会自动生成。</section>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";

import { fetchArchives } from "../api/learning";
import ArchiveHeader from "../components/archive/ArchiveHeader.vue";
import KeyPointsBlock from "../components/archive/KeyPointsBlock.vue";
import NextStepBlock from "../components/archive/NextStepBlock.vue";
import SummaryBlock from "../components/archive/SummaryBlock.vue";

const archives = ref([]);

const loadArchives = async () => {
  try {
    const res = await fetchArchives();
    archives.value = res.data;
  } catch (error) {
    ElMessage.error("加载归档失败。");
  }
};

onMounted(loadArchives);
</script>

<style scoped>
.grid {
  display: grid;
  gap: 16px;
}
.stack {
  display: grid;
  gap: 10px;
}
.empty {
  padding: 16px;
  color: var(--muted);
}
</style>
