import { applyPreset } from "../../api/config";
import { useToast } from "../shared/Toast";

interface PresetSelectorProps {
  presets: string[];
  currentPreset: string | null;
  onChanged: () => void;
}

export function PresetSelector({
  presets,
  currentPreset,
  onChanged,
}: PresetSelectorProps) {
  const { showSuccess, showError } = useToast();

  async function handleApply(name: string) {
    const data = await applyPreset(name);
    if (data.error) {
      showError(data.error);
    } else {
      showSuccess(`Preset: ${name}`);
      onChanged();
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-3">
      <h2 className="font-semibold text-gray-900 mb-2 text-sm">Preset</h2>
      <div className="grid grid-cols-3 gap-1.5">
        {presets.map((name) => {
          const active = name === currentPreset;
          return (
            <button
              key={name}
              onClick={() => handleApply(name)}
              disabled={active}
              className={`p-2 rounded text-xs font-semibold ${
                active
                  ? "text-white bg-blue-600"
                  : "text-gray-700 bg-gray-100 hover:bg-gray-200 cursor-pointer"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {name}
            </button>
          );
        })}
      </div>
    </div>
  );
}
