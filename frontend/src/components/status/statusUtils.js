const STATUS_MAP = {
  ok: "healthy",
  green: "healthy",
  operational: "healthy",
  healthy: "healthy",
  up: "healthy",
  warning: "degraded",
  yellow: "degraded",
  monitoring: "degraded",
  degraded: "degraded",
  red: "critical",
  critical: "critical",
  down: "critical",
  outage: "critical"
};

const STATUS_RANK = {
  healthy: 0,
  unknown: 1,
  stale: 2,
  degraded: 3,
  critical: 4
};

export const STATUS_LABELS = {
  healthy: "Healthy",
  degraded: "Degraded",
  critical: "Critical",
  stale: "Stale",
  unknown: "Unknown",
  empty: "No data",
  loading: "Loading",
  error: "Unavailable"
};

export function normalizeState(state) {
  if (!state) {
    return "unknown";
  }
  const key = String(state).toLowerCase();
  return STATUS_MAP[key] || "unknown";
}

export function pickWorseState(left, right) {
  const leftRank = STATUS_RANK[left] ?? STATUS_RANK.unknown;
  const rightRank = STATUS_RANK[right] ?? STATUS_RANK.unknown;
  return rightRank > leftRank ? right : left;
}

export function isStaleCheck(check) {
  if (!check) {
    return false;
  }
  const freshness = Number(check.freshness_minutes);
  const sla = Number(check.sla_minutes);
  if (!Number.isFinite(freshness) || !Number.isFinite(sla)) {
    return false;
  }
  return freshness > sla;
}

export function buildCheckSummary(check) {
  const stale = isStaleCheck(check);
  const normalized = normalizeState(check?.state);
  return {
    ...check,
    derivedState: stale ? "stale" : normalized,
    isStale: stale
  };
}

function latestTimestamp(values) {
  return values.reduce((latest, value) => {
    if (!value) {
      return latest;
    }
    if (!latest || value > latest) {
      return value;
    }
    return latest;
  }, null);
}

function summarizeChecks(checkSummaries) {
  if (!checkSummaries.length) {
    return {
      note: "No checks reported yet.",
      state: "unknown",
      staleCount: 0
    };
  }

  let worstState = "healthy";
  for (const check of checkSummaries) {
    worstState = pickWorseState(worstState, check.derivedState);
  }

  const staleCount = checkSummaries.filter((check) => check.isStale).length;

  const sortedBySeverity = [...checkSummaries].sort(
    (a, b) => (STATUS_RANK[b.derivedState] ?? 0) - (STATUS_RANK[a.derivedState] ?? 0)
  );
  const focus = sortedBySeverity[0];
  const state = staleCount > 0 ? pickWorseState(worstState, "stale") : worstState;
  if (staleCount > 0 && worstState === "healthy") {
    return {
      note: `${staleCount} check${staleCount === 1 ? "" : "s"} beyond freshness SLA.`,
      state,
      staleCount
    };
  }

  if (focus?.message) {
    return {
      note: focus.message,
      state,
      staleCount
    };
  }

  return {
    note: worstState === "healthy" ? "All checks within SLA." : "Monitoring platform signals.",
    state,
    staleCount
  };
}

function latestByKey(items, key) {
  return items.reduce((latest, item) => {
    if (!item || !item[key]) {
      return latest;
    }
    if (!latest || item[key] > latest[key]) {
      return item;
    }
    return latest;
  }, null);
}

export function buildPlatformSummaries(platforms = [], checks = [], results = []) {
  return platforms.map((platform) => {
    const platformChecks = checks.filter((check) => check.platform_id === platform.id);
    const checkSummaries = platformChecks
      .map(buildCheckSummary)
      .sort((a, b) => (b.checked_at || "").localeCompare(a.checked_at || ""));
    const platformResults = results.filter((result) => result.platform_id === platform.id);
    const latestResult = latestByKey(platformResults, "created_at");
    const resultState = latestResult ? normalizeState(latestResult.state) : null;
    const checkSummary = summarizeChecks(checkSummaries);
    const lastCheckedAt = latestTimestamp([
      latestTimestamp(checkSummaries.map((check) => check.checked_at)),
      latestResult?.created_at,
      platform.updated_at
    ]);

    let state = checkSummary.state;
    if (checkSummaries.length === 0 && resultState) {
      state = resultState;
    }

    return {
      platform,
      state,
      statusNote: checkSummary.note,
      lastCheckedAt,
      checkCount: checkSummaries.length,
      staleCount: checkSummary.staleCount,
      checks: checkSummaries,
      latestResult
    };
  });
}

export function buildDashboardSummary(platformSummaries = [], checks = [], results = [], dataState) {
  if (dataState === "loading") {
    return {
      state: "loading",
      counts: {},
      platformCount: 0,
      staleChecks: 0,
      lastUpdated: null
    };
  }

  if (dataState === "error") {
    return {
      state: "error",
      counts: {},
      platformCount: 0,
      staleChecks: 0,
      lastUpdated: null
    };
  }

  if (!platformSummaries.length) {
    return {
      state: "empty",
      counts: {},
      platformCount: 0,
      staleChecks: 0,
      lastUpdated: null
    };
  }

  const counts = {
    healthy: 0,
    degraded: 0,
    critical: 0,
    stale: 0,
    unknown: 0
  };

  let state = "healthy";
  let lastUpdated = null;
  for (const summary of platformSummaries) {
    const key = summary.state || "unknown";
    counts[key] = (counts[key] || 0) + 1;
    state = pickWorseState(state, key);
    if (summary.lastCheckedAt && (!lastUpdated || summary.lastCheckedAt > lastUpdated)) {
      lastUpdated = summary.lastCheckedAt;
    }
  }

  const resultUpdated = latestTimestamp(results.map((result) => result.created_at));
  lastUpdated = latestTimestamp([lastUpdated, resultUpdated]);

  return {
    state,
    counts,
    platformCount: platformSummaries.length,
    staleChecks: checks.filter((check) => isStaleCheck(check)).length,
    lastUpdated
  };
}

export function formatTimestamp(value) {
  if (!value || typeof value !== "string") {
    return "Not available";
  }
  if (value.includes("T")) {
    return value.replace("T", " ").replace("Z", " UTC");
  }
  return value;
}

export function formatDateRange(startAt, endAt) {
  if (!startAt && !endAt) {
    return null;
  }
  if (startAt && endAt) {
    return `${formatTimestamp(startAt)} - ${formatTimestamp(endAt)}`;
  }
  if (startAt) {
    return `Starts ${formatTimestamp(startAt)}`;
  }
  return `Ends ${formatTimestamp(endAt)}`;
}

export function filterPublishedMessages(messages = []) {
  return messages.filter((message) => message?.state === "published");
}
