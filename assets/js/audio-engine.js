/*************************************************************************
 * audio-engine.js
 * Dual-Mode Choukai Audio Engine:
 * 1. Authentic Web Audio API JLPT Chime Synthesizer (880Hz -> 698.46Hz)
 * 2. Pre-rendered edge-tts Multi-Role MP3 playback (KeitaNeural & NanamiNeural)
 * 3. Seamless Fallback & Single-Turn Replay via Dual-Pitch Web Speech API
 *************************************************************************/

let listeningSpeed = 1.0;
let isPlayingDialogue = false;
let dialogueAbortFlag = false;
let webAudioCtx = null;
let activePreRenderedAudio = null;

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
      el.className = 'px-2.5 py-1 rounded-lg text-[11px] font-mono bg-sky-500 text-slate-950 font-bold transition';
    } else {
      el.className = 'px-2.5 py-1 rounded-lg text-[11px] font-mono text-slate-400 hover:text-white transition';
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

  if (role === 'MALE' || role === 'MALE2') {
    const maleMatch = voices.find(v => /keita|ichiro|otoya|male|hattori/i.test(v.name));
    return maleMatch || voices[0];
  } else if (role === 'FEMALE') {
    const femaleMatch = voices.find(v => /nanami|haruka|kyoko|ayumi|female|sayaka/i.test(v.name));
    return femaleMatch || voices[Math.min(1, voices.length - 1)];
  }
  return voices[0];
}

function speakSingleUtterance(text, role) {
  return new Promise((resolve) => {
    if (!('speechSynthesis' in window) || dialogueAbortFlag) {
      resolve();
      return;
    }
    window.speechSynthesis.cancel();

    const clean = (text || '').replace(/<[^>]*>/g, '');
    const utter = new SpeechSynthesisUtterance(clean);
    utter.lang = 'ja-JP';
    const voice = selectJapaneseVoiceForRole(role);
    if (voice) utter.voice = voice;

    if (role === 'MALE') {
      utter.pitch = 0.76;
      utter.rate = Number((0.98 * listeningSpeed).toFixed(2));
    } else if (role === 'MALE2') {
      utter.pitch = 0.88;
      utter.rate = Number((1.02 * listeningSpeed).toFixed(2));
    } else if (role === 'FEMALE') {
      utter.pitch = 1.25;
      utter.rate = Number((1.03 * listeningSpeed).toFixed(2));
    } else {
      utter.pitch = 1.0;
      utter.rate = Number((1.0 * listeningSpeed).toFixed(2));
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

function tryPlayPreRenderedMp3(audioFileUrl, totalTurns) {
  return new Promise((resolve) => {
    if (!audioFileUrl || window.location.protocol === 'file:') {
      // On file:// standalone HTML without audio directory or if missing, check if reachable
    }
    const audio = new Audio(audioFileUrl);
    activePreRenderedAudio = audio;
    audio.playbackRate = listeningSpeed;

    let resolved = false;
    const finish = (ok) => {
      if (!resolved) {
        resolved = true;
        activePreRenderedAudio = null;
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

  playBtnText.textContent = '播放中... (點擊停止)';
  playBtnIcon.textContent = '⏸';
  eqBox.classList.add('eq-playing');
  statusDot.className = 'w-3 h-3 rounded-full bg-emerald-400 animate-ping';

  // 1. Play Authentic JLPT Exam Intro Chime ("Pin-Pon")
  setActiveKotaekataStep(1);
  speakerBadge.textContent = '🔔 考場提示鐘聲 (チャイム 880Hz→698Hz)...';
  await playExamChime();

  const totalTurns = q.dialogue.length;
  const audioModeSelect = document.getElementById('audioEngineModeSelect');
  const preferStaticMp3 = !audioModeSelect || audioModeSelect.value !== 'WEBSPEECH';

  let playedStatic = false;
  const hasDedicatedMp3 = Boolean(q.audioFile && q.id && q.audioFile.includes(`${q.id}.mp3`));
  if (preferStaticMp3 && hasDedicatedMp3 && !dialogueAbortFlag) {
    speakerBadge.textContent = '🎙️ 播放 edge-tts 真人級雙聲道音訊 (Keita & Nanami)...';
    playedStatic = await tryPlayPreRenderedMp3(q.audioFile, totalTurns);
  }

  // Fallback to Turn-by-Turn Web Speech API if static MP3 not used or offline
  if (!playedStatic && !dialogueAbortFlag) {
    for (let i = 0; i < totalTurns; i++) {
      if (dialogueAbortFlag) break;
      const turn = q.dialogue[i];
      turnCounter.textContent = `語音段: ${i + 1} / ${totalTurns}`;
      speakerBadge.textContent = `${turn.speakerLabel} 發話中...`;

      if (typeof highlightActiveTranscriptLine === 'function') {
        highlightActiveTranscriptLine(i);
      }
      setActiveKotaekataStep(i === 0 ? 1 : (turn.role === 'QUESTION' || i === totalTurns - 1 ? 3 : 2));

      if (turn.role === 'QUESTION' && i > 0) {
        await new Promise(r => setTimeout(r, 350));
        if (dialogueAbortFlag) break;
        await playExamChime();
      }

      await speakSingleUtterance(turn.jp, turn.role);
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
  if (speakerBadge) speakerBadge.textContent = `🔁 單句精聽重播：${turn.speakerLabel}`;
  if (typeof highlightActiveTranscriptLine === 'function') {
    highlightActiveTranscriptLine(turnIdx);
  }

  await speakSingleUtterance(turn.jp, turn.role);
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
