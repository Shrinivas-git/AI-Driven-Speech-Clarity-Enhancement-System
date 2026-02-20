# Abstract (Concise - For Report First Page)

---

Speech disfluencies including stuttering, repetitions, filler words, and grammatical errors significantly impact communication effectiveness. This research presents an AI-powered speech clarity enhancement system that automatically corrects speech disfluencies using a three-stage deep learning pipeline: (1) OpenAI Whisper ASR for speech-to-text transcription, (2) intelligent text cleaning with grammar correction using rule-based NLP and a custom Conv1D autoencoder for audio enhancement, and (3) TTS synthesis for fluent speech generation.

The system implements a comprehensive fluency metrics framework measuring word repetitions, filler words, pauses, grammar errors, and overall fluency score. Experimental results demonstrate 28.6% average fluency improvement, 100% repetition removal accuracy, and 95%+ filler word reduction effectiveness. The grammar correction module successfully identifies and corrects 11 distinct error patterns with 100% validation accuracy.

Implemented as a production-ready web application using FastAPI backend, React frontend, and MySQL database, the system features JWT authentication, role-based access control, subscription management, usage tracking, and comprehensive analytics dashboard. The system processes multiple audio formats with 15-30 seconds average processing time per minute of audio.

This research demonstrates practical application of AI for communication enhancement, with applications in education, professional development, content creation, and assistive technology. The explainable metrics and modular architecture facilitate academic evaluation and future research extensions.

**Keywords:** Speech Enhancement, Deep Learning, ASR, NLP, Fluency Metrics, Web Application

---

**Word Count:** ~200 words (suitable for abstract page)
