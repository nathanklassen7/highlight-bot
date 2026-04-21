import { Link } from "react-router-dom";
import type { Session } from "../../types";

interface OtherClipsProps {
  session: Session;
  currentFilename: string;
}

export function OtherClips({ session, currentFilename }: OtherClipsProps) {
  const others = session.filter((c) => c.filename !== currentFilename);
  if (others.length === 0) return null;

  return (
    <div className="mt-8">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Other Clips in This Session
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {others.map((clip) => (
          <Link
            key={clip.filename}
            to={`/clips/view/${clip.filename}`}
            className="block"
          >
            <div className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition">
              <p className="text-sm font-medium text-gray-900 truncate">
                {clip.filename}
              </p>
              <p className="text-xs text-gray-500">
                {(clip.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
