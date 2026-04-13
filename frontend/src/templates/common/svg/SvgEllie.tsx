function normalizeMood(raw: string): 'happy' | 'sad' | 'strong' | 'neutral' {
  const v = raw.toLowerCase();
  if (v.includes('happy') || v.includes('excited') || v.includes('joy')) return 'happy';
  if (v.includes('sad') || v.includes('worried') || v.includes('scared')) return 'sad';
  if (v.includes('strong') || v.includes('determined') || v.includes('angry')) return 'strong';
  return 'neutral';
}

export function SvgEllie({ mood = 'neutral', size = 80 }: { mood?: string; size?: number }) {
  const m = normalizeMood(mood);
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} fill="none" aria-hidden="true" className={`svg-char svg-char--ellie svg-char--${m}`}>
      {/* Ears */}
      <ellipse cx="42" cy="24" rx="11" ry="24" fill="#FFB3C6" transform="rotate(-8 42 24)" />
      <ellipse cx="78" cy="24" rx="11" ry="24" fill="#FFB3C6" transform="rotate(8 78 24)" />
      <ellipse cx="42" cy="24" rx="7" ry="18" fill="#FFD6E0" transform="rotate(-8 42 24)" />
      <ellipse cx="78" cy="24" rx="7" ry="18" fill="#FFD6E0" transform="rotate(8 78 24)" />
      {/* Head */}
      <circle cx="60" cy="68" r="36" fill="#FFB3C6" />
      {/* Face */}
      <ellipse cx="60" cy="72" rx="28" ry="24" fill="#FFD6E0" />
      {/* Blush */}
      <circle cx="40" cy="76" r="6" fill="#FF8FAB" opacity="0.3" />
      <circle cx="80" cy="76" r="6" fill="#FF8FAB" opacity="0.3" />
      {/* Eyes */}
      {m === 'happy' ? (
        <>
          <path d="M43 64 Q48 59 53 64" stroke="#5C3D4E" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M67 64 Q72 59 77 64" stroke="#5C3D4E" strokeWidth="2.5" strokeLinecap="round" />
        </>
      ) : m === 'sad' ? (
        <>
          <circle cx="48" cy="64" r="3.5" fill="#5C3D4E" />
          <circle cx="72" cy="64" r="3.5" fill="#5C3D4E" />
          <circle cx="49" cy="62.5" r="1.2" fill="#fff" />
          <circle cx="73" cy="62.5" r="1.2" fill="#fff" />
          <path d="M42 58 L54 61" stroke="#5C3D4E" strokeWidth="2" strokeLinecap="round" />
          <path d="M78 58 L66 61" stroke="#5C3D4E" strokeWidth="2" strokeLinecap="round" />
        </>
      ) : m === 'strong' ? (
        <>
          <circle cx="48" cy="64" r="4" fill="#5C3D4E" />
          <circle cx="72" cy="64" r="4" fill="#5C3D4E" />
          <circle cx="49" cy="62.5" r="1.3" fill="#fff" />
          <circle cx="73" cy="62.5" r="1.3" fill="#fff" />
          <path d="M40 59 L55 63" stroke="#5C3D4E" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M80 59 L65 63" stroke="#5C3D4E" strokeWidth="2.5" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx="48" cy="64" r="3.5" fill="#5C3D4E" />
          <circle cx="72" cy="64" r="3.5" fill="#5C3D4E" />
          <circle cx="49.2" cy="62.5" r="1.3" fill="#fff" />
          <circle cx="73.2" cy="62.5" r="1.3" fill="#fff" />
        </>
      )}
      {/* Nose */}
      <ellipse cx="60" cy="73" rx="3" ry="2.2" fill="#FF8FAB" />
      {/* Mouth */}
      {m === 'happy' ? (
        <path d="M52 79 Q60 87 68 79" stroke="#5C3D4E" strokeWidth="2" strokeLinecap="round" />
      ) : m === 'sad' ? (
        <path d="M53 83 Q60 78 67 83" stroke="#5C3D4E" strokeWidth="2" strokeLinecap="round" />
      ) : m === 'strong' ? (
        <path d="M53 80 L67 80" stroke="#5C3D4E" strokeWidth="2.5" strokeLinecap="round" />
      ) : (
        <path d="M54 80 Q60 83 66 80" stroke="#5C3D4E" strokeWidth="1.8" strokeLinecap="round" />
      )}
    </svg>
  );
}
