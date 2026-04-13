const SCENES: Record<string, { gradient: string; label: string }> = {
  forest_path: {
    gradient: 'linear-gradient(180deg, #b5e6a3 0%, #4a8c3f 60%, #2d5a27 100%)',
    label: 'Forest Path',
  },
  cave_gate: {
    gradient: 'linear-gradient(180deg, #3d2c5e 0%, #1a1a3e 60%, #0d0d24 100%)',
    label: 'Cave Gate',
  },
  moon_bridge: {
    gradient: 'linear-gradient(180deg, #1a2a50 0%, #0a1628 50%, #0d1b3e 100%)',
    label: 'Moon Bridge',
  },
  sea_coast: {
    gradient: 'linear-gradient(180deg, #87CEEB 0%, #4da6c9 50%, #2e8aad 100%)',
    label: 'Sea Coast',
  },
  forest_split_road: {
    gradient: 'linear-gradient(180deg, #a8d98a 0%, #5a9e50 50%, #3d7a32 100%)',
    label: 'Split Road',
  },
  learn_zone: {
    gradient: 'linear-gradient(180deg, #fff5e6 0%, #ffe0b2 50%, #ffd199 100%)',
    label: 'Learn Zone',
  },
  story_branch: {
    gradient: 'linear-gradient(180deg, #ffe0f0 0%, #fff5e6 60%, #fff0e0 100%)',
    label: 'Story',
  },
};

function Trees() {
  return (
    <svg className="scene-bg__decor" viewBox="0 0 320 80" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <path d="M20 80 L35 30 L50 80Z" fill="rgba(0,0,0,0.15)" />
      <path d="M70 80 L90 20 L110 80Z" fill="rgba(0,0,0,0.1)" />
      <path d="M200 80 L220 25 L240 80Z" fill="rgba(0,0,0,0.12)" />
      <path d="M270 80 L285 35 L300 80Z" fill="rgba(0,0,0,0.08)" />
    </svg>
  );
}

function Rocks() {
  return (
    <svg className="scene-bg__decor" viewBox="0 0 320 60" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <path d="M0 60 L10 30 L30 20 L50 35 L60 60Z" fill="rgba(255,255,255,0.08)" />
      <path d="M260 60 L275 25 L295 30 L310 20 L320 60Z" fill="rgba(255,255,255,0.06)" />
      <circle cx="160" cy="15" r="3" fill="rgba(255,255,255,0.15)" />
      <circle cx="180" cy="25" r="2" fill="rgba(255,255,255,0.12)" />
    </svg>
  );
}

function MoonAndStars() {
  return (
    <svg className="scene-bg__decor scene-bg__decor--top" viewBox="0 0 320 100" preserveAspectRatio="xMidYMin slice" aria-hidden="true">
      <circle cx="260" cy="30" r="20" fill="rgba(255,255,200,0.25)" />
      <circle cx="264" cy="26" r="18" fill="rgba(255,255,200,0.15)" />
      <circle cx="50" cy="20" r="1.5" fill="rgba(255,255,255,0.6)" className="scene-bg__star" />
      <circle cx="100" cy="40" r="1" fill="rgba(255,255,255,0.5)" className="scene-bg__star" style={{ animationDelay: '0.5s' }} />
      <circle cx="150" cy="15" r="1.2" fill="rgba(255,255,255,0.55)" className="scene-bg__star" style={{ animationDelay: '1s' }} />
      <circle cx="200" cy="50" r="0.8" fill="rgba(255,255,255,0.4)" className="scene-bg__star" style={{ animationDelay: '1.5s' }} />
      <circle cx="30" cy="55" r="1" fill="rgba(255,255,255,0.45)" className="scene-bg__star" style={{ animationDelay: '0.8s' }} />
    </svg>
  );
}

function Waves() {
  return (
    <svg className="scene-bg__decor" viewBox="0 0 320 50" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <path d="M0 50 Q40 30 80 40 Q120 50 160 38 Q200 26 240 38 Q280 50 320 35 L320 50Z" fill="rgba(255,255,255,0.15)" className="scene-bg__wave" />
      <path d="M0 50 Q50 35 100 42 Q150 50 200 40 Q250 30 320 42 L320 50Z" fill="rgba(255,255,255,0.1)" className="scene-bg__wave" style={{ animationDelay: '1s' }} />
    </svg>
  );
}

function ForestFork() {
  return (
    <svg className="scene-bg__decor" viewBox="0 0 320 80" preserveAspectRatio="xMidYMax slice" aria-hidden="true">
      <path d="M160 0 L160 40 Q140 50 100 80" stroke="rgba(255,255,255,0.2)" strokeWidth="4" fill="none" strokeLinecap="round" />
      <path d="M160 0 L160 40 Q180 50 220 80" stroke="rgba(255,255,255,0.2)" strokeWidth="4" fill="none" strokeLinecap="round" />
      <path d="M30 80 L45 35 L60 80Z" fill="rgba(0,0,0,0.1)" />
      <path d="M260 80 L275 40 L290 80Z" fill="rgba(0,0,0,0.08)" />
    </svg>
  );
}

const DECOR_MAP: Record<string, () => JSX.Element> = {
  forest_path: Trees,
  cave_gate: Rocks,
  moon_bridge: MoonAndStars,
  sea_coast: Waves,
  forest_split_road: ForestFork,
};

export function SceneBackground({ scene }: { scene?: string }) {
  const key = scene || 'forest_path';
  const config = SCENES[key] || SCENES.forest_path;
  const Decor = DECOR_MAP[key] || null;
  const isDark = key === 'cave_gate' || key === 'moon_bridge';

  return (
    <div className={`scene-bg ${isDark ? 'scene-bg--dark' : ''}`} style={{ background: config.gradient }}>
      {Decor ? <Decor /> : null}
      <span className="scene-bg__label">{config.label}</span>
    </div>
  );
}
