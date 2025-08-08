export function parseDeviceMeta(str = "") {
  const out = { deviceName: "", gain: null, apo: null, avg: null, msg: null };
  if (!str) return out;

  const gain = str.match(/(?:^|_)Gain-([^_]+)/i);
  const apo  = str.match(/(?:^|_)Apo-([^_]+)/i);
  const avg  = str.match(/(?:^|_)Avg-([^_]+)/i);
  const msg  = str.match(/'([^']*)'/); // contents inside single quotes

  const deviceNameMatch = str.match(/^(.*?)(?:_Gain-|_Apo-|_Avg-|$)/i);

  out.deviceName = deviceNameMatch ? deviceNameMatch[1] : str;
  out.gain = gain?.[1] ?? null;
  out.apo  = apo?.[1] ?? null;
  out.avg  = avg?.[1] ?? null;
  out.msg  = msg?.[1] ?? null;
  return out;
}
