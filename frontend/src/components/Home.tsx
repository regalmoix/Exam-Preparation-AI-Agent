import { useCallback, useState } from "react";
import clsx from "clsx";

import { ChatKitPanel } from "./ChatKitPanel";
import { DocumentPreviewModal } from "./DocumentPreviewModal";
import { StudyDocumentsPanel } from "./StudyDocumentsPanel";
import { ThemeToggle } from "./ThemeToggle";
import type { StudyDocument } from "../hooks/useStudyDocuments";
import { useStudyDocuments } from "../hooks/useStudyDocuments";
import type { ColorScheme } from "../hooks/useColorScheme";
import { EXAM_PREP_DOCUMENTS_URL } from "../lib/config";

type HomeProps = {
  scheme: ColorScheme;
  onThemeChange: (scheme: ColorScheme) => void;
};

export default function Home({ scheme, onThemeChange }: HomeProps) {
  const [selectedDocument, setSelectedDocument] = useState<StudyDocument | null>(null);

  const {
    documents,
    loading: loadingDocuments,
    error: documentsError,
    refresh: refreshDocuments,
  } = useStudyDocuments();

  const containerClass = clsx(
    "min-h-screen bg-gradient-to-br transition-colors duration-300",
    scheme === "dark"
      ? "from-slate-950 via-slate-950 to-slate-900 text-slate-100"
      : "from-slate-100 via-white to-slate-200 text-slate-900",
  );

  const handleDocumentSelect = useCallback((document: StudyDocument) => {
    setSelectedDocument(document);
  }, []);

  const handleClosePreview = useCallback(() => {
    setSelectedDocument(null);
  }, []);

  const handleDeleteDocument = useCallback(async (document: StudyDocument) => {
    if (!confirm(`Are you sure you want to delete "${document.title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      const response = await fetch(`${EXAM_PREP_DOCUMENTS_URL}/${document.id}`, {
        method: 'DELETE',
        headers: { Accept: "application/json" },
      });

      if (!response.ok) {
        throw new Error(`Failed to delete document (${response.status})`);
      }

      // Close preview if the deleted document is currently selected
      if (selectedDocument?.id === document.id) {
        setSelectedDocument(null);
      }

      // Refresh the documents list
      await refreshDocuments();
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      alert(`Failed to delete document: ${message}`);
    }
  }, [selectedDocument, refreshDocuments]);

  return (
    <div className={containerClass}>
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col gap-8 px-6 py-8 lg:py-10">
        <header className="flex flex-col gap-6 lg:flex-row lg:items-center lg:justify-between">
          <div className="space-y-3">
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
              AI Exam Preparation Assistant
            </p>
            <h1 className="text-3xl font-semibold sm:text-4xl">
              Master your study materials
            </h1>
            <p className="max-w-3xl text-sm text-slate-600 dark:text-slate-300">
              Ask questions about your uploaded study materials, create flashcards, and get personalized study assistance. The AI searches through your documents and provides cited references to help you learn effectively.
            </p>
          </div>
          <ThemeToggle value={scheme} onChange={onThemeChange} />
        </header>

        <div className="grid flex-1 grid-cols-1 gap-8 lg:h-[calc(100vh-260px)] lg:grid-cols-[minmax(320px,380px)_1fr] lg:items-stretch xl:grid-cols-[minmax(360px,420px)_1fr]">
          <section className="flex flex-1 flex-col overflow-hidden rounded-3xl bg-white/80 shadow-[0_45px_90px_-45px_rgba(15,23,42,0.6)] ring-1 ring-slate-200/60 backdrop-blur dark:bg-slate-900/70 dark:shadow-[0_45px_90px_-45px_rgba(15,23,42,0.85)] dark:ring-slate-800/60">
            <div className="flex flex-1">
              <ChatKitPanel theme={scheme} />
            </div>
          </section>

          <section className="flex flex-1 flex-col overflow-hidden">
            <StudyDocumentsPanel
              documents={documents}
              loadingDocuments={loadingDocuments}
              documentsError={documentsError}
              onSelectDocument={handleDocumentSelect}
              onDocumentsRefresh={refreshDocuments}
              onDeleteDocument={handleDeleteDocument}
            />
          </section>
        </div>
      </div>

      <DocumentPreviewModal document={selectedDocument} onClose={handleClosePreview} />
    </div>
  );
}
