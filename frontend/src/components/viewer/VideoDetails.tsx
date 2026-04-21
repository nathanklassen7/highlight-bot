interface VideoDetailsProps {
  filename: string;
  size: number;
  recorded: string;
  resolution: string | null;
  resolutionPreset: string | null;
  fps: number | null;
  duration: number | null;
}

export function VideoDetails({
  filename,
  size,
  recorded,
  resolution,
  resolutionPreset,
  fps,
  duration,
}: VideoDetailsProps) {
  const sizeMB = (size / 1024 / 1024).toFixed(2);

  return (
    <div>
      <h2 className="text-lg font-semibold text-gray-900 mb-4">
        Video Details
      </h2>
      <dl className="space-y-2">
        <div>
          <dt className="text-sm font-medium text-gray-500">File Name</dt>
          <dd className="mt-1 text-sm text-gray-900">{filename}</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">File Size</dt>
          <dd className="mt-1 text-sm text-gray-900">{sizeMB} MB</dd>
        </div>
        <div>
          <dt className="text-sm font-medium text-gray-500">Recorded</dt>
          <dd className="mt-1 text-sm text-gray-900">
            {recorded.slice(0, 19).replace("T", " ")}
          </dd>
        </div>
        {resolution && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Resolution</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {resolution}
              {resolutionPreset ? ` (${resolutionPreset})` : ""}
            </dd>
          </div>
        )}
        {fps != null && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Frame Rate</dt>
            <dd className="mt-1 text-sm text-gray-900">{fps} fps</dd>
          </div>
        )}
        {duration != null && (
          <div>
            <dt className="text-sm font-medium text-gray-500">Duration</dt>
            <dd className="mt-1 text-sm text-gray-900">
              {duration.toFixed(1)}s
            </dd>
          </div>
        )}
      </dl>
    </div>
  );
}
