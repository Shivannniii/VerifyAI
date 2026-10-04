import { useState } from "react";
import { ChevronDown, ExternalLink, Loader2, Search } from "lucide-react";
import StatusBadge from "./StatusBadge";
import { isChecked, verdictInfo } from "../verdicts";

function sourceHref(url) {
  if (!url) return null;
  return /^https?:\/\//i.test(url) ? url : null;
}

// A horizontal gauge with ticks at 25 / 50 / 75 %.
function MatchGauge({ confidence, status }) {
  const percent = Math.round((confidence ?? 0) * 100);
  const fill = {
    potentially_supported: "bg-supported",
    partially_supported: "bg-partial",
    uncertain: "bg-uncertain",
  }[status];

  return (
    <div className="flex items-center gap-3">
      <div
        className="relative h-1.5 w-40 rounded-full bg-line"
        role="meter"
        aria-label="Evidence match"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={percent}
      >
        <div className={`h-full rounded-full ${fill}`} style={{ width: `${percent}%` }} />
        {[25, 50, 75].map((tick) => (
          <span
            key={tick}
            className="absolute top-[-2px] h-[10px] w-px bg-surface"
            style={{ left: `${tick}%` }}
          />
        ))}
      </div>
      <span className="text-xs text-muted">Evidence match {percent}%</span>
    </div>
  );
}

export default function ClaimCard({ claim, onVerify, busy, disabled }) {
  const [open, setOpen] = useState(false);

  const verification = claim.verification;
  const status = verification?.status ?? claim.status;
  const checked = isChecked(status);
  const sources = verification?.sources ?? [];
  const { stripe } = verdictInfo(status);

  return (
    <li className={`border-l-4 bg-surface py-4 pl-4 pr-3 ${stripe}`}>
      <div className="flex items-start justify-between gap-3">
        <p className="max-w-[68ch] text-[15px] leading-relaxed">{claim.claim_text}</p>
        <StatusBadge status={status} />
      </div>

      {checked && (
        <div className="mt-3 space-y-2">
          <MatchGauge confidence={verification?.confidence} status={status} />
          <p className="max-w-[68ch] text-sm text-muted">{verification?.explanation}</p>
        </div>
      )}

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button
          type="button"
          onClick={() => onVerify(claim.id)}
          disabled={busy || disabled}
          className="inline-flex items-center gap-1.5 rounded-md border border-line px-2.5 py-1.5 text-sm font-medium hover:bg-paper disabled:cursor-not-allowed disabled:opacity-50"
        >
          {busy ? (
            <Loader2 size={14} className="animate-spin motion-reduce:animate-none" aria-hidden="true" />
          ) : (
            <Search size={14} aria-hidden="true" />
          )}
          {busy ? "Checking..." : checked ? "Check again" : "Check this claim"}
        </button>

        {checked && (
          <button
            type="button"
            onClick={() => setOpen((value) => !value)}
            aria-expanded={open}
            className="inline-flex items-center gap-1 text-sm text-brand hover:underline"
          >
            {sources.length === 0
              ? "No matching sources"
              : `${sources.length} source${sources.length === 1 ? "" : "s"}`}
            {sources.length > 0 && (
              <ChevronDown
                size={14}
                className={open ? "rotate-180" : ""}
                aria-hidden="true"
              />
            )}
          </button>
        )}
      </div>

      {open && sources.length > 0 && (
        <ul className="mt-3 space-y-3 border-t border-line pt-3">
          {sources.map((source, index) => {
            const href = sourceHref(source.url);
            const meta = [
              source.source_name,
              source.publication_year,
              source.cited_by_count != null ? `${source.cited_by_count} citations` : null,
              source.relevance != null ? `wording overlap ${Math.round(source.relevance * 100)}%` : null,
            ]
              .filter(Boolean)
              .join(", ");

            return (
              <li key={`${source.url ?? "source"}-${index}`} className="text-sm">
                {href ? (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-start gap-1 font-medium text-brand hover:underline"
                  >
                    {source.title || href}
                    <ExternalLink size={13} className="mt-1 shrink-0" aria-hidden="true" />
                  </a>
                ) : (
                  <span className="font-medium">{source.title || "Untitled source"}</span>
                )}
                {meta && <p className="text-xs text-muted">{meta}</p>}
                {source.snippet && (
                  <p className="mt-1 line-clamp-3 max-w-[68ch] text-muted">{source.snippet}</p>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </li>
  );
}
