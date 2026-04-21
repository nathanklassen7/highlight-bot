import type { Session } from "../types";

export async function getSessions(): Promise<Session[]> {
  const res = await fetch("/api/clips");
  return res.json();
}

export async function deleteClip(
  filename: string,
): Promise<{ status?: string; error?: string }> {
  const res = await fetch(`/api/clips/${filename}`, { method: "DELETE" });
  return res.json();
}

export async function trimClip(
  filename: string,
  startTime: number,
  endTime: number,
): Promise<{ download_url?: string; error?: string }> {
  const res = await fetch(`/trim/${filename}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ start_time: startTime, end_time: endTime }),
  });
  return res.json();
}

export async function shareClipFile(filename: string): Promise<void> {
  const res = await fetch(`/clips/file/${filename}`);
  const blob = await res.blob();
  const file = new File([blob], filename, { type: "video/mp4" });
  if (navigator.share) {
    await navigator.share({ files: [file] });
  } else {
    throw new Error("unsupported");
  }
}
