import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { deleteClip, shareClipFile } from "../../api/clips";

interface ClipActionsProps {
  filename: string;
}

export function ClipActions({ filename }: ClipActionsProps) {
  const navigate = useNavigate();
  const [sharing, setSharing] = useState(false);

  async function handleShare() {
    setSharing(true);
    try {
      await shareClipFile(filename);
    } catch (e: unknown) {
      if (e instanceof Error && e.name !== "AbortError") {
        alert(
          'Sharing not available over HTTP. To save to Camera Roll, long-press the video and tap "Save to Photos".',
        );
      }
    } finally {
      setSharing(false);
    }
  }

  async function handleDelete() {
    if (!confirm(`Delete ${filename}?`)) return;
    const data = await deleteClip(filename);
    if (data.status === "ok") {
      navigate("/clips");
    } else {
      alert("Error: " + (data.error ?? "Unknown error"));
    }
  }

  return (
    <div className="mt-6 flex flex-wrap gap-2">
      <a
        href={`/clips/file/${filename}`}
        download
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
      >
        Download Original
      </a>
      <button
        onClick={handleShare}
        disabled={sharing}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
      >
        {sharing ? "Preparing..." : "Share"}
      </button>
      <button
        onClick={handleDelete}
        className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
      >
        Delete
      </button>
    </div>
  );
}
