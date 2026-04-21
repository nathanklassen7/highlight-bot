import { useState } from "react";
import { connectWifi } from "../../api/wifi";

export function ConnectForm() {
  const [ssid, setSsid] = useState("");
  const [password, setPassword] = useState("");
  const [connecting, setConnecting] = useState(false);

  async function handleConnect() {
    if (!ssid.trim()) {
      alert("Enter a network name");
      return;
    }
    setConnecting(true);
    try {
      await connectWifi(ssid.trim(), password);
    } catch {
      /* ignore */
    }
    alert(
      "Connection attempt sent. This page will become unreachable while the bot switches networks.\n\nIf it fails, the hotspot will reopen automatically.",
    );
    setConnecting(false);
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6">
      <div className="p-4">
        <h2 className="text-lg font-semibold mb-3">Connect to WiFi</h2>
        <div className="space-y-3">
          <input
            type="text"
            placeholder="Network name (SSID)"
            value={ssid}
            onChange={(e) => setSsid(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            type="password"
            placeholder="Password (leave blank if open)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button
            onClick={handleConnect}
            disabled={connecting}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {connecting ? "Connecting..." : "Connect"}
          </button>
          <p className="text-xs text-gray-500 text-center">
            If connection fails, the hotspot will reopen automatically.
          </p>
        </div>
      </div>
    </div>
  );
}
