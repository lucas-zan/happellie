function normalizeMood(raw: string): 'happy' | 'sad' | 'strong' | 'neutral' {
  const v = raw.toLowerCase();
  if (v.includes('happy') || v.includes('excited') || v.includes('joy')) return 'happy';
  if (v.includes('sad') || v.includes('worried') || v.includes('scared')) return 'sad';
  if (v.includes('strong') || v.includes('determined') || v.includes('angry')) return 'strong';
  return 'neutral';
}

export function SvgFoxy({ mood = 'neutral', size = 80 }: { mood?: string; size?: number }) {
  const m = normalizeMood(mood);
  return (
    <svg viewBox="0 0 120 120" width={size} height={size} fill="none" aria-hidden="true" className={`svg-char svg-char--foxy svg-char--${m}`}>
      {/* Ears */}
      <path d="M32 46 L40 10 L52 42Z" fill="#FF8C42" />
      <path d="M68 42 L80 10 L88 46Z" fill="#FF8C42" />
      <path d="M37 42 L42 18 L50 40Z" fill="#FFD6A0" />
      <path d="M70 40 L78 18 L83 42Z" fill="#FFD6A0" />
      {/* Head */}
      <circle cx="60" cy="66" r="36" fill="#FF8C42" />
      {/* White face patch */}
      <path d="M36 70 Q42 56 60 52 Q78 56 84 70 Q78 92 60 96 Q42 92 36 70Z" fill="#FFF5E6" />
      {/* Eyes */}
      {m === 'happy' ? (
        <>
          <path d="M43 60 Q48 55 53 60" stroke="#4A3520" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M67 60 Q72 55 77 60" stroke="#4A3520" strokeWidth="2.5" strokeLinecap="round" />
        </>
      ) : m === 'sad' ? (
        <>
          <circle cx="48" cy="60" r="3.5" fill="#4A3520" />
          <circle cx="72" cy="60" r="3.5" fill="#4A3520" />
          <circle cx="49" cy="58.5" r="1.2" fill="#fff" />
          <circle cx="73" cy="58.5" r="1.2" fill="#fff" />
          <path d="M42 54 L54 57" stroke="#4A3520" strokeWidth="2" strokeLinecap="round" />
          <path d="M78 54 L66 57" stroke="#4A3520" strokeWidth="2" strokeLinecap="round" />
        </>
      ) : m === 'strong' ? (
        <>
          <ellipse cx="48" cy="60" rx="4" ry="3" fill="#4A3520" />
          <ellipse cx="72" cy="60" rx="4" ry="3" fill="#4A3520" />
          <circle cx="49" cy="58.5" r="1.3" fill="#fff" />
          <circle cx="73" cy="58.5" r="1.3" fill="#fff" />
          <path d="M40 55 L55 59" stroke="#4A3520" strokeWidth="2.5" strokeLinecap="round" />
          <path d="M80 55 L65 59" stroke="#4A3520" strokeWidth="2.5" strokeLinecap="round" />
        </>
      ) : (
        <>
          <ellipse cx="48" cy="60" rx="3.5" ry="4" fill="#4A3520" />
          <ellipse cx="72" cy="60" rx="3.5" ry="4" fill="#4A3520" />
          <circle cx="49.2" cy="58.5" r="1.3" fill="#fff" />
          <circle cx="73.2" cy="58.5" r="1.3" fill="#fff" />
        </>
      )}
      {/* Nose */}
      <path d="M57 70 L60 66 L63 70Z" fill="#4A3520" />
      {/* Whiskers */}
      <line x1="36" y1="70" x2="50" y2="72" stroke="#CC7A3A" strokeWidth="1" opacity="0.5" />
      <line x1="36" y1="74" x2="50" y2="74" stroke="#CC7A3A" strokeWidth="1" opacity="0.5" />
      <line x1="84" y1="70" x2="70" y2="72" stroke="#CC7A3A" strokeWidth="1" opacity="0.5" />
      <line x1="84" y1="74" x2="70" y2="74" stroke="#CC7A3A" strokeWidth="1" opacity="0.5" />
      {/* Mouth */}
      {m === 'happy' ? (
        <path d="M52 76 Q60 84 68 76" stroke="#4A3520" strokeWidth="2" strokeLinecap="round" />
      ) : m === 'sad' ? (
        <path d="M53 80 Q60 76 67 80" stroke="#4A3520" strokeWidth="2" strokeLinecap="round" />
      ) : (
        <path d="M54 77 Q60 80 66 77" stroke="#4A3520" strokeWidth="1.8" strokeLinecap="round" />
      )}
    </svg>
  );
}
