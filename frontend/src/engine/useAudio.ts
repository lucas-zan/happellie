import { useMemo } from 'react';
import type { AudioController, SfxKey } from './types';

let audioCtx: AudioContext | null = null;

function ctx(): AudioContext | null {
  try {
    if (!audioCtx) {
      const Ctor = window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext;
      if (!Ctor) return null;
      audioCtx = new Ctor();
    }
    if (audioCtx.state === 'suspended') audioCtx.resume().catch(() => undefined);
    return audioCtx;
  } catch {
    return null;
  }
}

function note(c: AudioContext, freq: number, start: number, dur: number, type: OscillatorType, vol: number) {
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = type;
  osc.frequency.value = freq;
  gain.gain.setValueAtTime(vol, start);
  gain.gain.exponentialRampToValueAtTime(0.001, start + dur);
  osc.connect(gain);
  gain.connect(c.destination);
  osc.start(start);
  osc.stop(start + dur);
}

function sfxCorrect(c: AudioContext) {
  const t = c.currentTime;
  note(c, 880, t, 0.12, 'triangle', 0.08);
  note(c, 1108, t + 0.08, 0.15, 'triangle', 0.07);
  note(c, 1318, t + 0.16, 0.2, 'sine', 0.05);
}

function sfxWrong(c: AudioContext) {
  const t = c.currentTime;
  note(c, 280, t, 0.15, 'sawtooth', 0.06);
  note(c, 220, t + 0.08, 0.2, 'sawtooth', 0.05);
}

function sfxCoin(c: AudioContext) {
  const t = c.currentTime;
  note(c, 1568, t, 0.06, 'sine', 0.07);
  note(c, 2093, t + 0.05, 0.08, 'sine', 0.06);
  note(c, 2637, t + 0.1, 0.12, 'sine', 0.04);
}

function sfxTap(c: AudioContext) {
  const t = c.currentTime;
  note(c, 800, t, 0.03, 'square', 0.04);
  note(c, 600, t + 0.015, 0.03, 'sine', 0.03);
}

function sfxWhoosh(c: AudioContext) {
  const t = c.currentTime;
  const osc = c.createOscillator();
  const gain = c.createGain();
  osc.type = 'sine';
  osc.frequency.setValueAtTime(600, t);
  osc.frequency.exponentialRampToValueAtTime(200, t + 0.15);
  gain.gain.setValueAtTime(0.05, t);
  gain.gain.exponentialRampToValueAtTime(0.001, t + 0.15);
  osc.connect(gain);
  gain.connect(c.destination);
  osc.start(t);
  osc.stop(t + 0.15);
}

function sfxCheer(c: AudioContext) {
  const t = c.currentTime;
  note(c, 523, t, 0.1, 'triangle', 0.06);
  note(c, 659, t + 0.08, 0.1, 'triangle', 0.06);
  note(c, 784, t + 0.16, 0.1, 'triangle', 0.06);
  note(c, 1046, t + 0.24, 0.2, 'sine', 0.05);
}

const SFX_MAP: Record<SfxKey, (c: AudioContext) => void> = {
  correct: sfxCorrect,
  wrong: sfxWrong,
  coin: sfxCoin,
  tap: sfxTap,
  whoosh: sfxWhoosh,
  cheer: sfxCheer,
};

export function useAudio(): AudioController {
  return useMemo(() => ({
    playSfx: (key) => {
      const c = ctx();
      if (!c) return;
      try { SFX_MAP[key]?.(c); } catch { /* ignore */ }
    },
    playTts: (text) => {
      try {
        if (!('speechSynthesis' in window)) return;
        const utter = new SpeechSynthesisUtterance(text);
        utter.rate = 0.9;
        utter.pitch = 1.05;
        window.speechSynthesis.cancel();
        window.speechSynthesis.speak(utter);
      } catch { /* ignore */ }
    },
  }), []);
}
