import { useState, useEffect } from "react";
import { updateTimeout } from "../../api/config";
import { useToast } from "../shared/Toast";

interface TimeoutSettingProps {
  timeoutHours: number | null;
  onSaved: () => void;
}

export function TimeoutSetting({
  timeoutHours,
  onSaved,
}: TimeoutSettingProps) {
  const [value, setValue] = useState("");
  const { showSuccess, showError } = useToast();

  useEffect(() => {
    if (timeoutHours !== null) {
      setValue(String(timeoutHours));
    }
  }, [timeoutHours]);

  async function handleSave() {
    const data = await updateTimeout(value);
    if (data.error) {
      showError(data.error);
    } else {
      showSuccess("Timeout saved");
      onSaved();
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-3">
      <div className="flex items-center gap-2">
        <label className="flex-1 text-sm font-medium text-gray-700 whitespace-nowrap">
          Timeout (hours)
        </label>
        <input
          type="number"
          step="any"
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-28 px-2 py-1.5 border border-gray-300 rounded-md text-base"
        />
        <button
          onClick={handleSave}
          className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          Save
        </button>
      </div>
    </div>
  );
}
