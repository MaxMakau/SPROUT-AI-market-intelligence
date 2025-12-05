import React, { useEffect, useRef, useState } from 'react';
import { Mic, Volume2 } from 'lucide-react';

// Lightweight speech input/output controls using browser Web Speech APIs.
// - onTranscript(text): called when speech recognition returns text
// - speak(text): speaks provided text via SpeechSynthesis
export default function SpeechControls({ onTranscript, speakText, lang = 'en-US' }) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  useEffect(() => {
    // Cross-browser SpeechRecognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition || null;
    if (!SpeechRecognition) return;

    const recog = new SpeechRecognition();
    recog.lang = lang || 'en-US';
    recog.interimResults = false;
    recog.maxAlternatives = 1;

    recog.onresult = (event) => {
      const t = event.results && event.results[0] && event.results[0][0] && event.results[0][0].transcript;
      if (t && onTranscript) onTranscript(t.trim());
      setListening(false);
    };

    recog.onend = () => setListening(false);
    recog.onerror = () => setListening(false);

    recognitionRef.current = recog;
    return () => {
      try { recog.abort(); } catch (e) {}
    };
  }, [onTranscript, lang]);

  function startListening() {
    const r = recognitionRef.current;
    if (!r) return window.alert('Speech recognition not supported in this browser');
    try {
      r.start();
      setListening(true);
    } catch (e) {
      // ignore start errors when already started
    }
  }

  function stopListening() {
    const r = recognitionRef.current;
    if (!r) return;
    try { r.stop(); } catch (e) {}
    setListening(false);
  }

  function speak() {
    if (!speakText) return;
    const text = speakText();
    if (!text) return;
    if (!window.speechSynthesis) return window.alert('Speech synthesis not available');
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang = lang || 'en-US';
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
  }

  return (
    <div className="flex gap-2 items-center">
      <button
        type="button"
        onClick={() => (listening ? stopListening() : startListening())}
        className={`flex items-center gap-2 px-3 py-1 rounded ${listening ? 'bg-rose-500 text-white' : 'bg-slate-200 text-slate-800'}`}
        aria-pressed={listening}
        title={listening ? 'Stop listening' : 'Speak to enter data'}
      >
        <Mic className="w-4 h-4" />
        <span className="text-sm">{listening ? 'Listening...' : 'Voice Input'}</span>
      </button>

      <button
        type="button"
        onClick={speak}
        className="flex items-center gap-2 px-3 py-1 rounded bg-slate-200 text-slate-800"
        title="Read recommendation aloud"
      >
        <Volume2 className="w-4 h-4" />
        <span className="text-sm">Read</span>
      </button>
    </div>
  );
}
