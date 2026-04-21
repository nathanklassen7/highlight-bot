import { postBotAction } from "../../api/bot";
import type { BotState } from "../../types";

interface BotControlsProps {
  state: BotState;
  onAction: () => void;
}

export function BotControls({ state, onAction }: BotControlsProps) {
  const isIdle = state === "IDLE";
  const isRecording = state === "RECORDING";

  async function handleAction(action: "start" | "stop" | "clip" | "poke") {
    await postBotAction(action);
    setTimeout(onAction, 500);
  }

  return (
    <div className="grid gap-4">
      {isIdle && (
        <button
          onClick={() => handleAction("start")}
          className="p-4 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700"
        >
          Start Recording
        </button>
      )}
      {isRecording && (
        <>
          <button
            onClick={() => handleAction("clip")}
            className="p-4 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700"
          >
            Save Clip
          </button>
          <button
            onClick={() => handleAction("stop")}
            className="p-4 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700"
          >
            Stop Recording
          </button>
          <button
            onClick={() => handleAction("poke")}
            className="p-4 bg-yellow-500 text-white rounded-lg font-semibold hover:bg-yellow-600"
          >
            Poke (Refresh Buffers)
          </button>
        </>
      )}
    </div>
  );
}
