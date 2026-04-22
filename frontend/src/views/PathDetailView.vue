<template>
  <div v-if="path.id" class="layout">
    <PathHeader :path="path" />
    <section class="top-grid">
      <StudyStatusPanel
        :weekly-minutes="weeklyMinutes"
        :weekly-completed="weeklyCompleted"
        :pending-review="pendingReview"
        :streak="stats.streak"
        :total-units="path.total_units"
        :completed-units="path.completed_units"
      />
      <StudyTimerPanel
        :timer="timer"
        :pending-units="pendingUnits"
        :selected-unit-id="timerUnitId"
        @update:selected-unit-id="timerUnitId = $event"
        @start="handleTimerStart"
        @pause="handleTimerPause"
        @resume="handleTimerResume"
        @stop="handleTimerStop"
      />
    </section>
    <ChapterList
      :units="path.units"
      @complete="handleComplete"
      @mark-review="handleMarkReview"
      @review="handleReview"
      @plan-days="handlePlanDays"
    />
    <StudyLogPanel :logs="logs" />
  </div>

  <el-dialog v-model="completeDialogVisible" title="记录本章学习" width="460px">
    <el-form label-position="top">
      <el-form-item label="章节">
        <el-input :model-value="selectedUnit?.unit_title || ''" disabled />
      </el-form-item>
      <el-form-item label="学习时长（分钟）">
        <el-input-number v-model="completeForm.study_minutes" :min="1" :max="600" />
      </el-form-item>
      <el-form-item label="备注（可选）">
        <el-input v-model="completeForm.comment" type="textarea" :rows="3" />
      </el-form-item>
      <el-form-item>
        <el-checkbox v-model="completeForm.review_needed">加入待复习章节</el-checkbox>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="completeDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitComplete">确认完成</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage, ElMessageBox } from "element-plus";

import {
  completeUnit,
  fetchDashboard,
  fetchPathDetail,
  fetchPathLogs,
  fetchTimerStatus,
  markUnitForReview,
  pauseTimer,
  resumeTimer,
  reviewUnit,
  startTimer,
  stopTimer,
  updateUnitPlanDays
} from "../api/learning";
import ChapterList from "../components/path/ChapterList.vue";
import PathHeader from "../components/path/PathHeader.vue";
import StudyLogPanel from "../components/path/StudyLogPanel.vue";
import StudyStatusPanel from "../components/path/StudyStatusPanel.vue";
import StudyTimerPanel from "../components/path/StudyTimerPanel.vue";

const route = useRoute();
let ticker = null;

const path = reactive({
  id: null,
  title: "",
  type: "tutorial",
  source_url: "",
  daily_rule: "1 chapter/day",
  rule_type: "count",
  daily_chapter_count: 1,
  interval_days: 1,
  range_start: null,
  range_end: null,
  status: "ongoing",
  total_units: 0,
  completed_units: 0,
  units: []
});

const stats = reactive({
  streak: 0
});

const logs = ref([]);
const completeDialogVisible = ref(false);
const selectedUnit = ref(null);
const timerUnitId = ref(null);
const completeForm = reactive({
  study_minutes: 30,
  comment: "",
  review_needed: false
});
const timer = reactive({
  status: "idle",
  path_id: null,
  unit_id: null,
  elapsed_seconds: 0,
  elapsed_minutes: 0
});

const getWeekStart = () => {
  const now = new Date();
  const day = now.getDay();
  const diff = day === 0 ? -6 : 1 - day;
  const start = new Date(now);
  start.setDate(now.getDate() + diff);
  start.setHours(0, 0, 0, 0);
  return start;
};

const pendingUnits = computed(() => path.units.filter((unit) => unit.status !== "done"));

const weeklyMinutes = computed(() => {
  const weekStart = getWeekStart();
  return logs.value
    .filter((log) => {
      const logDate = new Date(log.log_date);
      return !Number.isNaN(logDate.getTime()) && logDate >= weekStart;
    })
    .reduce((sum, log) => sum + (log.study_minutes || 0), 0);
});

const weeklyCompleted = computed(() => {
  const weekStart = getWeekStart();
  return path.units.filter((unit) => {
    if (!unit.completed_at) return false;
    const completedDate = new Date(unit.completed_at);
    return !Number.isNaN(completedDate.getTime()) && completedDate >= weekStart;
  }).length;
});

const pendingReview = computed(() => path.units.filter((unit) => unit.review_needed).length);

const defaultComment = (title) => `${title} 已完成`;

const normalizeComment = (value, fallbackTitle) => {
  const text = (value || "").trim();
  return text || defaultComment(fallbackTitle);
};

const stopTicker = () => {
  if (ticker) {
    clearInterval(ticker);
    ticker = null;
  }
};

const startTicker = () => {
  stopTicker();
  ticker = setInterval(() => {
    if (timer.status === "running") {
      timer.elapsed_seconds += 1;
    }
  }, 1000);
};

const applyTimerState = (payload) => {
  timer.status = payload.status;
  timer.path_id = payload.path_id;
  timer.unit_id = payload.unit_id;
  timer.elapsed_seconds = payload.elapsed_seconds || 0;
  timer.elapsed_minutes = payload.elapsed_minutes || 0;
  if (!timerUnitId.value && payload.unit_id) {
    timerUnitId.value = payload.unit_id;
  }
  if (timer.status === "running") {
    startTicker();
  } else {
    stopTicker();
  }
};

const load = async () => {
  try {
    const [pathRes, dashRes, logRes, timerRes] = await Promise.all([
      fetchPathDetail(route.params.id),
      fetchDashboard(),
      fetchPathLogs(route.params.id),
      fetchTimerStatus(route.params.id)
    ]);
    Object.assign(path, pathRes.data);
    stats.streak = dashRes.data.current_streak;
    logs.value = logRes.data;
    applyTimerState(timerRes.data);
    if (!timerUnitId.value && pendingUnits.value.length) {
      timerUnitId.value = pendingUnits.value[0].id;
    }
  } catch (error) {
    ElMessage.error("加载详情失败。");
  }
};

const handleComplete = async (unit) => {
  selectedUnit.value = unit;
  completeForm.study_minutes = 30;
  completeForm.comment = defaultComment(unit.unit_title);
  completeForm.review_needed = Boolean(unit.review_needed);
  completeDialogVisible.value = true;
};

const submitComplete = async () => {
  if (!selectedUnit.value) return;
  try {
    const res = await completeUnit(path.id, selectedUnit.value.id, {
      study_minutes: completeForm.study_minutes,
      comment: normalizeComment(completeForm.comment, selectedUnit.value.unit_title),
      review_needed: completeForm.review_needed
    });
    stats.streak = res.data.current_streak;
    completeDialogVisible.value = false;
    ElMessage.success("本章已完成，学习状态已更新。");
    await load();
  } catch (error) {
    ElMessage.error("操作失败。");
  }
};

const handleReview = async (unit) => {
  try {
    const { value } = await ElMessageBox.prompt(
      `请输入「${unit.unit_title}」复习时长（分钟）`,
      "记录复习",
      {
        confirmButtonText: "确认复习完成",
        cancelButtonText: "取消",
        inputValue: "15",
        inputPattern: /^[1-9]\d{0,2}$/,
        inputErrorMessage: "请输入 1-999 的整数分钟"
      }
    );
    await reviewUnit(path.id, unit.id, {
      study_minutes: Number(value),
      comment: `复习完成：${unit.unit_title}`
    });
    ElMessage.success("已从待复习队列移除。");
    await load();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("复习记录失败。");
    }
  }
};

const handleMarkReview = async (unit) => {
  try {
    await markUnitForReview(path.id, unit.id);
    ElMessage.success(`已将「${unit.unit_title}」加入待复习。`);
    await load();
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "加入复习队列失败。");
  }
};

const handlePlanDays = async (unit, plannedDays) => {
  try {
    await updateUnitPlanDays(path.id, unit.id, plannedDays);
    ElMessage.success(`已更新「${unit.unit_title}」为 ${plannedDays} 天。`);
    await load();
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "更新章节计划失败。");
  }
};

const handleTimerStart = async () => {
  if (!timerUnitId.value) {
    ElMessage.warning("请先选择一个章节再开始计时。");
    return;
  }
  try {
    const res = await startTimer(path.id, timerUnitId.value);
    applyTimerState(res.data);
    ElMessage.success("计时已开始。");
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "开始计时失败。");
  }
};

const handleTimerPause = async () => {
  try {
    const res = await pauseTimer(path.id);
    applyTimerState(res.data);
    ElMessage.success("计时已暂停。");
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "暂停失败。");
  }
};

const handleTimerResume = async () => {
  try {
    const res = await resumeTimer(path.id);
    applyTimerState(res.data);
    ElMessage.success("已继续计时。");
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "继续失败。");
  }
};

const handleTimerStop = async () => {
  try {
    const res = await stopTimer(path.id);
    applyTimerState(res.data);
    const unit = path.units.find((item) => item.id === res.data.unit_id);
    if (unit && unit.status !== "done") {
      selectedUnit.value = unit;
      completeForm.study_minutes = res.data.suggested_minutes || 1;
      completeForm.comment = defaultComment(unit.unit_title);
      completeForm.review_needed = Boolean(unit.review_needed);
      completeDialogVisible.value = true;
      ElMessage.success("计时结束，已自动写入建议学习时长。");
    } else {
      ElMessage.success("计时结束。");
    }
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || "结束计时失败。");
  }
};

onMounted(load);
onBeforeUnmount(stopTicker);
</script>

<style scoped>
.layout {
  display: grid;
  gap: 16px;
}

.top-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 1.35fr 1fr;
}

@media (max-width: 980px) {
  .top-grid {
    grid-template-columns: 1fr;
  }
}
</style>
