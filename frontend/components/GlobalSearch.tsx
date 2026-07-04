"use client";

import { useRouter } from "next/navigation";
import { Search, X } from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";

import { StatusBadge } from "@/components/StatusBadge";
import { formatControlledValue } from "@/lib/controlled-values";
import { type SearchResult, globalSearch } from "@/lib/fms-api";

const resultTypeOrder: SearchResult["type"][] = ["building", "property", "passport", "asset", "document", "campus", "organization"];

export function GlobalSearch() {
  const router = useRouter();
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleClick = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClick);
    return () => document.removeEventListener("mousedown", handleClick);
  }, []);

  useEffect(() => {
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setResults([]);
      setIsLoading(false);
      setError(null);
      return;
    }

    setIsLoading(true);
    setError(null);
    const handle = window.setTimeout(() => {
      void globalSearch(trimmedQuery)
        .then((nextResults) => {
          setResults(nextResults);
          setIsOpen(true);
        })
        .catch((searchError) => {
          setError(searchError instanceof Error ? searchError.message : "Search failed.");
          setResults([]);
          setIsOpen(true);
        })
        .finally(() => setIsLoading(false));
    }, 250);

    return () => window.clearTimeout(handle);
  }, [query]);

  const groupedResults = useMemo(() => {
    return resultTypeOrder
      .map((type) => ({
        type,
        results: results.filter((result) => result.type === type)
      }))
      .filter((group) => group.results.length > 0);
  }, [results]);

  function openResult(result: SearchResult) {
    setIsOpen(false);
    setQuery("");
    router.push(result.url);
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" && results[0]) {
      event.preventDefault();
      openResult(results[0]);
    }
    if (event.key === "Escape") {
      event.preventDefault();
      setIsOpen(false);
      inputRef.current?.blur();
    }
  }

  return (
    <div ref={containerRef} className="relative w-full max-w-xl">
      <div className="flex h-10 items-center gap-2 rounded-xl border border-white/10 bg-white/5 px-3 text-[#B6C1CF] shadow-sm transition focus-within:border-[#FF6B5F]/70 focus-within:shadow-md">
        <Search size={18} />
        <input
          ref={inputRef}
          value={query}
          onChange={(event) => {
            setQuery(event.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder="Search FPP"
          className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-[#7D8CA3]"
          aria-label="Global search"
        />
        {query ? (
          <button
            type="button"
            onClick={() => {
              setQuery("");
              setResults([]);
              setIsOpen(false);
            }}
            className="flex h-6 w-6 items-center justify-center rounded-lg text-[#7D8CA3] hover:bg-white/10 hover:text-white"
            aria-label="Clear search"
            title="Clear search"
          >
            <X size={14} />
          </button>
        ) : null}
      </div>

      {isOpen && query.trim() ? (
        <div className="absolute right-0 z-50 mt-2 max-h-[70vh] w-full min-w-[320px] overflow-auto rounded-2xl border border-white/10 bg-[#111827] shadow-2xl">
          {isLoading ? <div className="p-4 text-sm text-[#B6C1CF]">Searching...</div> : null}
          {error ? <div className="p-4 text-sm text-red-700">{error}</div> : null}
          {!isLoading && !error && !results.length ? <div className="p-4 text-sm text-[#B6C1CF]">No results found.</div> : null}
          {!isLoading && !error && groupedResults.length ? (
            <div className="py-2">
              {groupedResults.map((group) => (
                <div key={group.type} className="border-b border-white/10 py-2 last:border-b-0">
                  <p className="px-3 pb-1 text-xs font-semibold uppercase text-[#7D8CA3]">{formatControlledValue(group.type)}</p>
                  <div className="space-y-1">
                    {group.results.map((result) => (
                      <button
                        key={`${result.type}-${result.id}-${result.url}`}
                        type="button"
                        onClick={() => openResult(result)}
                        className="flex w-full items-start justify-between gap-3 px-3 py-2 text-left transition hover:bg-white/[0.045]"
                      >
                        <span className="min-w-0">
                          <span className="block truncate text-sm font-semibold text-white">{result.title}</span>
                          <span className="block truncate text-xs text-[#7D8CA3]">{result.subtitle || result.matched_field}</span>
                        </span>
                        <StatusBadge status={formatControlledValue(result.type)} />
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
