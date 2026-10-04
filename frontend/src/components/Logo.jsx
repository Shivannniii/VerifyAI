export default function Logo({ compact = false, dark = false }) {
  const stroke = dark ? '#ffffff' : '#ffffff';
  return (
    <div className="logo" aria-label="VerifyAI">
      <svg className="logo-mark" viewBox="0 0 48 48" fill="none" aria-hidden="true">
        <defs><linearGradient id="bookg" x1="4" y1="5" x2="43" y2="43" gradientUnits="userSpaceOnUse"><stop stopColor="#6366F1"/><stop offset="1" stopColor="#8B5CF6"/></linearGradient></defs>
        <path d="M7 12c5-5 11-5 17 0v27c-6-4-12-4-17 0V12Z" fill="url(#bookg)"/>
        <path d="M41 12c-5-5-11-5-17 0v27c6-4 12-4 17 0V12Z" fill="url(#bookg)" opacity=".92"/>
        <circle cx="29.5" cy="25.5" r="7.5" fill="#0F172A" stroke={stroke} strokeWidth="2.8"/>
        <path d="m35.2 31.2 6.2 6.2" stroke={stroke} strokeWidth="3.4" strokeLinecap="round"/>
      </svg>
      {!compact && <span className="logo-word-wrap"><span className="logo-word">Verify<span>AI</span></span><span className="logo-tag">Research with Confidence</span></span>}
    </div>
  );
}
