"use client";

import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface TranscriptViewerProps {
  transcript: string;
}

export default function TranscriptViewer({ transcript }: TranscriptViewerProps) {
  const [copied, setCopied] = useState(false);
  const lines = transcript.split("\n");
  const wordCount = transcript.split(/\s+/).filter(Boolean).length;

  const handleCopy = () => {
    navigator.clipboard.writeText(transcript);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="rounded-xl overflow-hidden" style={{ background: "var(--admin-surface)", border: "1px solid var(--admin-border)" }}>
      <div className="flex items-center justify-between px-4 py-2.5" style={{ borderBottom: "1px solid var(--admin-border)", background: "#FAFAF9" }}>
        <span style={{ fontSize: 12, color: "var(--admin-muted)" }}>{wordCount} palabras · {lines.length} líneas</span>
        <button onClick={handleCopy} className="flex items-center gap-1 rounded px-2 py-1" style={{ fontSize: 11, color: "var(--admin-muted)", background: copied ? "var(--admin-green-bg)" : "transparent" }}>
          {copied ? <Check className="h-3 w-3" style={{ color: "var(--admin-green)" }} /> : <Copy className="h-3 w-3" />}
          {copied ? "Copiado" : "Copiar"}
        </button>
      </div>
      <div className="overflow-y-auto p-4" style={{ maxHeight: 400 }}>
        <pre className="font-mono whitespace-pre-wrap" style={{ fontSize: 13, lineHeight: 1.7, color: "var(--admin-text)" }}>
          {lines.map((line, i) => (
            <div key={i} className="flex">
              <span className="select-none text-right w-8 mr-4 shrink-0 font-mono" style={{ fontSize: 11, color: "var(--admin-dim)" }}>{i + 1}</span>
              <span>{line}</span>
            </div>
          ))}
        </pre>
      </div>
    </div>
  );
}
