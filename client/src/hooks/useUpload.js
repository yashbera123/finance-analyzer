"use client";

import { useState, useCallback } from "react";
import { uploadFile } from "@/lib/api";

/**
 * Hook for managing file upload state.
 *
 * @returns {{ upload, isUploading, error, result, reset }}
 */
export function useUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const upload = useCallback(async (file) => {
    setIsUploading(true);
    setError(null);
    setResult(null);

    try {
      const data = await uploadFile(file);
      setResult(data);
      return data;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setIsUploading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setIsUploading(false);
    setError(null);
    setResult(null);
  }, []);

  return { upload, isUploading, error, result, reset };
}
