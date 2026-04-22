<template>
  <section class="panel-card page">
    <h2>创建学习路线</h2>

    <el-form :model="form" label-position="top">
      <el-form-item label="路线名称">
        <el-input v-model="form.title" placeholder="例如：FastAPI 从入门到实战" />
      </el-form-item>

      <el-form-item label="学习类型">
        <el-radio-group v-model="form.type">
          <el-radio value="tutorial">教程学习</el-radio>
          <el-radio value="open_source">开源项目学习</el-radio>
        </el-radio-group>
      </el-form-item>

      <el-form-item label="GitHub 链接">
        <el-input v-model="form.source_url" placeholder="可选：课程/仓库链接" />
      </el-form-item>

      <el-form-item label="简介">
        <el-input v-model="form.description" type="textarea" :rows="3" />
      </el-form-item>

      <el-form-item label="章节清单（每行一个 chapter）">
        <el-input
          v-model="form.units_text"
          type="textarea"
          :rows="8"
          placeholder="Day 1 - Chapter 1: Intro&#10;Day 2 - Chapter 2: Setup&#10;Day 3 - Chapter 3: API Basics"
        />
      </el-form-item>

      <div class="actions">
        <el-button type="primary" :disabled="units.length === 0" @click="handleCreate">
          创建路线
        </el-button>
      </div>
    </el-form>

    <section class="preview" v-if="units.length">
      <h3>手动上传结果</h3>
      <p>总章节数：{{ units.length }}</p>
      <p>学习预计天数：{{ estimatedDays }} 天（默认 1 天 1 章）</p>
      <ul>
        <li v-for="(unit, index) in units" :key="`${index}-${unit}`">Day {{ index + 1 }} · {{ unit }}</li>
      </ul>
    </section>
  </section>
</template>

<script setup>
import { computed, reactive } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";

import { createPath } from "../api/learning";

const router = useRouter();

const form = reactive({
  title: "",
  type: "tutorial",
  source_url: "",
  description: "",
  units_text: ""
});

const units = computed(() =>
  form.units_text
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
);

const estimatedDays = computed(() => units.value.length);

const handleCreate = async () => {
  if (units.value.length === 0) {
    ElMessage.warning("请至少填写一章内容。");
    return;
  }
  try {
    const payload = {
      title: form.title,
      type: form.type,
      source_url: form.source_url,
      description: form.description,
      daily_rule: "1 chapter/day",
      rule_type: "count",
      daily_chapter_count: 1,
      interval_days: 1,
      range_start: null,
      range_end: null,
      units: units.value
    };
    const res = await createPath(payload);
    ElMessage.success("学习路线已创建。");
    router.push(`/paths/${res.data.id}`);
  } catch (error) {
    ElMessage.error("创建失败，请检查输入内容。");
  }
};
</script>

<style scoped>
.page {
  padding: 18px;
}
h2 {
  margin-top: 0;
}
.actions {
  display: flex;
  gap: 10px;
}
.preview {
  margin-top: 18px;
  border-top: 1px solid rgba(25, 52, 65, 0.1);
  padding-top: 14px;
}
ul {
  margin: 8px 0 0;
  padding-left: 20px;
}
</style>
