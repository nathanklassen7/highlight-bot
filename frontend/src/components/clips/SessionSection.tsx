import { ClipCard } from "./ClipCard";
import type { Session } from "../../types";

interface SessionSectionProps {
  session: Session;
  index: number;
  onClipDeleted: () => void;
}

export function SessionSection({
  session,
  index,
  onClipDeleted,
}: SessionSectionProps) {
  return (
    <div>
      <div className="bg-gray-100 p-4 my-4 rounded-lg border-l-4 border-blue-500">
        <h2 className="text-xl font-semibold text-gray-900">
          Session {index + 1}
        </h2>
        <p className="text-sm text-gray-500">
          {session.length} clip{session.length !== 1 ? "s" : ""}
        </p>
      </div>
      <div className="grid grid-cols-[repeat(auto-fill,minmax(300px,1fr))] gap-4 px-4">
        {session.map((clip) => (
          <ClipCard
            key={clip.filename}
            clip={clip}
            onDeleted={onClipDeleted}
          />
        ))}
      </div>
    </div>
  );
}
