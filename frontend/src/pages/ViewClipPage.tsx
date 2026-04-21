import { useEffect, useState, useRef } from "react";
import { useParams } from "react-router-dom";
import { Header } from "../components/layout/Header";
import { VideoPlayer } from "../components/viewer/VideoPlayer";
import { TrimControls } from "../components/viewer/TrimControls";
import { VideoDetails } from "../components/viewer/VideoDetails";
import { SessionInfo } from "../components/viewer/SessionInfo";
import { ClipActions } from "../components/viewer/ClipActions";
import { OtherClips } from "../components/viewer/OtherClips";
import { getSessions } from "../api/clips";
import type { Session } from "../types";

interface ClipMeta {
  filename: string;
  size: number;
  created_at: string;
  resolution_preset: string | null;
  duration: number | null;
}

export function ViewClipPage() {
  const { "*": filename } = useParams();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [clip, setClip] = useState<ClipMeta | null>(null);
  const [session, setSession] = useState<Session | null>(null);
  const [sessionIndex, setSessionIndex] = useState(0);

  useEffect(() => {
    if (!filename) return;
    getSessions().then((sessions) => {
      for (let i = 0; i < sessions.length; i++) {
        const found = sessions[i].find((c) => c.filename === filename);
        if (found) {
          setClip(found);
          setSession(sessions[i]);
          setSessionIndex(i);
          return;
        }
      }
    });
  }, [filename]);

  if (!filename) return <p>Not found</p>;

  return (
    <>
      <Header
        title={filename}
        backTo={{ label: "Back to all clips", path: "/clips" }}
        maxWidth="max-w-7xl"
      />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <VideoPlayer ref={videoRef} filename={filename} />
          <div className="p-6">
            <TrimControls filename={filename} videoRef={videoRef} />
            {clip && (
              <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                <VideoDetails
                  filename={clip.filename}
                  size={clip.size}
                  recorded={clip.created_at}
                  resolution={null}
                  resolutionPreset={clip.resolution_preset}
                  fps={null}
                  duration={clip.duration}
                />
                {session && (
                  <SessionInfo
                    sessionIndex={sessionIndex}
                    clipCount={session.length}
                  />
                )}
              </div>
            )}
            <ClipActions filename={filename} />
            {session && (
              <OtherClips session={session} currentFilename={filename} />
            )}
          </div>
        </div>
      </main>
    </>
  );
}
