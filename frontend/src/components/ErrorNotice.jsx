import { AlertCircle } from "lucide-react";

export default function ErrorNotice({ children }) {
  if (!children) return null;

  return (
    <div
      role="alert"
      className="flex items-start gap-2 rounded-md bg-danger-bg px-3 py-2 text-sm text-danger"
    >
      <AlertCircle size={16} className="mt-0.5 shrink-0" aria-hidden="true" />
      <span>{children}</span>
    </div>
  );
}
