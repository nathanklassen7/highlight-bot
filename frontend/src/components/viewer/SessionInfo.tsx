interface SessionInfoProps {
  sessionIndex: number;
  clipCount: number;
}

export function SessionInfo({ sessionIndex, clipCount }: SessionInfoProps) {
  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Session Information
      </h2>
      <dl className="space-y-2">
        <div>
          <dt className="text-sm font-medium text-gray-500">Session Number</dt>
          <dd className="mt-1 text-sm text-gray-900">
            Session {sessionIndex + 1}
          </dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">
            Clips in Session
          </dt>
          <dd className="mt-1 text-sm text-gray-900">
            {clipCount} clip{clipCount !== 1 ? "s" : ""}
          </dd>
        </div>
      </dl>
    </div>
  );
}
