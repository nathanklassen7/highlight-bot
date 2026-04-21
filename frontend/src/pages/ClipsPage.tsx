import { useCallback } from "react";
import { Header } from "../components/layout/Header";
import { SessionSection } from "../components/clips/SessionSection";
import { useClipsSocket } from "../hooks/useClipsSocket";
import { getSessions } from "../api/clips";

export function ClipsPage() {
  const { sessions, setSessions } = useClipsSocket();

  const reload = useCallback(() => {
    getSessions().then(setSessions);
  }, [setSessions]);

  return (
    <>
      <Header
        title="Video Clips Browser"
        backTo={{ label: "Home", path: "/" }}
        maxWidth="max-w-7xl"
      />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {sessions.map((session, i) => (
          <SessionSection
            key={i}
            session={session}
            index={i}
            onClipDeleted={reload}
          />
        ))}
        {sessions.length === 0 && (
          <p className="text-center text-gray-500 py-12">No clips yet.</p>
        )}
      </main>
    </>
  );
}
