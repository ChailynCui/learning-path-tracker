import client from "./client";

export const fetchDashboard = () => client.get("/dashboard");
export const updateWeeklyGoal = (target) => client.put("/dashboard/weekly-goal", { target });
export const fetchPaths = () => client.get("/paths");
export const fetchPathDetail = (pathId) => client.get(`/paths/${pathId}`);
export const updatePathRule = (pathId, payload) => client.put(`/paths/${pathId}/rule`, payload);
export const updateUnitPlanDays = (pathId, unitId, plannedDays) =>
  client.put(`/paths/${pathId}/units/${unitId}/plan-days`, { planned_days: plannedDays });
export const fetchPathLogs = (pathId) => client.get(`/paths/${pathId}/logs`);
export const createPath = (payload) => client.post("/paths", payload);
export const completeUnit = (pathId, unitId, payload) =>
  client.post(`/paths/${pathId}/units/${unitId}/complete`, payload);
export const reviewUnit = (pathId, unitId, payload) =>
  client.post(`/paths/${pathId}/units/${unitId}/review`, payload);
export const markUnitForReview = (pathId, unitId) =>
  client.post(`/paths/${pathId}/units/${unitId}/mark-review`);
export const fetchTimerStatus = (pathId) => client.get(`/paths/${pathId}/timer`);
export const startTimer = (pathId, unitId) => client.post(`/paths/${pathId}/timer/start`, { unit_id: unitId });
export const pauseTimer = (pathId) => client.post(`/paths/${pathId}/timer/pause`);
export const resumeTimer = (pathId) => client.post(`/paths/${pathId}/timer/resume`);
export const stopTimer = (pathId) => client.post(`/paths/${pathId}/timer/stop`);
export const exportBackup = () => client.get("/backup/export");
export const importBackup = (data) => client.post("/backup/import", { data });
export const fetchArchives = () => client.get("/archives");
