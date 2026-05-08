"use client";

/**
 * Animated progress bar with status message.
 *
 * @param {{ status: "idle"|"uploading"|"processing"|"done"|"error", message: string }} props
 */
export default function UploadProgress({ status, message }) {
  if (status === "idle") return null;

  const colors = {
    uploading: "var(--color-primary)",
    processing: "var(--color-accent)",
    done: "var(--color-success)",
    error: "var(--color-danger)",
  };

  const color = colors[status] || colors.uploading;
  const isAnimating = status === "uploading" || status === "processing";

  return (
    <div className="space-y-3">
      {/* Progress bar */}
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--color-surface-2)]">
        <div
          className="h-full rounded-full transition-all duration-500 ease-out"
          style={{
            backgroundColor: color,
            width: status === "done" ? "100%" : status === "error" ? "100%" : "70%",
            animation: isAnimating ? "progress-pulse 2s ease-in-out infinite" : "none",
          }}
        />
      </div>

      {/* Status message */}
      <div className="flex items-center gap-2">
        {isAnimating && (
          <svg className="h-4 w-4 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
            />
          </svg>
        )}
        {status === "done" && (
          <svg className="h-4 w-4 text-[var(--color-success)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        )}
        {status === "error" && (
          <svg className="h-4 w-4 text-[var(--color-danger)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
          </svg>
        )}
        <span
          className="text-sm"
          style={{ color: status === "error" ? "var(--color-danger)" : "var(--color-text-secondary)" }}
        >
          {message}
        </span>
      </div>

      <style jsx>{`
        @keyframes progress-pulse {
          0%, 100% { opacity: 1; width: 40%; }
          50% { opacity: 0.8; width: 80%; }
        }
      `}</style>
    </div>
  );
}
