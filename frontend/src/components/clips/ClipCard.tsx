import { useState } from "react";
import { Link } from "react-router-dom";
import { ThumbnailCycler } from "./ThumbnailCycler";
import { deleteClip, shareClipFile } from "../../api/clips";
import type { Clip } from "../../types";

interface ClipCardProps {
  clip: Clip;
  onDeleted: () => void;
}

export function ClipCard({ clip, onDeleted }: ClipCardProps) {
  const [sharing, setSharing] = useState(false);
  const label = clip.created_at
    ? clip.created_at.slice(0, 19).replace("T", " ")
    : clip.filename;
  const sizeMB = (clip.size / 1024 / 1024).toFixed(2);

  async function handleShare() {
    setSharing(true);
    try {
      await shareClipFile(clip.filename);
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
    if (!confirm(`Delete clip from ${label}?`)) return;
    const data = await deleteClip(clip.filename);
    if (data.status === "ok") {
      onDeleted();
    } else {
      alert("Error: " + (data.error ?? "Unknown error"));
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden transition-transform hover:-translate-y-0.5">
      <Link to={`/clips/view/${clip.filename}`}>
        <ThumbnailCycler snapshots={clip.snapshots} />
      </Link>
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 truncate">
          <Link
            to={`/clips/view/${clip.filename}`}
            className="hover:text-blue-600"
          >
            {label}
          </Link>
        </h3>
        <p className="text-sm text-gray-500">Size: {sizeMB} MB</p>
        <div className="mt-4 flex flex-wrap gap-2">
          <Link
            to={`/clips/view/${clip.filename}`}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
          >
            View
          </Link>
          <a
            href={`/clips/file/${clip.filename}`}
            download
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
          >
            Download
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
      </div>
    </div>
  );
}
