"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import DropZone from "@/components/upload/DropZone";
import FilePreview from "@/components/upload/FilePreview";
import UploadProgress from "@/components/upload/UploadProgress";
import ColumnCorrection from "@/components/upload/ColumnCorrection";
import { uploadFile, correctColumns } from "@/lib/api";
import { useSession } from "@/components/SessionProvider";
import { FadeIn } from "@/components/ui/Motion";

const SUPPORTED_UPLOAD_EXTENSIONS = ["csv", "tsv", "txt", "xlsx", "xlsm", "xls", "pdf", "docx", "doc"];

export default function Home() {
  const router = useRouter();
  const { setSession } = useSession();
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState("");
  const [fileId, setFileId] = useState(null);
  const [correctionData, setCorrectionData] = useState(null);

  const handleFileSelect = useCallback((selectedFile) => {
    const ext = selectedFile.name.split(".").pop()?.toLowerCase();
    if (!SUPPORTED_UPLOAD_EXTENSIONS.includes(ext)) {
      setStatus("error");
      setMessage("Invalid file type. Please upload a supported text or spreadsheet file.");
      return;
    }
    if (selectedFile.size > 10 * 1024 * 1024) {
      setStatus("error");
      setMessage("File is too large. Maximum size is 10 MB.");
      return;
    }
    setFile(selectedFile);
    setStatus("idle");
    setMessage("");
    setFileId(null);
  }, []);

  const handleRemove = useCallback(() => {
    setFile(null);
    setStatus("idle");
    setMessage("");
    setFileId(null);
    setCorrectionData(null);
  }, []);

  const handleCorrection = useCallback(async (mappings) => {
    setStatus("processing");
    setMessage("Re-processing with your mappings...");
    try {
      const result = await correctColumns(correctionData.file_id, mappings);
      setFileId(result.data.file_id);
      setSession(result.data.session_id);
      setStatus("done");
      setMessage("Analysis complete!");
      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (err) {
      setStatus("error");
      setMessage(err.message || "Correction failed. Please try again.");
    }
  }, [correctionData, router, setSession]);

  const handleCancelCorrection = useCallback(() => {
    setCorrectionData(null);
    setStatus("idle");
    setMessage("");
  }, []);

  const handleUpload = useCallback(async () => {
    if (!file) return;
    setStatus("uploading");
    setMessage("Uploading your file...");
    try {
      setStatus("processing");
      setMessage("Analyzing transactions — this may take a moment...");
      const result = await uploadFile(file);
      if (result.status === "correction_needed") {
        setCorrectionData(result.data);
        setStatus("correction");
        setMessage("Please confirm the column mappings for your data.");
        return;
      }
      const id = result.data.file_id;
      const sessionId = result.data.session_id;
      setFileId(id);
      setSession(sessionId);
      setStatus("done");
      setMessage(result.message || "Analysis complete!");
      setTimeout(() => router.push("/dashboard"), 1500);
    } catch (err) {
      setStatus("error");
      setMessage(err.message || "Upload failed. Please try again.");
    }
  }, [file, router, setSession]);

  const isProcessing = status === "uploading" || status === "processing";

  return (
    <div className="flex min-h-screen flex-col items-center justify-center px-4 py-12">
      <div className="w-full max-w-xl">
        {/* Header — staggered fade */}
        <FadeIn delay={0.1} className="mb-10 text-center">
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
          >
            <h1 className="mb-3 text-5xl font-bold tracking-tight">
              <span className="text-gradient">Finance Analyzer</span>
            </h1>
          </motion.div>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
            className="text-lg text-[var(--color-text-secondary)]"
          >
            Upload your bank statement for instant AI-powered analysis
          </motion.p>
        </FadeIn>

        {/* Upload card */}
        <FadeIn delay={0.3}>
          {correctionData ? (
            <ColumnCorrection
              correctionData={correctionData}
              onCorrect={handleCorrection}
              onCancel={handleCancelCorrection}
              status={status}
              message={message}
            />
          ) : (
            <div className="glass-card space-y-6 p-8">
              <DropZone
                onFileSelect={handleFileSelect}
                accept=".csv,.tsv,.txt,.xlsx,.xlsm,.xls,.pdf,.docx,.doc"
                disabled={isProcessing}
              />

              {/* Animated file preview */}
              <AnimatePresence mode="wait">
                {file && (
                  <motion.div
                    key="file-preview"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <FilePreview file={file} onRemove={handleRemove} />
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Progress */}
              <UploadProgress status={status} message={message} />

              {/* Upload button */}
              <AnimatePresence mode="wait">
                {file && status !== "done" && (
                  <motion.button
                    key="upload-btn"
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.25 }}
                    onClick={handleUpload}
                    disabled={isProcessing}
                    className={`
                      w-full rounded-xl px-6 py-3.5 text-base font-semibold
                      text-white transition-all duration-300
                      ${isProcessing
                        ? "cursor-not-allowed opacity-60"
                        : "hover:scale-[1.02] active:scale-[0.98]"
                      }
                    `}
                    style={{
                      background: "var(--gradient-primary)",
                      boxShadow: isProcessing ? "none" : "0 4px 24px rgba(99, 102, 241, 0.3)",
                    }}
                    whileHover={!isProcessing ? { scale: 1.02 } : {}}
                    whileTap={!isProcessing ? { scale: 0.98 } : {}}
                  >
                    {isProcessing ? "Analyzing..." : status === "error" ? "Try Again" : "Analyze My Finances"}
                  </motion.button>
                )}

                {status === "done" && fileId && (
                  <motion.button
                    key="dashboard-btn"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, ease: [0.25, 0.46, 0.45, 0.94] }}
                    onClick={() => router.push("/dashboard")}
                    className="w-full rounded-xl border border-[var(--color-success)]/30
                               bg-[var(--color-success)]/10 px-6 py-3.5 text-base
                               font-semibold text-[var(--color-success)]
                               transition-all duration-300
                               hover:bg-[var(--color-success)]/20"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    View Dashboard →
                  </motion.button>
                )}
              </AnimatePresence>
            </div>
          )}
        </FadeIn>

        {/* Footer */}
        <FadeIn delay={0.5}>
          <p className="mt-6 text-center text-xs text-[var(--color-text-muted)]">
            Your data is processed locally and never stored permanently.
          </p>
        </FadeIn>
      </div>
    </div>
  );
}
