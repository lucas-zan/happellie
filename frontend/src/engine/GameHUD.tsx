import { SvgEllie } from '../templates/common/svg';

export function GameHUD({
  stepIndex,
  totalSteps,
  coins,
}: {
  stepIndex: number;
  totalSteps: number;
  coins: number;
}) {
  const completed = Math.min(stepIndex + 1, totalSteps);
  return (
    <div className="game-hud">
      <div className="game-hud__left">
        <div className="game-hud__pet">
          <SvgEllie mood="happy" size={36} />
        </div>
        <span className="game-hud__meta">Ellie's Adventure</span>
      </div>
      <div className="game-hud__center">
        <div className="game-hud__stars" aria-label={`Step ${completed} of ${totalSteps}`}>
          {Array.from({ length: totalSteps }).map((_, i) => (
            <span
              key={i}
              className={`game-hud__star ${i < completed ? 'is-filled' : ''}`}
              aria-hidden="true"
            >
              {i < completed ? '⭐️' : '☆'}
            </span>
          ))}
        </div>
      </div>
      <div className="game-hud__right">
        <div className="game-hud__coins">
          <span className="game-hud__coin-icon" aria-hidden="true">💰</span>
          <span className="game-hud__coin-value">{coins}</span>
        </div>
      </div>
    </div>
  );
}
