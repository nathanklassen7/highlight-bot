import { useEffect, useState, useCallback } from "react";
import { Header } from "../components/layout/Header";
import { PageLayout } from "../components/layout/PageLayout";
import { SnapshotPreview } from "../components/config/SnapshotPreview";
import { PresetSelector } from "../components/config/PresetSelector";
import { ConfigField } from "../components/config/ConfigField";
import { TimeoutSetting } from "../components/config/TimeoutSetting";
import { useToast } from "../components/shared/Toast";
import { getConfig, resetConfig as apiResetConfig } from "../api/config";
import { getBotStatus } from "../api/bot";
import { usePolling } from "../hooks/usePolling";
import type { ConfigData } from "../types";

export function ConfigPage() {
  const [config, setConfig] = useState<ConfigData | null>(null);
  const [isIdle, setIsIdle] = useState(true);
  const { showSuccess, showError } = useToast();

  const loadConfig = useCallback(async () => {
    try {
      setConfig(await getConfig());
    } catch {
      showError("Failed to load config");
    }
  }, [showError]);

  const checkStatus = useCallback(async () => {
    try {
      const state = await getBotStatus();
      setIsIdle(state === "IDLE");
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    loadConfig();
  }, [loadConfig]);

  usePolling(checkStatus, 2000);

  async function handleReset() {
    if (!confirm("Reset all config values to defaults?")) return;
    const data = await apiResetConfig();
    if (data.error) {
      showError(data.error);
    } else {
      showSuccess("Config reset");
      loadConfig();
    }
  }

  return (
    <>
      <Header title="Camera" backTo={{ label: "Home", path: "/" }} />
      <PageLayout>
        <div className="space-y-4">
          <SnapshotPreview />

          {!isIdle && (
            <div className="p-3 bg-yellow-100 text-yellow-800 rounded-lg text-sm font-medium text-center">
              Stop recording to edit camera config.
            </div>
          )}

          {config && (
            <>
              <PresetSelector
                presets={config.presets}
                currentPreset={config.current_preset}
                onChanged={loadConfig}
              />

              <div className="bg-white rounded-lg shadow-sm p-3 space-y-2">
                {config.fields.map((field) => (
                  <ConfigField
                    key={field.key}
                    field={field}
                    disabled={!isIdle}
                    onSaved={loadConfig}
                  />
                ))}
              </div>

              <button
                onClick={handleReset}
                disabled={!isIdle}
                className="w-full p-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Reset to Defaults
              </button>

              <TimeoutSetting
                timeoutHours={config.timeout_hours}
                onSaved={loadConfig}
              />
            </>
          )}
        </div>
      </PageLayout>
    </>
  );
}
