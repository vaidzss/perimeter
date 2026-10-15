import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from './client';
import { AlertStatus } from '../types';

export const QUERY_KEYS = {
  posture: ['posture'],
  inventory: (params?: any) => ['inventory', params],
  inventoryItem: (id: string) => ['inventoryItem', id],
  alerts: (params?: any) => ['alerts', params],
  alert: (id: string) => ['alert', id],
  alertRequests: (id: string) => ['alertRequests', id],
  actorActivity: (actor: string) => ['actorActivity', actor],
  riskScore: (id: string) => ['riskScore', id],
  trafficStats: (window: string) => ['trafficStats', window],
  evaluation: ['evaluation'],
  health: ['health'],
};

// 1. Posture hook - polls every 1.5 seconds
export function usePostureQuery() {
  return useQuery({
    queryKey: QUERY_KEYS.posture,
    queryFn: () => apiClient.getPosture(),
    refetchInterval: 1500,
  });
}

// 2. Inventory query - polls every 2 seconds
export function useInventoryQuery(params?: {
  status?: string;
  auth?: string;
  sensitive?: string;
  q?: string;
  sort?: string;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.inventory(params),
    queryFn: () => apiClient.getInventory(params),
    refetchInterval: 2000,
  });
}

// 3. Single API Item query
export function useInventoryItemQuery(apiId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.inventoryItem(apiId),
    queryFn: () => apiClient.getInventoryItem(apiId),
    enabled: !!apiId,
    refetchInterval: 2000,
  });
}

// 4. Alerts query - polls every 1.5 seconds for new live alerts
export function useAlertsQuery(params?: {
  severity?: string;
  type?: string;
  status?: string;
  api?: string;
  actor?: string;
}) {
  return useQuery({
    queryKey: QUERY_KEYS.alerts(params),
    queryFn: () => apiClient.getAlerts(params),
    refetchInterval: 1500,
  });
}

// 5. Single Alert query
export function useAlertQuery(alertId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.alert(alertId),
    queryFn: () => apiClient.getAlert(alertId),
    enabled: !!alertId,
    refetchInterval: 2000,
  });
}

// 6. Alert Requests query
export function useAlertRequestsQuery(alertId: string) {
  return useQuery({
    queryKey: QUERY_KEYS.alertRequests(alertId),
    queryFn: () => apiClient.getAlertRequests(alertId),
    enabled: !!alertId,
    refetchInterval: 2000,
  });
}

// 7. Actor Activity query
export function useActorActivityQuery(actor: string) {
  return useQuery({
    queryKey: QUERY_KEYS.actorActivity(actor),
    queryFn: () => apiClient.getActorActivity(actor),
    enabled: !!actor,
    refetchInterval: 2000,
  });
}

// 8. Update Alert Status mutation
export function useUpdateAlertStatusMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: AlertStatus }) =>
      apiClient.updateAlertStatus(id, status),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.alert(data.alert_id) });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.posture });
    },
  });
}

// 9. Traffic Stats query - polls every 2 seconds
export function useTrafficStatsQuery(window: string = '1h') {
  return useQuery({
    queryKey: QUERY_KEYS.trafficStats(window),
    queryFn: () => apiClient.getTrafficStats(window),
    refetchInterval: 2000,
  });
}

// 10. Evaluation query - polls every 1.5 seconds for live simulation validation
export function useEvaluationQuery() {
  return useQuery({
    queryKey: QUERY_KEYS.evaluation,
    queryFn: () => apiClient.getEvaluation(),
    refetchInterval: 1500,
  });
}

// 11. Health query
export function useHealthQuery() {
  return useQuery({
    queryKey: QUERY_KEYS.health,
    queryFn: () => apiClient.getHealth(),
    refetchInterval: 5000,
  });
}

// 12. Defense Status hook - polls every 1.5 seconds for live active defense stats
export function useDefenseStatusQuery() {
  return useQuery({
    queryKey: ['defenseStatus'],
    queryFn: () => apiClient.getDefenseStatus(),
    refetchInterval: 1500,
  });
}

// 13. One-click Active Defense Mitigation
export function useMitigateAllMutation() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => apiClient.mitigateAllThreats(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['defenseStatus'] });
      queryClient.invalidateQueries({ queryKey: QUERY_KEYS.posture });
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['inventory'] });
    },
  });
}

