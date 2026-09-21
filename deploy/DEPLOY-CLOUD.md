# Laya as a self-hosted decision API

Packages laya's typed-decisions checkpoint (ModernBERT-large, 421M, Apache-2.0) as a
Jev-style HTTP service: state + typed questions in, probabilities out. CPU-only — no GPU.

```bash
docker build -f deploy/Dockerfile -t laya-api .
docker run -p 8080:8080 laya-api

curl -X POST localhost:8080/decide -H "Content-Type: application/json" -d '{
  "state": "Your API started returning 502s on the payments endpoint. Checkout is down.",
  "questions": [{"type": "choice", "instructions": "Which team should handle this?",
                 "options": ["billing", "technical", "sales"]}]
}'
```

Question types: `noul` (yes/no probability), `choice` (+`options`), `score` (ordered `options`).

## Measured on a 2 vCPU / 4GB cloud container

Latency is linear at ~1.1ms per input token and very stable:

| State size | Latency |
| --- | --- |
| ~125 tokens | ~268ms |
| ~500 tokens | ~608ms |
| ~900 tokens | ~1,055ms |

Accuracy on 150 public test examples (50 each), zero-shot through this API:

| Task | Accuracy |
| --- | --- |
| AG News topics (4-way, out of domain) | **96%** |
| BoolQ yes/no | 72% |
| SST-5 sentiment | 46% exact / 94% within one level |

Profile: an excellent fast **classifier** (topics, intents, routing); weaker at passage
reading and multi-step reasoning (5/8 on a rule+exception suite where a 4B decoder
scores 8/8). Two caveats: inputs past ~1K tokens are silently truncated (keep states
short, or extend the window — the encoder RoPE-scales to 8K per upstream), and
confidence values ship miscalibrated per upstream's own ECE numbers — use them to
rank, not as probabilities of being right.

The multilingual checkpoint (`subfolder="multilingual"`, 322M, 100+ languages, ~2x
faster) drops into the same wrapper by changing one line in `deploy/app.py`.
