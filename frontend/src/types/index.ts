export interface Clip {
  filename: string;
  path: string;
  size: number;
  created_at: string;
  resolution_preset: string | null;
  duration: number | null;
  snapshots: string[];
}

export type Session = Clip[];

export interface ConfigField {
  key: string;
  label: string;
  type: "int" | "float" | "bool";
  value: number | boolean | null;
}

export interface ConfigData {
  fields: ConfigField[];
  presets: string[];
  current_preset: string | null;
  timeout_hours: number | null;
}

export interface WifiStatus {
  mode: "hotspot" | "connected" | "disconnected";
  ssid?: string;
}

export type BotState = "IDLE" | "RECORDING" | "SAVING" | "unknown";
