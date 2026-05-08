"use client";

import { useState, useCallback, Suspense } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useTransactions } from "@/hooks/useTransactions";
import { useSession } from "@/components/SessionProvider";
import TransactionTable from "@/components/ui/TransactionTable";
import FilterBar from "@/components/ui/FilterBar";
import { FadeIn, StaggerContainer, StaggerItem } from "@/components/ui/Motion";
import { TableSkeleton } from "@/components/ui/Skeleton";

function TransactionsContent() {
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [txnType, setTxnType] = useState("");
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo] = useState("");
  const [sortBy, setSortBy] = useState("date");
  const [order, setOrder] = useState("asc");

  const filters = { category, txn_type: txnType, sort_by: sortBy, order, date_from: dateFrom, date_to: dateTo };
  const { transactions, total, filtered, isLoading, error, sessionReady, hasSession } =
    useTransactions(filters, search);

  const handleSort = useCallback(
    (col) => {
      if (sortBy === col) {
        setOrder((o) => (o === "asc" ? "desc" : "asc"));
      } else {
        setSortBy(col);
        setOrder("asc");
      }
    },
    [sortBy]
  );

  if (!sessionReady) {
    return (
      <div className="space-y-4">
        <div className="glass-card p-4"><div className="shimmer h-10 w-full rounded-lg" /></div>
        <TableSkeleton />
      </div>
    );
  }

  if (!hasSession) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">📄</span>
          <h2 className="mt-4 text-xl font-semibold">No analysis session</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">
            Upload a bank statement to view transactions.
          </p>
          <Link
            href="/"
            className="mt-6 inline-block rounded-xl px-6 py-2.5 text-sm font-semibold text-white transition-all hover:scale-105"
            style={{ background: "var(--gradient-primary)" }}
          >
            Upload File
          </Link>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="glass-card p-4"><div className="shimmer h-10 w-full rounded-lg" /></div>
        <TableSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="glass-card max-w-md p-10 text-center">
          <span className="text-5xl">⚠️</span>
          <h2 className="mt-4 text-xl font-semibold text-[var(--color-danger)]">Failed to load</h2>
          <p className="mt-2 text-sm text-[var(--color-text-secondary)]">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <StaggerContainer stagger={0.12} className="space-y-4">
      <StaggerItem>
        <FilterBar
          search={search}
          onSearchChange={setSearch}
          category={category}
          onCategoryChange={setCategory}
          txnType={txnType}
          onTypeChange={setTxnType}
          dateFrom={dateFrom}
          dateTo={dateTo}
          onDateFromChange={setDateFrom}
          onDateToChange={setDateTo}
          total={total}
          filtered={filtered}
        />
      </StaggerItem>
      <StaggerItem>
        <TransactionTable
          transactions={transactions}
          sortBy={sortBy}
          order={order}
          onSort={handleSort}
        />
      </StaggerItem>
    </StaggerContainer>
  );
}

export default function TransactionsPage() {
  const router = useRouter();
  const { clearSession } = useSession();

  const handleNewUpload = () => {
    clearSession();
    router.push("/");
  };

  return (
    <div className="min-h-screen bg-grid px-4 py-8 sm:px-6 lg:px-8">
      <FadeIn className="mx-auto mb-6 max-w-7xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">
              <span className="text-gradient">Transactions</span>
            </h1>
            <p className="mt-1 text-sm text-[var(--color-text-muted)]">
              Browse, search, and filter your financial data
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/dashboard"
              className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-light)] hover:text-[var(--color-text)]"
            >
              ← Dashboard
            </Link>
            <button
              type="button"
              onClick={handleNewUpload}
              className="rounded-lg border border-[var(--color-border)] px-4 py-2 text-sm text-[var(--color-text-secondary)] transition-colors hover:border-[var(--color-border-light)] hover:text-[var(--color-text)]"
            >
              Upload New File
            </button>
          </div>
        </div>
      </FadeIn>

      <div className="mx-auto max-w-7xl">
        <Suspense
          fallback={
            <div className="flex min-h-[60vh] items-center justify-center">
              <div className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]" />
            </div>
          }
        >
          <TransactionsContent />
        </Suspense>
      </div>
    </div>
  );
}
