export const NOTIFICATION_MIN_URGENCY_LEVELS = ["high", "medium", "low"] as const;

export type NotificationMinUrgency = (typeof NOTIFICATION_MIN_URGENCY_LEVELS)[number];
