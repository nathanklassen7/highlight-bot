export async function getTemperature(): Promise<number | null> {
  try {
    const res = await fetch("/api/temperature");
    const data = await res.json();
    return data.temp ?? null;
  } catch {
    return null;
  }
}
