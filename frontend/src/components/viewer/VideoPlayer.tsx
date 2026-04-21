import { forwardRef } from "react";

interface VideoPlayerProps {
  filename: string;
}

export const VideoPlayer = forwardRef<HTMLVideoElement, VideoPlayerProps>(
  function VideoPlayer({ filename }, ref) {
    return (
      <div className="relative w-full pt-[56.25%]">
        <video
          ref={ref}
          controls
          playsInline
          className="absolute top-0 left-0 w-full h-full object-contain bg-black"
        >
          <source src={`/clips/file/${filename}`} type="video/mp4" />
        </video>
      </div>
    );
  },
);
