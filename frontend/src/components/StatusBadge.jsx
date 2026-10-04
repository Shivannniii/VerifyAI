import { verdictInfo } from "../verdicts";

export default function StatusBadge({ status }) {
  const { label, classes } = verdictInfo(status);

  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${classes}`}>
      {label}
    </span>
  );
}
