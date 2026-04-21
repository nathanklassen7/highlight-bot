import { useState } from "react";
import { updateConfigField } from "../../api/config";
import { useToast } from "../shared/Toast";
import type { ConfigField as ConfigFieldType } from "../../types";

interface ConfigFieldProps {
  field: ConfigFieldType;
  disabled: boolean;
  onSaved: () => void;
}

export function ConfigField({ field, disabled, onSaved }: ConfigFieldProps) {
  const [value, setValue] = useState(String(field.value ?? ""));
  const { showSuccess, showError } = useToast();

  async function handleSave() {
    const data = await updateConfigField(field.key, value);
    if (data.error) {
      showError(data.error);
    } else {
      showSuccess("Saved");
      onSaved();
    }
  }

  return (
    <div className="flex items-center gap-2">
      <label className="flex-1 text-sm font-medium text-gray-700 whitespace-nowrap">
        {field.label}
      </label>
      {field.type === "bool" ? (
        <select
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          className="w-28 px-2 py-1.5 border border-gray-300 rounded-md text-base disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          <option value="true">On</option>
          <option value="false">Off</option>
        </select>
      ) : (
        <input
          type="number"
          step={field.type === "float" ? "any" : "1"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={disabled}
          className="w-28 px-2 py-1.5 border border-gray-300 rounded-md text-base disabled:bg-gray-100 disabled:text-gray-400 disabled:cursor-not-allowed"
        />
      )}
      <button
        onClick={handleSave}
        disabled={disabled}
        className="px-3 py-1.5 text-xs bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Save
      </button>
    </div>
  );
}
