"use client";

import { useCallback, useState } from "react";

/**
 * Drag-and-drop file upload zone.
 *
 * @param {{ onFileSelect: (file: File) => void, accept: string, disabled: boolean }} props
 */
export default function DropZone({
  onFileSelect,
  accept = ".csv,.tsv,.txt,.xlsx,.xlsm,.xls,.pdf,.docx,.doc",
  disabled = false,
}) {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      if (disabled) return;

      const file = e.dataTransfer?.files?.[0];
      if (file) onFileSelect(file);
    },
    [onFileSelect, disabled]
  );

  const handleClick = useCallback(() => {
    if (disabled) return;
    const input = document.createElement("input");
    input.type = "file";
    input.accept = accept;
    input.onchange = (e) => {
      const file = e.target.files?.[0];
      if (file) onFileSelect(file);
    };
    input.click();
  }, [onFileSelect, accept, disabled]);

  return (
    <div
      onClick={handleClick}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`
        group relative cursor-pointer rounded-2xl border-2 border-dashed
        p-12 text-center transition-all duration-300
        ${isDragging
          ? "border-[var(--color-primary)] bg-[var(--color-primary)]/5 scale-[1.02]"
          : "border-[var(--color-border)] hover:border-[var(--color-border-light)] hover:bg-[var(--color-surface)]/50"
        }
        ${disabled ? "pointer-events-none opacity-50" : ""}
      `}
    >
      {/* Animated icon */}
      <div
        className={`
          mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-2xl
          transition-all duration-300
          ${isDragging
            ? "bg-[var(--color-primary)]/15 scale-110"
            : "bg-[var(--color-surface-2)] group-hover:bg-[var(--color-surface-3)]"
          }
        `}
      >
        <svg
          className={`h-9 w-9 transition-colors duration-300 ${
            isDragging ? "text-[var(--color-primary)]" : "text-[var(--color-text-muted)]"
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.5}
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
          />
        </svg>
      </div>

      <p className="text-lg font-medium text-[var(--color-text)]">
        {isDragging ? "Drop your file here" : "Drag & drop your file here"}
      </p>
      <p className="mt-2 text-sm text-[var(--color-text-muted)]">
        or <span className="text-[var(--color-primary)] underline underline-offset-2">browse files</span>
      </p>
      <p className="mt-4 text-xs text-[var(--color-text-muted)]">
        Supports CSV, TSV, TXT, Excel, PDF, and Word (.docx, .doc) — Max 10 MB
      </p>
    </div>
  );
}
