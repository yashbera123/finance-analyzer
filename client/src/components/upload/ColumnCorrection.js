"use client";

import { useState, useCallback } from "react";
import { motion } from "framer-motion";
import UploadProgress from "@/components/upload/UploadProgress";

const COLUMN_TYPES = [
  { field: "date_column", label: "Date" },
  { field: "description_column", label: "Description" },
  { field: "amount_column", label: "Amount" },
  { field: "debit_column", label: "Debit" },
  { field: "credit_column", label: "Credit" },
  { field: "type_column", label: "Type" },
];

function getInitialMappings(columnMapping = {}) {
  return COLUMN_TYPES.reduce((acc, type) => {
    acc[type.field] = columnMapping[type.field] || "";
    return acc;
  }, {});
}

export default function ColumnCorrection({
  correctionData,
  onCorrect,
  onCancel,
  status = "correction",
  message = "",
}) {
  const [mappings, setMappings] = useState(() =>
    getInitialMappings(correctionData.column_mapping)
  );

  const handleMappingChange = useCallback((field, column) => {
    setMappings(prev => ({
      ...prev,
      [field]: column,
    }));
  }, []);

  const handleSubmit = useCallback(() => {
    const normalizedMappings = Object.fromEntries(
      Object.entries(mappings).map(([field, column]) => [
        field,
        column || null,
      ])
    );
    onCorrect(normalizedMappings);
  }, [mappings, onCorrect]);

  const canSubmit = Boolean(
    mappings.date_column &&
    mappings.description_column &&
    (mappings.amount_column || mappings.debit_column || mappings.credit_column)
  );
  const isProcessing = status === "processing";
  const showProgress = ["processing", "done", "error"].includes(status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card space-y-6 p-8"
    >
      <div className="text-center">
        <h3 className="text-xl font-semibold mb-2">Confirm Column Mappings</h3>
        <p className="text-sm text-[var(--color-text-secondary)]">
          We detected the following columns. Please map them to the correct data types.
        </p>
      </div>

      {/* Sample Data Preview */}
      <div className="space-y-4">
        <h4 className="font-medium">Sample Data:</h4>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)]">
                {correctionData.detected_columns.map(col => (
                  <th key={col} className="text-left p-2 font-medium">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {correctionData.sample_data.slice(0, 3).map((row, idx) => (
                <tr key={idx} className="border-b border-[var(--color-border)]">
                  {correctionData.detected_columns.map(col => (
                    <td key={col} className="p-2 text-[var(--color-text-secondary)]">
                      {row[col] || ""}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Column Mappings */}
      <div className="space-y-4">
        <h4 className="font-medium">Column Mappings:</h4>
        <div className="grid gap-4">
          {COLUMN_TYPES.map(type => (
            <div key={type.field} className="flex items-center gap-4">
              <label className="w-24 text-sm font-medium">
                {type.label}:
              </label>
              <select
                value={mappings[type.field] || ""}
                onChange={(e) => handleMappingChange(type.field, e.target.value)}
                disabled={isProcessing}
                className="flex-1 px-3 py-2 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-md text-sm"
              >
                <option value="">Select column...</option>
                {correctionData.detected_columns.map(col => (
                  <option key={col} value={col}>
                    {col}
                  </option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      {showProgress && <UploadProgress status={status} message={message} />}

      {/* Actions */}
      <div className="flex gap-4 pt-4">
        <button
          onClick={onCancel}
          disabled={isProcessing}
          className="flex-1 px-4 py-2 text-sm font-medium text-[var(--color-text-secondary)] bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-md hover:bg-[var(--color-bg-hover)] transition-colors"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          disabled={!canSubmit || isProcessing}
          className={`flex-1 px-4 py-2 text-sm font-medium text-white bg-[var(--color-primary)] rounded-md transition-colors ${
            canSubmit && !isProcessing
              ? "hover:bg-[var(--color-primary-hover)]"
              : "cursor-not-allowed opacity-60"
          }`}
        >
          {isProcessing ? "Analyzing..." : "Continue with Analysis"}
        </button>
      </div>
    </motion.div>
  );
}
