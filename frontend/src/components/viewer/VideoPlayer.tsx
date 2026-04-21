import { forwardRef } from "react";

interface VideoPlayerProps {
  filename: string;
}

export const VideoPlayer = forwardRef<HTMLVideoElement, VideoPlayerProps>(
  function VideoPlayer({ filename }, ref) {
    return (
      <div
        className="relative w-full pt-[56.25%] bg-black select-none"
        style={{ WebkitTouchCallout: "none", WebkitUserSelect: "none" }}
      >
        <video
          ref={ref}
          controls
          playsInline
          preload="auto"
          {...{ "webkit-playsinline": "true" }}
          className="absolute top-0 left-0 w-full h-full object-contain bg-black"
          style={{ WebkitTouchCallout: "default" }}
        >
          <source src={`/clips/file/${filename}`} type="video/mp4" />
        </video>
      </div>
    );
  },
);
