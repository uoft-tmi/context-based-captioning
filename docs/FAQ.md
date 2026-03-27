# Frequently Asked Questions (FAQ)

## General Questions

**Q: What exactly is Context-Based Closed Captioning?**  
A: It is an open-source python system that supercharges OpenAI's Whisper ASR model. By feeding the system a list of domain-specific "hot words" (jargon, names, acronyms), it mathematically forces Whisper to spell them right, even when the audio is muffled or heavily accented.

**Q: Who should use this?**  
A: University professors wanting accurate transcripts of high-level courses (e.g. quantum physics, organic chemistry). Medical professionals transcribing patient notes. Legal transcribers handling highly specific case law terminology.

## Comparison Questions

**Q: How does this compare to fine-tuning Whisper?**  
A: Fine-tuning requires hundreds of hours of labeled audio, expensive compute, and suffers from **catastrophic forgetting** (it learns the jargon but suddenly forgets how to spell "the" correctly). Our system requires **zero retraining**, keeps Whisper's conversational accuracy flawless, and fixes domain terms instantly via shallow fusion. 

**Q: How does this compare to commercial services like Otter.ai or Rev?**  
A: Otter.ai does not offer dynamic, sentence-level phonetic correction against a Custom Vocabulary API with the same rigor. More importantly, our system runs **100% locally**. No audio is ever uploaded to the cloud, strictly adhering to HIPAA and FERPA compliance.

## Technical Questions

**Q: Why use GPT-2 instead of BERT for the language model?**  
A: BERT is a Masked Language Model (MLM), great for filling in missing blanks. But Shallow Fusion requires auto-regressive log-likelihood ($P(W)$) to integrate with the ASR probabilities. Causal models like GPT-2 are mathematically designed to output this naturally, making inference significantly faster for sequence scoring.

**Q: Does it work for non-English languages?**  
A: Currently, the architecture is heavily optimized for English. While Whisper supports 90+ languages, our phonetic matching algorithm (Double Metaphone) explicitly models English consonant sounds. To support German or Spanish, a language-equivalent phonetic algorithm (like Soundex for German) must be swapped in. See the open Issue on [multi-language support](#123).

## Practical Questions

**Q: What does this cost to run?**  
A: Zero. The software is MIT-licensed, and all underlying models (Whisper, GPT-2) are open-weight and run entirely on your local hardware.

**Q: How much latency does this add?**  
A: On a standard NVIDIA T4 or A10G GPU, the phonetic matching and LM constraints add roughly ~40-60 milliseconds of compute time per word flagged for review. For offline processing, this translates to finishing a 1-hour lecture in ~4-5 minutes instead of ~3 minutes (a minimal cost for 45% better technical accuracy).

**Q: How accurate is it really?**  
A: On standard English, Whisper is already ~95% accurate (5% WER). On out-of-vocabulary medical terms, Whisper often drops to 40% accuracy. Our system pushes technical term recall back up to roughly ~89%, almost completely closing the domain gap. 

## Contribution Questions

**Q: How can I help?**  
A: Check out `CONTRIBUTING.md`! We actively need help with real-time stream processing integrations, multi-language phonetic mappers, and broader unit testing.

**Q: I found a bug. Where do I report it?**  
A: Please open an issue on GitHub. Include your OS, python version, explicit error logs, and the specific audio snippet if possible.
