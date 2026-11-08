/*************************************************************************
 * audio-engine.js
 * Sovereign Neural Choukai & Stem Audio Engine v4.3:
 * 1. Authentic Web Audio API JLPT Chime Synthesizer (880Hz -> 698.46Hz)
 * 2. 100% Pre-rendered Microsoft Edge Neural MP3 Coverage for N2:
 *    - 27 Full Listening Dialogues (155/155 N2 Listening questions)
 *    - 103 Individual Dialogue Turns (100% single-turn & Kotaekata replay)
 *    - 105 Written Question Stems (375/375 N2 Written questions at 1.0x/0.8x)
 *    - 26 Taiwanese High School Trap Cards & Keigo Examples
 * 3. <ruby><rt> Furigana Stripper + Cloud-Neural Web Speech Fallback
 *    (Zero PSOLA ±25% Formant Distortion)
 *************************************************************************/

let listeningSpeed = 1.0;
let isPlayingDialogue = false;
let dialogueAbortFlag = false;
let webAudioCtx = null;
let activePreRenderedAudio = null;

const NEURAL_CARD_AUDIO_MAP = {
  "あめがふる、あめをなめる": "audio/n2/cards/card_7c668f7cb7.mp3",
  "あんざんが得意だ": "audio/n2/cards/card_f7952b85b7.mp3",
  "えんりょしないでください": "audio/n2/cards/card_697d8f9931.mp3",
  "おおやさん": "audio/n2/cards/card_72fc31c5b5.mp3",
  "おざなりな対応、ないがしろにする": "audio/n2/cards/card_9917fa50a2.mp3",
  "おじゃまします": "audio/n2/cards/card_2ea6c91b7e.mp3",
  "おゆをわかす": "audio/n2/cards/card_b3c1a06827.mp3",
  "かんびょうする": "audio/n2/cards/card_fad8066876.mp3",
  "がまんする": "audio/n2/cards/card_6c705fb0f5.mp3",
  "きしゃにのる": "audio/n2/cards/card_4db9ba25e4.mp3",
  "けがをする": "audio/n2/cards/card_6b3b251776.mp3",
  "けっそくをかためる": "audio/n2/cards/card_c312654c8f.mp3",
  "こうえんをはしる": "audio/n2/cards/card_9dd406e2d6.mp3",
  "しんぶんをよむ": "audio/n2/cards/card_82ed358a51.mp3",
  "つごうがいい": "audio/n2/cards/card_77dce1790c.mp3",
  "てがみをかく": "audio/n2/cards/card_4d88f7321b.mp3",
  "にほんごをべんきょうする": "audio/n2/cards/card_20dbce2777.mp3",
  "にんじん": "audio/n2/cards/card_165e6294e4.mp3",
  "はし": "audio/n2/cards/card_2f3fd35e5d.mp3",
  "むすめさん": "audio/n2/cards/card_a090069664.mp3",
  "ゆかにすわる": "audio/n2/cards/card_cef3da857f.mp3",
  "ゆだんたいてき": "audio/n2/cards/card_3fff971454.mp3",
  "悪人をせいばいする": "audio/n2/cards/card_48cb29f4a4.mp3",
  "ともだちにほんをかしてあげた": "audio/n2/cards/card_9a29b81acb.mp3",
  "せんせいがせつめいしてくださった": "audio/n2/cards/card_0029f6bb01.mp3",
  "せんせいにすいせんじょうをかいていただいた": "audio/n2/cards/card_9d529399c5.mp3"
};

/**
 * Strip <rt>...</rt> and <rp>...</rp> BEFORE stripping HTML tags so that
 * <ruby>漢字<rt>かんじ</rt></ruby> is never double-read as "漢字かんじ".
 */
function cleanJapaneseForTts(rawHtml) {
  if (!rawHtml) return '';
  let s = String(rawHtml);
  s = s.replace(/<rt[^>]*>.*?<\/rt>/gi, '');
  s = s.replace(/<rp[^>]*>.*?<\/rp>/gi, '');
  s = s.replace(/<[^>]+>/g, '');
  s = s.replace(/[（(][\s　＿_★＊*]+[）)]/g, '、');
  s = s.replace(/[＿_]{2,}/g, '、');
  s = s.replace(/★/g, '、');
  s = s.replace(/\s+/g, ' ').trim();
  return s;
}

function playExamChime() {
  return new Promise(resolve => {
    try {
      if (!webAudioCtx) {
        const AudioContextClass = window.AudioContext || window.webkitAudioContext;
        webAudioCtx = new AudioContextClass();
      }
      if (webAudioCtx.state === 'suspended') {
        webAudioCtx.resume();
      }
      const now = webAudioCtx.currentTime;

      // Tone 1: "Pin" (A5 = 880 Hz)
      const osc1 = webAudioCtx.createOscillator();
      const gain1 = webAudioCtx.createGain();
      osc1.type = 'sine';
      osc1.frequency.setValueAtTime(880, now);
      gain1.gain.setValueAtTime(0.18, now);
      gain1.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      osc1.connect(gain1);
      gain1.connect(webAudioCtx.destination);
      osc1.start(now);
      osc1.stop(now + 0.36);

      // Tone 2: "Pon" (F5 = 698.46 Hz)
      const osc2 = webAudioCtx.createOscillator();
      const gain2 = webAudioCtx.createGain();
      osc2.type = 'sine';
      osc2.frequency.setValueAtTime(698.46, now + 0.28);
      gain2.gain.setValueAtTime(0.18, now + 0.28);
      gain2.gain.exponentialRampToValueAtTime(0.001, now + 0.85);
      osc2.connect(gain2);
      gain2.connect(webAudioCtx.destination);
      osc2.start(now + 0.28);
      osc2.stop(now + 0.86);

      setTimeout(resolve, 750);
    } catch (e) {
      resolve();
    }
  });
}

function setListeningSpeed(spd) {
  listeningSpeed = spd;
  const map = {
    0.85: 'spdBtn085',
    1.0: 'spdBtn100',
    1.15: 'spdBtn115',
    1.25: 'spdBtn125'
  };
  Object.entries(map).forEach(([k, btnId]) => {
    const el = document.getElementById(btnId);
    if (!el) return;
    if (parseFloat(k) === spd) {
      el.className = 'px-2.5 py-1 rounded-lg text-xs font-mono bg-sky-500 text-slate-950 font-bold transition';
    } else {
      el.className = 'px-2.5 py-1 rounded-lg text-xs font-mono text-slate-400 hover:text-white transition';
    }
  });
  if (activePreRenderedAudio) {
    activePreRenderedAudio.playbackRate = spd;
  }
  const mp3Player = document.getElementById('localMp3Player');
  if (mp3Player) mp3Player.playbackRate = spd;
  if (typeof showToast === 'function') {
    showToast(`🎧 聽解播放倍速已設定為 ${spd}x`, 'sky');
  }
}

function selectJapaneseVoiceForRole(role) {
  if (!('speechSynthesis' in window)) return null;
  const voices = window.speechSynthesis.getVoices().filter(v => v.lang && v.lang.toLowerCase().includes('ja'));
  if (voices.length === 0) return null;
  if (voices.length === 1) return voices[0];

  const isMaleRole = role === 'MALE' || role === 'MALE2';
  const scored = voices.map(v => {
    let score = 0;
    const name = v.name || '';
    // Prioritize Cloud Neural / Natural / Enhanced voices over legacy SAPI5 Desktop voices
    if (/Online \(Natural\)|Neural|Enhanced|Premium|Siri/i.test(name)) score += 100;
    if (/Google 日本語/i.test(name)) score += 80;
    if (!v.localService) score += 40;
    if (/Desktop/i.test(name)) score -= 30;

    if (isMaleRole && /keita|ichiro|otoya|male|hattori|takumi/i.test(name)) {
      score += 60;
    } else if (!isMaleRole && /nanami|kyoko|haruka|ayumi|sayaka|female|mizuki/i.test(name)) {
      score += 60;
    }
    return { v, score };
  });

  scored.sort((a, b) => b.score - a.score);
  return scored[0].v;
}

async function speakSingleUtterance(text, role, audioUrlOverride = null, customRate = null) {
  const clean = cleanJapaneseForTts(text);
  const audioModeSelect = document.getElementById('audioEngineModeSelect');
  const preferStaticMp3 = !audioModeSelect || audioModeSelect.value !== 'WEBSPEECH';
  const mappedMp3 = audioUrlOverride || NEURAL_CARD_AUDIO_MAP[text] || NEURAL_CARD_AUDIO_MAP[clean];

  if (preferStaticMp3 && mappedMp3 && !dialogueAbortFlag) {
    const ok = await tryPlayPreRenderedMp3(mappedMp3, 0, customRate || listeningSpeed);
    if (ok) return;
  }

  return new Promise((resolve) => {
    if (!('speechSynthesis' in window) || dialogueAbortFlag || !clean) {
      resolve();
      return;
    }
    window.speechSynthesis.cancel();

    const utter = new SpeechSynthesisUtterance(clean);
    utter.lang = 'ja-JP';
    const voice = selectJapaneseVoiceForRole(role);
    if (voice) utter.voice = voice;

    const baseSpeed = customRate || listeningSpeed;
    // Keep pitch near 1.0 (0.95..1.03) to prevent metallic PSOLA formant distortion
    if (role === 'MALE') {
      utter.pitch = 0.95;
      utter.rate = Number((0.98 * baseSpeed).toFixed(2));
    } else if (role === 'MALE2') {
      utter.pitch = 0.98;
      utter.rate = Number((1.0 * baseSpeed).toFixed(2));
    } else if (role === 'FEMALE') {
      utter.pitch = 1.03;
      utter.rate = Number((1.0 * baseSpeed).toFixed(2));
    } else {
      utter.pitch = 1.0;
      utter.rate = Number((0.98 * baseSpeed).toFixed(2));
    }

    utter.onend = () => resolve();
    utter.onerror = () => resolve();
    window.speechSynthesis.speak(utter);
  });
}

function setActiveKotaekataStep(activeStep) {
  for (let s = 1; s <= 4; s++) {
    const el = document.getElementById(`kotaeStep${s}`);
    if (!el) continue;
    if (s === activeStep) {
      el.className = 'kotaekata-step p-2 rounded-lg bg-emerald-900/60 border-2 border-emerald-400 text-center shadow-lg scale-[1.02] transition-all';
    } else {
      el.className = 'kotaekata-step p-2 rounded-lg bg-slate-900/90 border border-slate-700 text-center opacity-80 transition-all';
    }
  }
}

function tryPlayPreRenderedMp3(audioFileUrl, totalTurns = 0, customRate = null) {
  return new Promise((resolve) => {
    if (!audioFileUrl) {
      resolve(false);
      return;
    }
    if (activePreRenderedAudio) {
      try {
        activePreRenderedAudio.pause();
        activePreRenderedAudio.currentTime = 0;
      } catch (e) {}
      activePreRenderedAudio = null;
    }

    const audio = new Audio(audioFileUrl);
    activePreRenderedAudio = audio;
    audio.playbackRate = customRate || listeningSpeed;

    let resolved = false;
    const finish = (ok) => {
      if (!resolved) {
        resolved = true;
        if (activePreRenderedAudio === audio) {
          activePreRenderedAudio = null;
        }
        resolve(ok);
      }
    };

    audio.ontimeupdate = () => {
      if (audio.duration && totalTurns > 0) {
        const ratio = audio.currentTime / audio.duration;
        const estTurn = Math.min(totalTurns, Math.floor(ratio * totalTurns) + 1);
        const turnCounter = document.getElementById('turnCounterText');
        if (turnCounter) turnCounter.textContent = `語音段: ${estTurn} / ${totalTurns} (Neural MP3)`;
        if (typeof highlightActiveTranscriptLine === 'function') {
          highlightActiveTranscriptLine(estTurn - 1);
        }
        setActiveKotaekataStep(estTurn === 1 ? 1 : (estTurn === totalTurns ? 3 : 2));
      }
    };

    audio.onended = () => finish(true);
    audio.onerror = () => finish(false);

    audio.play().catch(() => finish(false));
  });
}

async function playListeningDialogue() {
  const q = typeof getCurrentQuestion === 'function' ? getCurrentQuestion() : null;
  if (!q || !Array.isArray(q.dialogue)) {
    if (typeof speakQuestion === 'function') speakQuestion(listeningSpeed);
    return;
  }

  if (isPlayingDialogue) {
    stopListeningDialogue();
    return;
  }

  isPlayingDialogue = true;
  dialogueAbortFlag = false;

  const playBtnText = document.getElementById('playChoukaiText');
  const playBtnIcon = document.getElementById('playChoukaiIcon');
  const eqBox = document.getElementById('eqVisualizer');
  const speakerBadge = document.getElementById('activeSpeakerBadge');
  const statusDot = document.getElementById('choukaiStatusDot');
  const turnCounter = document.getElementById('turnCounterText');

  if (playBtnText) playBtnText.textContent = '播放中... (點擊停止)';
  if (playBtnIcon) playBtnIcon.textContent = '⏸';
  if (eqBox) eqBox.classList.add('eq-playing');
  if (statusDot) statusDot.className = 'w-3 h-3 rounded-full bg-emerald-400';

  // 1. Play Authentic JLPT Exam Intro Chime ("Pin-Pon")
  setActiveKotaekataStep(1);
  if (speakerBadge) speakerBadge.textContent = '🔔 考場提示鐘聲 (チャイム 880Hz→698Hz)...';
  await playExamChime();

  const totalTurns = q.dialogue.length;
  const audioModeSelect = document.getElementById('audioEngineModeSelect');
  const preferStaticMp3 = !audioModeSelect || audioModeSelect.value !== 'WEBSPEECH';

  let playedStatic = false;
  const hasDedicatedMp3 = Boolean(q.audioFile && q.hasExactMp3 !== false);
  if (preferStaticMp3 && hasDedicatedMp3 && !dialogueAbortFlag) {
    if (speakerBadge) speakerBadge.textContent = '🎙️ 播放 Microsoft Neural 真人級雙聲道音訊 (Keita & Nanami)...';
    playedStatic = await tryPlayPreRenderedMp3(q.audioFile, totalTurns);
  }

  // Fallback to Turn-by-Turn playback (uses per-turn Neural MP3 first, then Cloud Web Speech)
  if (!playedStatic && !dialogueAbortFlag) {
    for (let i = 0; i < totalTurns; i++) {
      if (dialogueAbortFlag) break;
      const turn = q.dialogue[i];
      if (turnCounter) turnCounter.textContent = `語音段: ${i + 1} / ${totalTurns}`;
      if (speakerBadge) speakerBadge.textContent = `${turn.speakerLabel} 發話中...`;

      if (typeof highlightActiveTranscriptLine === 'function') {
        highlightActiveTranscriptLine(i);
      }
      setActiveKotaekataStep(i === 0 ? 1 : (turn.role === 'QUESTION' || i === totalTurns - 1 ? 3 : 2));

      if (turn.role === 'QUESTION' && i > 0) {
        await new Promise(r => setTimeout(r, 350));
        if (dialogueAbortFlag) break;
        await playExamChime();
      }

      await speakSingleUtterance(turn.jp, turn.role, turn.audioTurnFile || null);
      if (dialogueAbortFlag) break;
      await new Promise(r => setTimeout(r, 260));
    }
  }

  if (!dialogueAbortFlag && q.blindOptions && typeof blindOptionsUnmasked !== 'undefined' && !blindOptionsUnmasked) {
    if (typeof unmaskBlindOptions === 'function') unmaskBlindOptions();
    if (typeof showToast === 'function') {
      showToast('🎧 音訊播放完畢！已為您自動解鎖盲聽題選項，請作答。', 'sky');
    }
  }

  resetChoukaiPlayerUI();
}

function stopListeningDialogue() {
  dialogueAbortFlag = true;
  isPlayingDialogue = false;
  if (activePreRenderedAudio) {
    try {
      activePreRenderedAudio.pause();
      activePreRenderedAudio.currentTime = 0;
    } catch (e) {}
    activePreRenderedAudio = null;
  }
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
  }
  resetChoukaiPlayerUI();
}

function resetChoukaiPlayerUI() {
  isPlayingDialogue = false;
  const playBtnText = document.getElementById('playChoukaiText');
  const playBtnIcon = document.getElementById('playChoukaiIcon');
  const eqBox = document.getElementById('eqVisualizer');
  const speakerBadge = document.getElementById('activeSpeakerBadge');
  const statusDot = document.getElementById('choukaiStatusDot');

  if (playBtnText) playBtnText.textContent = '重新播放考場對話';
  if (playBtnIcon) playBtnIcon.textContent = '▶';
  if (eqBox) eqBox.classList.remove('eq-playing');
  if (speakerBadge) speakerBadge.textContent = '播放完畢 (可重播或作答)';
  if (statusDot) statusDot.className = 'w-3 h-3 rounded-full bg-sky-400';
  if (typeof highlightActiveTranscriptLine === 'function') {
    highlightActiveTranscriptLine(-1);
  }
  setActiveKotaekataStep(4);
}

async function replayDialogueTurn(turnIdx) {
  const q = typeof getCurrentQuestion === 'function' ? getCurrentQuestion() : null;
  if (!q || !q.dialogue || !q.dialogue[turnIdx]) return;
  stopListeningDialogue();
  dialogueAbortFlag = false;

  const turn = q.dialogue[turnIdx];
  const eqBox = document.getElementById('eqVisualizer');
  const speakerBadge = document.getElementById('activeSpeakerBadge');

  if (eqBox) eqBox.classList.add('eq-playing');
  if (speakerBadge) speakerBadge.textContent = `🔁 單句精聽重播 (Neural MP3)：${turn.speakerLabel}`;
  if (typeof highlightActiveTranscriptLine === 'function') {
    highlightActiveTranscriptLine(turnIdx);
  }

  await speakSingleUtterance(turn.jp, turn.role, turn.audioTurnFile || null);
  resetChoukaiPlayerUI();
}

async function triggerKotaekataStep(stepNum) {
  const q = typeof getCurrentQuestion === 'function' ? getCurrentQuestion() : null;
  if (!q || !Array.isArray(q.dialogue) || q.dialogue.length === 0) return;
  setActiveKotaekataStep(stepNum);
  if (stepNum === 1) {
    await replayDialogueTurn(0);
  } else if (stepNum === 2) {
    const keyIdx = q.dialogue.findIndex(t => t.isKeySignal);
    const targetIdx = keyIdx !== -1 ? keyIdx : Math.min(1, q.dialogue.length - 1);
    if (typeof peekListeningTranscript === 'function') peekListeningTranscript();
    await replayDialogueTurn(targetIdx);
  } else if (stepNum === 3) {
    await replayDialogueTurn(q.dialogue.length - 1);
  } else if (stepNum === 4) {
    if (typeof unmaskBlindOptions === 'function') unmaskBlindOptions();
    document.getElementById('optionsContainer')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
}
