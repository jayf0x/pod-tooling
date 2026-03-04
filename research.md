# Current AI list

### Qwen3: 4B-thinking-2507-fp16

- Small, smart, tuned for step-by-step logic.
- Lightweight, efficient, solid math skills.
- Limited world knowledge and nuance.

### spooknik/hermes-2-pro-mistral-7b:q8

- Mistral base with strong instruction tuning.
- Polite, verbose, good for chat + logic.
- A bit wordy; can overexplain.

### Yi: 9B-chat-v1.5-q6_K

- Sharp instruction-following, multilingual.
- Balanced, clean responses with minimal fluff.
- Not playful; a bit stiff in tone.

### Qwen2.5: 7B-instruct-q4_K_M

- Logical, structured, and fast in 4-bit.
- Better than older Qwen at consistency.
- Can sound dry or mechanical.

### Phi-3: latest

- Tiny, fast, trained on synthetic reasoning.
- Good at short logic chains and basic math.
- Poor memory and general knowledge.

### DeepSeek-Coder: latest

- Strong at code tasks, large context.
- Precise and quiet—no fluff.
- Not good for general chat.

### LLaMA 3: latest

- Strong all-rounder; great alignment.
- Clean outputs, low hallucination.
- Formal tone, less flexible reasoning control.

### Reka Flash 3

- Reasoning tags + budget = controllable CoT.
- 32K context, trained from scratch, RLOO RLHF.
- Ideal for logic-heavy tasks, not casual chat.

## Links

- Models: https://artificialanalysis.ai/leaderboards/models?open_weights=open_source&size_class=small
- diarization can be all local: https://github.com/pyannote/pyannote-audio
- advanced audio detection (eg. emotions): https://medium.com/behavioral-signals-ai/intro-to-audio-analysis-recognizing-sounds-using-machine-learning-20fd646a0ec5

## Why Use `llama.cpp` (Instead of Ollama or Similar Wrappers)

### Full Control

- Run any `.gguf` model locally without restrictions or wrappers.
- Choose quantization levels, context size, threading, and runtime options.

### No Vendor Lock-In

- Ollama and others often use internal formats or depend on their infrastructure.
- `llama.cpp` is fully open and portable — no hidden telemetry, full offline use.

### Max Performance (If Tuned)

- Native Metal GPU acceleration on macOS (M1/M2/M3).
- Potentially faster inference with optimized settings than pre-wrapped tools.

### Privacy & Transparency

- No automatic analytics, model fetching, or background connections.
- Every byte of inference and config is under your control.

### Lightweight & Flexible

- Tiny binary, minimal dependencies.
- Easily scriptable for CLI, TUI, or integration into other tools.

### Interoperability

- Works seamlessly with other tools like:
  - LM Studio (GUI for `.gguf` models)
  - text-generation-webui (multi-backend support)
  - KoboldCPP, GPT4All, llama-cpp-python

### 🛠️ Developer & Research Friendly

- Ideal for experimenting, benchmarking, or building your own LLM tools.
- Active open-source community with rapid updates and support.
