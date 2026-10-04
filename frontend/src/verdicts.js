// Backend verdict codes -> labels and colours used across the UI.

export const VERDICTS = {
  potentially_supported: {
    label: "Likely supported",
    classes: "bg-supported-bg text-supported",
    stripe: "border-supported",
    checked: true,
  },
  partially_supported: {
    label: "Partly supported",
    classes: "bg-partial-bg text-partial",
    stripe: "border-partial",
    checked: true,
  },
  uncertain: {
    label: "Uncertain",
    classes: "bg-uncertain-bg text-uncertain",
    stripe: "border-uncertain",
    checked: true,
  },
};

const NOT_CHECKED = {
  label: "Not checked",
  classes: "bg-white text-muted ring-1 ring-inset ring-line",
  stripe: "border-line",
  checked: false,
};

// "pending", "unverified" and "verification_pending" all mean: no evidence check yet.
export const verdictInfo = (status) => VERDICTS[status] ?? NOT_CHECKED;

export const isChecked = (status) => Boolean(VERDICTS[status]);

export function formatDate(value) {
  if (!value) return "";
  // the API sends UTC timestamps without a "Z" suffix
  const iso = /[zZ]|[+-]\d\d:?\d\d$/.test(value) ? value : `${value}Z`;
  const date = new Date(iso);
  return Number.isNaN(date.getTime())
    ? ""
    : date.toLocaleDateString(undefined, { day: "numeric", month: "short", year: "numeric" });
}
