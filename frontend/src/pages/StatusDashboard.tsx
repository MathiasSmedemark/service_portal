import { useEffect, useMemo, useState } from "react";
import { apiFetch } from "../api/client";
import PlatformDetailPanel from "../components/status/PlatformDetailPanel.jsx";
import PlatformTile from "../components/status/PlatformTile.jsx";
import StatusBadge from "../components/status/StatusBadge.jsx";
import StatusMessageBanner from "../components/status/StatusMessageBanner.jsx";
import StatusSummary from "../components/status/StatusSummary.jsx";
import {
  buildDashboardSummary,
  buildPlatformSummaries,
  filterPublishedMessages
} from "../components/status/statusUtils.js";

const PLACEHOLDER_TILES = Array.from({ length: 3 }, (_, index) => index);

export default function StatusDashboard() {
  const [dataState, setDataState] = useState({
    state: "loading",
    error: null,
    platforms: [],
    checks: [],
    results: [],
    messages: []
  });
  const [selectedPlatformId, setSelectedPlatformId] = useState(null);

  useEffect(() => {
    let active = true;
    setDataState((prev) => ({ ...prev, state: "loading", error: null }));

    Promise.all([
      apiFetch("/platforms"),
      apiFetch("/status-checks"),
      apiFetch("/status-results"),
      apiFetch("/status-messages")
    ])
      .then(([platforms, checks, results, messages]) => {
        if (!active) {
          return;
        }
        setDataState({
          state: "ready",
          error: null,
          platforms: platforms?.items || [],
          checks: checks?.items || [],
          results: results?.items || [],
          messages: messages?.items || []
        });
      })
      .catch((error) => {
        if (!active) {
          return;
        }
        setDataState({
          state: "error",
          error: error?.message || "Unable to load status data.",
          platforms: [],
          checks: [],
          results: [],
          messages: []
        });
      });

    return () => {
      active = false;
    };
  }, []);

  const platformSummaries = useMemo(
    () =>
      buildPlatformSummaries(dataState.platforms, dataState.checks, dataState.results),
    [dataState.platforms, dataState.checks, dataState.results]
  );

  useEffect(() => {
    if (!selectedPlatformId) {
      return;
    }
    const exists = platformSummaries.some(
      (summary) => summary.platform.id === selectedPlatformId
    );
    if (!exists) {
      setSelectedPlatformId(null);
    }
  }, [platformSummaries, selectedPlatformId]);

  const dashboardSummary = useMemo(
    () =>
      buildDashboardSummary(
        platformSummaries,
        dataState.checks,
        dataState.results,
        dataState.state
      ),
    [platformSummaries, dataState.checks, dataState.results, dataState.state]
  );

  const summaryMetrics = useMemo(() => {
    if (["loading", "error"].includes(dashboardSummary.state)) {
      return [];
    }
    const counts = dashboardSummary.counts || {};
    const attention = (counts.degraded || 0) + (counts.critical || 0);
    return [
      { label: "Healthy", value: counts.healthy || 0 },
      { label: "Attention", value: attention },
      { label: "Stale signals", value: dashboardSummary.staleChecks || 0 },
      { label: "Unknown", value: counts.unknown || 0 }
    ];
  }, [dashboardSummary]);

  const publishedMessages = useMemo(
    () => filterPublishedMessages(dataState.messages),
    [dataState.messages]
  );

  const platformNameById = useMemo(() => {
    const map = new Map();
    dataState.platforms.forEach((platform) => {
      map.set(platform.id, platform.name);
    });
    return map;
  }, [dataState.platforms]);

  const bannerMessages = useMemo(() => {
    const globalMessages = publishedMessages.filter((message) => !message.platform_id);
    const platformMessages = selectedPlatformId
      ? publishedMessages.filter((message) => message.platform_id === selectedPlatformId)
      : [];
    return [...globalMessages, ...platformMessages]
      .slice(0, 3)
      .map((message) => ({
        ...message,
        scope: message.platform_id
          ? platformNameById.get(message.platform_id) || "Platform"
          : "Global"
      }));
  }, [publishedMessages, selectedPlatformId, platformNameById]);

  const selectedSummary = platformSummaries.find(
    (summary) => summary.platform.id === selectedPlatformId
  );
  const selectedMessages = selectedPlatformId
    ? publishedMessages.filter((message) => message.platform_id === selectedPlatformId)
    : [];

  const summaryWithError = {
    ...dashboardSummary,
    message: dataState.error || dashboardSummary.message
  };

  return (
    <section className="page status-dashboard">
      <div className="page-header">
        <div>
          <h1 className="page-title">Platform status</h1>
          <p className="page-subtitle">
            Global health, freshness, and platform signals in one view.
          </p>
        </div>
        <StatusBadge state={dashboardSummary.state} />
      </div>

      {dataState.state === "error" ? (
        <div className="status-error">{dataState.error}</div>
      ) : null}

      <div className="status-overview">
        <StatusSummary summary={summaryWithError} metrics={summaryMetrics} />
        <div className="status-sidecard">
          <h3>Drilldown tips</h3>
          <p className="page-subtitle">
            Pick a platform tile to see its latest checks, messages, and freshness
            details.
          </p>
          <div className="status-sidecard-row">
            <span>Platforms</span>
            <strong>{platformSummaries.length || 0}</strong>
          </div>
          <div className="status-sidecard-row">
            <span>Messages</span>
            <strong>{publishedMessages.length || 0}</strong>
          </div>
        </div>
      </div>

      <section className="status-section">
        <div className="status-section-header">
          <div>
            <h2>Message board</h2>
            <p className="page-subtitle">
              Global comms and platform-specific advisories.
            </p>
          </div>
        </div>
        <div className="status-banner-grid">
          {dataState.state === "loading" ? (
            PLACEHOLDER_TILES.map((index) => (
              <div key={`message-skeleton-${index}`} className="status-message skeleton" />
            ))
          ) : bannerMessages.length === 0 ? (
            <div className="status-empty">No active status messages.</div>
          ) : (
            bannerMessages.map((message) => (
              <StatusMessageBanner key={message.id} message={message} />
            ))
          )}
        </div>
      </section>

      <section className="status-section">
        <div className="status-section-header">
          <div>
            <h2>Platforms</h2>
            <p className="page-subtitle">
              Drill into each platform for live status checks and freshness.
            </p>
          </div>
        </div>
        <div className="platform-grid">
          {dataState.state === "loading"
            ? PLACEHOLDER_TILES.map((index) => (
                <div key={`tile-skeleton-${index}`} className="platform-tile skeleton" />
              ))
            : platformSummaries.length === 0
              ? (
                  <div className="status-empty">
                    No platforms have reported status signals yet.
                  </div>
                )
              : platformSummaries.map((summary) => (
                  <PlatformTile
                    key={summary.platform.id}
                    summary={summary}
                    isSelected={summary.platform.id === selectedPlatformId}
                    onSelect={setSelectedPlatformId}
                  />
                ))}
        </div>
      </section>

      <PlatformDetailPanel summary={selectedSummary} messages={selectedMessages} />
    </section>
  );
}
