import { enableHotspot as apiEnableHotspot } from "../../api/wifi";
import type { WifiStatus as WifiStatusType } from "../../types";

interface WifiStatusProps {
  status: WifiStatusType | null;
}

export function WifiStatusDisplay({ status }: WifiStatusProps) {
  async function handleHotspot() {
    if (!confirm("Switch to hotspot mode? You will lose WiFi internet."))
      return;
    try {
      await apiEnableHotspot();
    } catch {
      /* ignore */
    }
    alert(
      "Switching to hotspot. Reconnect to HighlightBot WiFi to access this page.",
    );
  }

  let statusContent: React.ReactNode = "Checking...";
  let showHotspotBtn = false;

  if (status) {
    if (status.mode === "hotspot") {
      statusContent = (
        <span className="text-yellow-600">Hotspot (HighlightBot)</span>
      );
    } else if (status.mode === "connected") {
      statusContent = (
        <span className="text-green-600">Connected to {status.ssid}</span>
      );
      showHotspotBtn = true;
    } else {
      statusContent = <span className="text-red-600">Disconnected</span>;
      showHotspotBtn = true;
    }
  }

  return (
    <div className="mb-6 p-4 bg-white rounded-lg shadow-sm">
      <div className="flex justify-between items-center">
        <div>
          <span className="text-sm text-gray-500">Status:</span>
          <span className="ml-1 font-medium">{statusContent}</span>
        </div>
        {showHotspotBtn && (
          <button
            onClick={handleHotspot}
            className="px-3 py-1.5 text-sm bg-yellow-500 text-white rounded hover:bg-yellow-600"
          >
            Switch to Hotspot
          </button>
        )}
      </div>
    </div>
  );
}
