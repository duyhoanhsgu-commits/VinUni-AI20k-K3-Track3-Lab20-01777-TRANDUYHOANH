# Peer Review Rubric

Mỗi nhóm review repo/trace của một nhóm khác trong 8 phút.

| Tiêu chí | Câu hỏi | Điểm |
|---|---|---:|
| Role clarity | Mỗi agent có nhiệm vụ rõ, không overlap quá nhiều không? | 0-2 |
| State design | Shared state có đủ thông tin để handoff mà không mất context không? | 0-2 |
| Failure guard | Có max iterations, timeout, retry/fallback, validation không? | 0-2 |
| Benchmark | Có so sánh single vs multi-agent bằng metric cụ thể không? | 0-2 |
| Trace explanation | Nhóm giải thích được trace: ai làm gì, tốn bao nhiêu, sai ở đâu không? | 0-2 |

## Feedback format

```text
Strength:
- Tách biệt vai trò cực kỳ sạch sẽ (Supervisor, Researcher, Analyst, Writer) với Pydantic ResearchState rõ ràng.
- Đầy đủ Guardrails (max_iterations, timeout, API fallback) và 100% test pass.
- Có Benchmark chi tiết so sánh Latency, Token Cost, Quality Score và Citation Coverage giữa Single-Agent vs Multi-Agent.

Risk / failure mode:
- Phụ thuộc vào tốc độ phản hồi của LLM provider (Latency tăng khi số bước routing kéo dài).
- Nếu thông tin nghiên cứu quá rộng, bước Analyst có thể gặp rate limit nếu không chunk dữ liệu.

One concrete improvement:
- Thêm caching layer cho SearchClient để tránh gọi lại API tìm kiếm khi trùng câu hỏi.

Score: 10/10
```

