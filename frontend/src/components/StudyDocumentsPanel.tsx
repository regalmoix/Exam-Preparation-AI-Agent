import clsx from "clsx";

import type { StudyDocument } from "../hooks/useStudyDocuments";
import { FileUpload } from "./FileUpload";

type StudyDocumentsPanelProps = {
  documents: StudyDocument[];
  loadingDocuments: boolean;
  documentsError: string | null;
  onSelectDocument: (document: StudyDocument) => void;
  onDocumentsRefresh?: () => void;
  onDeleteDocument?: (document: StudyDocument) => void;
};

export function StudyDocumentsPanel({
  documents,
  loadingDocuments,
  documentsError,
  onSelectDocument,
  onDocumentsRefresh,
  onDeleteDocument,
}: StudyDocumentsPanelProps) {

  return (
    <div className="flex h-full flex-col rounded-3xl border border-slate-200/60 bg-white/80 shadow-[0_35px_90px_-45px_rgba(15,23,42,0.55)] ring-1 ring-slate-200/60 backdrop-blur dark:border-slate-800/70 dark:bg-slate-900/70 dark:shadow-[0_45px_95px_-50px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
      <div className="border-b border-slate-200/60 px-6 py-5 dark:border-slate-800/60">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-100">
              Study materials
            </h2>
            <p className="mt-2 max-w-2xl text-sm text-slate-600 dark:text-slate-300">
              Browse your uploaded study documents. Click any document to view its contents.
            </p>
          </div>
          <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium uppercase tracking-wide text-slate-600 dark:bg-slate-800/70 dark:text-slate-300">
            {loadingDocuments ? "Loading…" : `${documents.length} files`}
          </span>
        </div>

        {/* File Upload Section */}
        {onDocumentsRefresh && (
          <FileUpload
            onUploadComplete={onDocumentsRefresh}
            className="mt-4"
          />
        )}
      </div>

      <div className="relative flex-1 overflow-hidden">
        {documentsError ? (
          <ErrorState message={documentsError} />
        ) : (
          <DocumentGrid
            documents={documents}
            loading={loadingDocuments}
            onSelectDocument={onSelectDocument}
            onDeleteDocument={onDeleteDocument}
          />
        )}
      </div>

    </div>
  );
}


function DocumentGrid({
  documents,
  loading,
  onSelectDocument,
  onDeleteDocument,
}: {
  documents: StudyDocument[];
  loading: boolean;
  onSelectDocument: (document: StudyDocument) => void;
  onDeleteDocument?: (document: StudyDocument) => void;
}) {
  if (loading) {
    return (
      <div className="grid h-full place-items-center bg-gradient-to-br from-slate-50/70 via-white to-slate-100/80 text-slate-500 dark:from-slate-900/40 dark:via-slate-900/20 dark:to-slate-900/60">
        <span className="text-sm font-medium">Loading documents…</span>
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="grid h-full place-items-center bg-slate-50/50 text-sm text-slate-500 dark:bg-slate-900/40 dark:text-slate-400">
        No documents available.
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto px-6 py-6">
      <div
        className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3"
        style={{ gridAutoRows: "1fr" }}
      >
        {documents.map((document) => {
          const fileVariant = getFileVariant(document.filename);
          return (
            <div
              key={document.id}
              className="group relative flex h-full min-h-[260px] flex-col justify-between overflow-hidden rounded-2xl border border-slate-200/70 bg-white/80 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg dark:border-slate-800/70 dark:bg-slate-900/80"
            >
              {/* Delete button */}
              {onDeleteDocument && (
                <button
                  type="button"
                  className="absolute right-2 top-2 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-red-500/10 text-red-500 opacity-0 transition-all duration-200 hover:bg-red-500 hover:text-white group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 dark:bg-red-500/20 dark:focus:ring-offset-slate-900"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteDocument(document);
                  }}
                  title={`Delete ${document.title}`}
                >
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              )}

              {/* Main clickable area */}
              <button
                type="button"
                className="flex h-full w-full flex-col justify-between p-4 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
                onClick={() => onSelectDocument(document)}
              >
                <div className="flex flex-col gap-4">
                  <div className="space-y-1">
                    <span
                      className={clsx(
                        "inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide",
                        fileVariant.badge,
                      )}
                    >
                      {fileVariant.label}
                    </span>
                    <p
                      className="text-xs font-medium text-slate-500 dark:text-slate-400 break-words"
                    >
                      {document.filename}
                    </p>
                  </div>
                  <div className="flex flex-1 flex-col space-y-2">
                    <h3 className="text-base font-semibold leading-snug text-slate-800 transition-colors group-hover:text-blue-600 dark:text-slate-100 dark:group-hover:text-blue-300 break-words">
                      {document.title}
                    </h3>
                    {document.description ? (
                      <p
                        className="text-sm leading-snug text-slate-600 dark:text-slate-300 line-clamp-3 break-words"
                        style={{
                          display: "-webkit-box",
                          WebkitBoxOrient: "vertical",
                          WebkitLineClamp: 3,
                          overflow: "hidden",
                        }}
                      >
                        {document.description}
                      </p>
                    ) : null}
                  </div>
                </div>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function ErrorState({ message }: { message: string }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-3 bg-red-50/70 px-6 text-center text-sm text-red-600 dark:bg-red-950/40 dark:text-red-300">
      <span className="font-semibold">Unable to load documents</span>
      <span>{message}</span>
    </div>
  );
}

type FileVariant = "pdf" | "html" | "default";

function getFileVariant(filename: string): {
  variant: FileVariant;
  label: string;
  badge: string;
} {
  const lower = filename.toLowerCase();
  let variant: FileVariant = "default";
  if (lower.endsWith(".pdf")) variant = "pdf";
  else if (lower.endsWith(".html")) variant = "html";

  const styles: Record<FileVariant, { label: string; badge: string }> = {
    pdf: {
      label: "PDF",
      badge: "bg-rose-100 text-rose-700 dark:bg-rose-900/50 dark:text-rose-200",
    },
    html: {
      label: "HTML",
      badge: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200",
    },
    default: {
      label: "FILE",
      badge: "bg-slate-100 text-slate-600 dark:bg-slate-800/60 dark:text-slate-200",
    },
  };

  const style = styles[variant];
  return { variant, ...style };
}
