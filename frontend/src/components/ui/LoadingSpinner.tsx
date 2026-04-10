import { Loader2 } from "lucide-react";

export default function LoadingSpinner({ message }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <Loader2 className="h-8 w-8 animate-spin text-amber-500" />
      {message && <p className="mt-3 text-sm text-slate-500">{message}</p>}
    </div>
  );
}
