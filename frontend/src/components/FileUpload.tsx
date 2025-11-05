import { useState, useRef, useCallback } from "react";
import clsx from "clsx";

type FileUploadProps = {
  onUploadComplete: () => void;
  className?: string;
};

export function FileUpload({ onUploadComplete, className }: FileUploadProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<{
    message: string;
    type: "success" | "error" | null;
  }>({ message: "", type: null });

  const fileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED_FILE_TYPES = [".pdf", ".txt", ".md", ".html", ".docx", ".json"];
  const API_BASE = "/exam-assistant";

  const handleFiles = useCallback(async (files: FileList | File[]) => {
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadStatus({ message: "", type: null });

    const filesToUpload = Array.from(files);
    let successCount = 0;
    let errorCount = 0;

    for (const file of filesToUpload) {
      // Check file type
      const fileExtension = "." + file.name.split(".").pop()?.toLowerCase();
      if (!ALLOWED_FILE_TYPES.includes(fileExtension || "")) {
        console.error(`File type not supported: ${file.name}`);
        errorCount++;
        continue;
      }

      try {
        const formData = new FormData();
        formData.append("file", file);

        const response = await fetch(`${API_BASE}/documents/upload`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          successCount++;
        } else {
          const error = await response.json();
          console.error(`Upload failed for ${file.name}:`, error);
          errorCount++;
        }
      } catch (error) {
        console.error(`Upload error for ${file.name}:`, error);
        errorCount++;
      }
    }

    // Show status
    if (errorCount === 0) {
      setUploadStatus({
        message: `✅ Successfully uploaded ${successCount} file${successCount !== 1 ? "s" : ""}!`,
        type: "success",
      });
    } else if (successCount > 0) {
      setUploadStatus({
        message: `⚠️ Uploaded ${successCount} files, ${errorCount} failed`,
        type: "error",
      });
    } else {
      setUploadStatus({
        message: `❌ Upload failed. Check file types and try again.`,
        type: "error",
      });
    }

    setIsUploading(false);

    // Clear status after 4 seconds
    setTimeout(() => {
      setUploadStatus({ message: "", type: null });
    }, 4000);

    // Refresh documents if any succeeded
    if (successCount > 0) {
      onUploadComplete();
    }

    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, [onUploadComplete]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setDragActive(false);

      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFiles(e.dataTransfer.files);
      }
    },
    [handleFiles]
  );

  const handleFileInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        handleFiles(e.target.files);
      }
    },
    [handleFiles]
  );

  const openFileDialog = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  return (
    <div className={clsx("mt-4", className)}>
      <div
        className={clsx(
          "relative rounded-xl border-2 border-dashed p-4 text-center transition-all",
          dragActive
            ? "border-blue-400 bg-blue-50/50 dark:border-blue-500 dark:bg-blue-900/20"
            : "border-slate-300 bg-slate-50/50 hover:border-slate-400 hover:bg-slate-100/50 dark:border-slate-600 dark:bg-slate-800/30 dark:hover:border-slate-500",
          isUploading && "pointer-events-none opacity-60"
        )}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          className="hidden"
          accept={ALLOWED_FILE_TYPES.join(",")}
          onChange={handleFileInputChange}
          disabled={isUploading}
        />

        {isUploading ? (
          <div className="flex flex-col items-center gap-2">
            <div className="h-5 w-5 animate-spin rounded-full border-2 border-blue-600 border-t-transparent" />
            <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
              Uploading files...
            </span>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <div className="rounded-full bg-slate-200/60 p-2 dark:bg-slate-700/60">
              <svg
                className="h-5 w-5 text-slate-500 dark:text-slate-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                />
              </svg>
            </div>
            <div>
              <button
                type="button"
                className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
                onClick={openFileDialog}
              >
                Click to upload
              </button>
              <span className="text-sm text-slate-500 dark:text-slate-400">
                {" "}
                or drag and drop
              </span>
            </div>
            <p className="text-xs text-slate-400 dark:text-slate-500">
              PDF, TXT, MD, HTML, DOCX, JSON files
            </p>
          </div>
        )}
      </div>

      {uploadStatus.message && (
        <div
          className={clsx(
            "mt-3 rounded-lg px-3 py-2 text-sm font-medium",
            uploadStatus.type === "success"
              ? "bg-green-50 text-green-700 border border-green-200 dark:bg-green-900/20 dark:text-green-400 dark:border-green-800"
              : "bg-red-50 text-red-700 border border-red-200 dark:bg-red-900/20 dark:text-red-400 dark:border-red-800"
          )}
        >
          {uploadStatus.message}
        </div>
      )}
    </div>
  );
}
