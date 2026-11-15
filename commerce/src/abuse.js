/**
 * Approximate per-Cloudflare-location safety cap, BEFORE payment/Stripe calls.
 * Cloudflare's ratelimit binding is intentionally fail-closed on protected
 * routes. A WAF rule is still necessary for network-level protection.
 */
export async function checkRateLimit(c, env, route) {
  const limiter = route === 'checkout' ? env.CHECKOUT_RATE_LIMITER : env.IP_RATE_LIMITER;
  const ip = c.req.header('cf-connecting-ip');
  // Only Cloudflare-controlled CF-Connecting-IP is used. X-Forwarded-For is
  // deliberately ignored because the caller may supply arbitrary values.
  if (!limiter || typeof limiter.limit !== 'function' ||
      !ip || ip.length > 64 || !/^[a-fA-F0-9:.]+$/.test(ip)) {
    return deny(c, 503, 'rate_limiter_unavailable');
  }
  try {
    const decision = await limiter.limit({ key: route + ':' + ip.toLowerCase() });
    if (!decision || decision.success !== true) {
      c.header('Retry-After', '60');
      return deny(c, 429, 'rate_limited');
    }
    return null;
  } catch {
    return deny(c, 503, 'rate_limiter_unavailable');
  }
}

function deny(c, status, error) {
  c.header('Cache-Control', 'no-store');
  c.header('X-Content-Type-Options', 'nosniff');
  return c.json({ error }, status);
}
