import { useEffect, useState } from "react";
import socket from "../api/socket";
import { getSessions } from "../api/clips";
import type { Session } from "../types";

export function useClipsSocket() {
  const [sessions, setSessions] = useState<Session[]>([]);

  useEffect(() => {
    getSessions().then(setSessions);

    function onUpdate(data: string) {
      setSessions(JSON.parse(data));
    }

    socket.on("clips_update", onUpdate);
    return () => {
      socket.off("clips_update", onUpdate);
    };
  }, []);

  return { sessions, setSessions };
}
