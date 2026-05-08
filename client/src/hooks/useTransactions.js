"use client";

import { useCallback, useMemo } from "react";
import { useSession } from "@/components/SessionProvider";

/**
 * Transactions from session with optional filters (client-side).
 *
 * @param {object} filters - { category, txn_type, sort_by, order, date_from, date_to }
 * @param {string} search - client-side search term
 */
export function useTransactions(filters = {}, search = "") {
  const { sessionId, data, isLoading, error } = useSession();
  const sessionReady = sessionId !== undefined;

  const rawTransactions = useMemo(() => {
    const list = data?.transactions;
    if (!Array.isArray(list)) return [];
    return list.map((txn) => ({
      ...txn,
      categorization_confidence:
        txn.categorization_confidence ?? txn.confidence ?? 0,
    }));
  }, [data?.transactions]);

  const applyFilters = useCallback(
    (txns) => {
      let txns2 = [...txns];

      if (filters.category) {
        txns2 = txns2.filter((t) => t.category === filters.category);
      }
      if (filters.txn_type) {
        txns2 = txns2.filter((t) => t.transaction_type === filters.txn_type);
      }
      if (filters.date_from) {
        txns2 = txns2.filter(
          (t) =>
            t.transaction_date &&
            String(t.transaction_date) >= filters.date_from
        );
      }
      if (filters.date_to) {
        txns2 = txns2.filter(
          (t) =>
            t.transaction_date && String(t.transaction_date) <= filters.date_to
        );
      }

      const reverse = filters.order === "desc";
      if (filters.sort_by === "amount") {
        txns2.sort((a, b) =>
          reverse ? b.amount - a.amount : a.amount - b.amount
        );
      } else if (filters.sort_by === "category") {
        txns2.sort((a, b) =>
          reverse
            ? String(b.category).localeCompare(String(a.category))
            : String(a.category).localeCompare(String(b.category))
        );
      } else {
        txns2.sort((a, b) => {
          const da = String(a.transaction_date || "9999-99-99");
          const db = String(b.transaction_date || "9999-99-99");
          return reverse ? db.localeCompare(da) : da.localeCompare(db);
        });
      }

      return txns2;
    },
    [
      filters.category,
      filters.txn_type,
      filters.sort_by,
      filters.order,
      filters.date_from,
      filters.date_to,
    ]
  );

  const filteredPipeline = useMemo(() => {
    const total = rawTransactions.length;
    const afterFilters = applyFilters(rawTransactions);
    const rows = afterFilters.filter((txn) => {
      if (!search) return true;
      const s = search.toLowerCase();
      return (
        txn.description?.toLowerCase().includes(s) ||
        txn.category_label?.toLowerCase().includes(s) ||
        String(txn.amount).includes(s)
      );
    });
    return { total, rows };
  }, [rawTransactions, applyFilters, search]);

  return {
    transactions: filteredPipeline.rows,
    total: filteredPipeline.total,
    filtered: filteredPipeline.rows.length,
    isLoading: sessionReady && isLoading,
    error,
    sessionReady,
    hasSession: Boolean(sessionId),
  };
}
