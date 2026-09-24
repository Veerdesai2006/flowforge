import React, { useState, useEffect, useMemo } from 'react';
import { Activity, ChevronLeft, ChevronRight, Inbox } from 'lucide-react';

/**
 * ActivityFeed Component with internal pagination and fixed height scroll.
 * 
 * Features:
 * - Fixed max height container with internal scroll (no outer layout shift/push).
 * - Configurable PAGE_SIZE (default: 10).
 * - Pinned pagination footer with flex-shrink: 0.
 * - Auto page reset when item count changes.
 * - Accessible: aria-labels, role="region", and aria-live="polite".
 */
export default function ActivityFeed({ activities = [], pageSize = 10, maxHeight = '420px', title }) {
  const [currentPage, setCurrentPage] = useState(1);

  // Reset to page 1 whenever activities list changes
  useEffect(() => {
    setCurrentPage(1);
  }, [activities.length]);

  const totalItems = activities.length;
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  // Ensure current page doesn't exceed totalPages if items shrink
  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [totalPages, currentPage]);

  // Paginated items
  const paginatedActivities = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return activities.slice(startIndex, startIndex + pageSize);
  }, [activities, currentPage, pageSize]);

  const handlePrev = () => {
    setCurrentPage((prev) => Math.max(1, prev - 1));
  };

  const handleNext = () => {
    setCurrentPage((prev) => Math.min(totalPages, prev + 1));
  };

  return (
    <div
      className="flex flex-col rounded-2xl bg-bg2 border border-border overflow-hidden"
      style={{ maxHeight }}
      role="region"
      aria-label={title || "Activity feed"}
    >
      {/* Optional Card Header if title provided */}
      {title && (
        <div className="p-6 pb-4 border-b border-border/50 flex-shrink-0 flex items-center gap-2">
          <Activity className="text-accent2" size={20} />
          <h2 className="text-xl font-bold text-textMain">{title}</h2>
        </div>
      )}

      {/* Scrollable Inner List Area */}
      <div 
        className="flex-1 overflow-y-auto p-6 space-y-4 min-h-0 focus:outline-none" 
        tabIndex={0}
        aria-live="polite"
        aria-atomic="true"
      >
        {totalItems === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center text-text3">
            <Inbox className="w-10 h-10 mb-2 opacity-40 text-text3" />
            <p className="text-sm italic">No recent activity recorded.</p>
          </div>
        ) : (
          paginatedActivities.map((act) => (
            <div
              key={act.id}
              className="flex items-start gap-4 p-4 rounded-xl bg-bg3 border border-border hover:border-accent2/40 transition-colors"
            >
              <div className="p-2.5 bg-accent2/10 text-accent2 rounded-xl flex-shrink-0 mt-0.5 border border-accent2/20">
                <Activity size={16} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="text-sm font-bold text-textMain truncate">{act.action}</div>
                  <time className="text-xs text-text3 flex-shrink-0" dateTime={act.created_at}>
                    {new Date(act.created_at).toLocaleString([], {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </time>
                </div>
                {act.description && (
                  <div className="text-sm text-text2 mt-1.5 break-words line-clamp-2">
                    {act.description}
                  </div>
                )}
                {act.user_id && (
                  <div className="mt-2 inline-block px-2 py-0.5 bg-bg4 text-[11px] font-medium text-text3 rounded">
                    User ID: {act.user_id}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      {/* Pinned Pagination Footer */}
      {totalItems > 0 && totalPages > 1 && (
        <div className="flex-shrink-0 px-6 py-3.5 bg-bg3/60 border-t border-border flex items-center justify-between gap-4">
          <span className="text-xs font-medium text-text3">
            Page <strong className="text-textMain">{currentPage}</strong> of <strong className="text-textMain">{totalPages}</strong>
            <span className="hidden sm:inline text-text3 ml-1.5">({totalItems} total items)</span>
          </span>

          <div className="flex items-center gap-2">
            <button
              onClick={handlePrev}
              disabled={currentPage === 1}
              aria-label="Previous page of activities"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 bg-bg4 text-textMain border border-border hover:bg-accent hover:border-accent disabled:opacity-40 disabled:hover:bg-bg4 disabled:hover:border-border disabled:cursor-not-allowed transition-all active:scale-95"
            >
              <ChevronLeft size={14} />
              <span>Prev</span>
            </button>
            <button
              onClick={handleNext}
              disabled={currentPage === totalPages}
              aria-label="Next page of activities"
              className="px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center gap-1 bg-bg4 text-textMain border border-border hover:bg-accent hover:border-accent disabled:opacity-40 disabled:hover:bg-bg4 disabled:hover:border-border disabled:cursor-not-allowed transition-all active:scale-95"
            >
              <span>Next</span>
              <ChevronRight size={14} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
