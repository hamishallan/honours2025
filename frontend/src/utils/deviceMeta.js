export function parseDeviceMeta(str = "") {
  const out = { deviceName: "", gain: null, avg: null, msg: null };
  if (!str) return out;

  const gain = str.match(/(?:^|_)Gain-([^_]+)/i)?.[1] ?? null;
  const avg  = str.match(/(?:^|_)Avg-([^_]+)/i)?.[1] ?? null;
  const msg  = str.match(/'([^']*)'/)?.[1] ?? null;
  const deviceName = (str.match(/^(.*?)(?:_Gain-|_Avg-|$)/i)?.[1] ?? str).trim();

  return { deviceName, gain, avg, msg };
}
