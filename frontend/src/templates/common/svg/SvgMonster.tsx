function normalizeMood(raw: string): 'happy' | 'sad' | 'strong' | 'neutral' {
  const v = raw.toLowerCase();
  if (v.includes('happy') || v.includes('excited') || v.includes('joy')) return 'happy';
  if (v.includes('sad') || v.includes('worried') || v.includes('scared')) return 'sad';
  if (v.includes('strong') || v.includes('determined') || v.includes('angry')) return 'strong';
  return 'neutral';
}

export function SvgMonster({ mood = 'neutral', size = 80 }: { mood?: string; size?: number }) {
  const m = normalizeMood(mood);
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} fill="none" aria-hidden="true" className={`svg-char svg-char--monster svg-char--${m}`}>
      {/* Horns */}
      <path d="M38 38 L28 8 L50 34Z" fill="#7D3C98" />
      <path d="M70 34 L92 8 L82 38Z" fill="#7D3C98" />
      {/* Body */}
      <circle cx="60" cy="66" r="40" fill="#8E44AD" />
      {/* Belly */}
      <ellipse cx="60" cy="74" rx="28" ry="22" fill="#A569BD" />
      {/* Spots */}
      <circle cx="34" cy="54" r="4" fill="#7D3C98" opacity="0.5" />
      <circle cx="88" cy="58" r="3" fill="#7D3C98" opacity="0.5" />
      <circle cx="78" cy="44" r="3.5" fill="#7D3C98" opacity="0.5" />
      {/* Big eye */}
      {m === 'happy' ? (
        <>
          <circle cx="60" cy="56" r="16" fill="#fff" />
          <path d="M50 56 Q60 48 70 56" stroke="#2C3E50" strokeWidth="3" strokeLinecap="round" />
        </>
      ) : m === 'sad' ? (
        <>
          <circle cx="60" cy="56" r="16" fill="#fff" />
          <circle cx="60" cy="58" r="10" fill="#2C3E50" />
          <circle cx="63" cy="55" r="3.5" fill="#fff" />
          <path d="M46 46 L54 50" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M74 46 L66 50" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" />
        </>
      ) : m === 'strong' ? (
        <>
          <circle cx="60" cy="56" r="16" fill="#fff" />
          <circle cx="60" cy="56" r="12" fill="#C0392B" />
          <circle cx="60" cy="56" r="6" fill="#2C3E50" />
          <circle cx="62" cy="53" r="3" fill="#fff" />
          <path d="M44 44 L56 50" stroke="#2C3E50" strokeWidth="3" strokeLinecap="round" />
          <path d="M76 44 L64 50" stroke="#2C3E50" strokeWidth="3" strokeLinecap="round" />
        </>
      ) : (
        <>
          <circle cx="60" cy="56" r="16" fill="#fff" />
          <circle cx="60" cy="56" r="10" fill="#2C3E50" />
          <circle cx="63" cy="53" r="3.5" fill="#fff" />
        </>
      )}
      {/* Mouth */}
      {m === 'happy' ? (
        <path d="M42 80 L50 74 L58 80 L66 74 L74 80" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      ) : m === 'sad' ? (
        <path d="M48 84 Q60 78 72 84" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" />
      ) : m === 'strong' ? (
        <>
          <path d="M40 78 L50 72 L58 78 L66 72 L74 78 L80 72" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
          <path d="M44 78 L50 82 L58 78 L66 82 L76 78" stroke="#fff" strokeWidth="1.5" strokeLinecap="round" opacity="0.6" />
        </>
      ) : (
        <path d="M44 80 L52 74 L60 80 L68 74 L76 80" stroke="#2C3E50" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
      )}
      {/* Small feet */}
      <ellipse cx="46" cy="104" rx="10" ry="5" fill="#7D3C98" />
      <ellipse cx="74" cy="104" rx="10" ry="5" fill="#7D3C98" />
    </svg>
  );
}
