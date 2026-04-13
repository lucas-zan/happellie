import { resolveCharacterAsset } from './characterRegistry';
import { SceneBackground } from './SceneBackground';

type CharacterStageProps = {
  left?: { id?: string; mood?: string; line?: string };
  right?: { id?: string; mood?: string; line?: string };
  scene?: string;
};

function moodClass(mood?: string) {
  const value = String(mood || '').toLowerCase();
  if (value.includes('excited') || value.includes('happy')) return 'mood-happy';
  if (value.includes('angry') || value.includes('determined')) return 'mood-strong';
  if (value.includes('sad') || value.includes('worried')) return 'mood-sad';
  return 'mood-neutral';
}

function CharacterCard({
  position,
  char,
}: {
  position: 'left' | 'right';
  char?: { id?: string; mood?: string; line?: string };
}) {
  const id = String(char?.id || (position === 'left' ? 'foxy' : 'ellie'));
  const mood = String(char?.mood || 'neutral');
  const asset = resolveCharacterAsset(id);
  const Svg = asset.SvgComponent;

  return (
    <div className={`char-stage__character char-stage__character--${position} ${moodClass(mood)}`}>
      <div className="char-stage__avatar-wrap">
        {Svg ? (
          <Svg mood={mood} size={56} />
        ) : asset.sprite ? (
          <img className="char-stage__sprite" src={asset.sprite} alt={id} />
        ) : (
          <span className="char-stage__emoji" aria-hidden="true">
            {asset.emoji}
          </span>
        )}
      </div>
      <div className="char-stage__meta">
        <strong>{asset.displayName}</strong>
        <span>{mood}</span>
      </div>
      {char?.line ? <p className="char-stage__line">"{char.line}"</p> : null}
    </div>
  );
}

export function CharacterStage({ left, right, scene }: CharacterStageProps) {
  return (
    <div className="char-stage">
      <SceneBackground scene={scene} />
      <div className="char-stage__actors">
        <CharacterCard position="left" char={left} />
        <CharacterCard position="right" char={right} />
      </div>
    </div>
  );
}
