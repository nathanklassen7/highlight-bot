import type { BotState } from "../../types";

const STATE_COLORS: Record<string, string> = {
  IDLE: "bg-gray-400",
  RECORDING: "bg-red-500 pulse",
  SAVING: "bg-yellow-500 pulse",
};

const STATE_LABELS: Record<string, string> = {
  IDLE: "Idle",
  RECORDING: "Recording",
  SAVING: "Saving clip...",
};

interface StatusIndicatorProps {
  state: BotState;
}

export function StatusIndicator({ state }: StatusIndicatorProps) {
  const colorClass = STATE_COLORS[state] ?? "bg-gray-400";
  const label = STATE_LABELS[state] ?? state;

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 text-center">
      <div
        className={`inline-block w-4 h-4 rounded-full mb-3 ${colorClass}`}
      />
      <p className="text-lg font-semibold">{label}</p>
    </div>
  );
}
