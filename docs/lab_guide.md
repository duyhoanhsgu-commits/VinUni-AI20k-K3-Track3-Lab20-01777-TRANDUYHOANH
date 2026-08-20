# Lab Guide: Multi-Agent Research System

## Scenario

Bạn cần xây dựng một research assistant có thể nhận câu hỏi dài, tìm thông tin, phân tích và viết câu trả lời cuối cùng. Lab yêu cầu so sánh hai cách làm:

1. **Single-agent baseline**: một agent làm toàn bộ.
2. **Multi-agent workflow**: Supervisor điều phối Researcher, Analyst, Writer.

## Quy tắc quan trọng

- Không thêm agent nếu không có lý do rõ ràng.
- Mỗi agent phải có responsibility riêng.
- Shared state phải đủ rõ để debug.
- Phải có trace hoặc log cho từng bước.
- Phải benchmark, không chỉ nhìn output bằng cảm tính.

## Milestone 1: Baseline

File gợi ý:

- `src/multi_agent_research_lab/cli.py`
- `src/multi_agent_research_lab/services/llm_client.py`

TODO(student): thay baseline placeholder bằng một call LLM thật.

## Milestone 2: Supervisor

File gợi ý:

- `src/multi_agent_research_lab/agents/supervisor.py`
- `src/multi_agent_research_lab/graph/workflow.py`

TODO(student): implement routing policy.

Gợi ý câu hỏi thiết kế:

- Khi nào gọi Researcher?
- Khi nào gọi Analyst?
- Khi nào gọi Writer?
- Khi nào stop?
- Nếu agent fail thì retry hay fallback?

## Milestone 3: Worker agents

File gợi ý:

- `src/multi_agent_research_lab/agents/researcher.py`
- `src/multi_agent_research_lab/agents/analyst.py`
- `src/multi_agent_research_lab/agents/writer.py`

TODO(student): implement từng worker.

## Milestone 4: Trace và benchmark

File gợi ý:

- `src/multi_agent_research_lab/observability/tracing.py`
- `src/multi_agent_research_lab/evaluation/benchmark.py`
- `src/multi_agent_research_lab/evaluation/report.py`

Benchmark tối thiểu:

| Metric | Cách đo gợi ý |
|---|---|
| Latency | wall-clock time |
| Cost | token usage hoặc provider usage |
| Quality | rubric 0-10 do peer review |
| Citation coverage | số claims có source / tổng claims chính |
| Failure rate | số query fail / tổng query |

## Troubleshooting

### macOS: lỗi SSL certificate khi gọi API qua HTTPS (Tavily, OpenAI, ...)

Triệu chứng: khi implement `SearchClient` (hoặc bất kỳ HTTPS call nào) trên macOS, bạn có thể gặp lỗi kiểu:

```
ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed:
unable to get local issuer certificate
```

Nguyên nhân: Python cài từ python.org trên macOS **không dùng** certificate store của hệ điều hành, nên không tìm thấy CA bundle hợp lệ. Đây là lỗi môi trường, **không phải** do API key sai.

Cách khắc phục (chọn 1 trong 3):

1. **Chạy script cài certificate đi kèm Python** (nhanh nhất):

   ```bash
   /Applications/Python\ 3.12/Install\ Certificates.command
   ```

   (thay `3.12` bằng version Python của bạn)

2. **Dùng `certifi` trong code** — thêm `certifi` vào dependencies, rồi tạo SSL context khi gọi HTTPS:

   ```python
   import certifi
   import ssl
   from urllib.request import urlopen

   ssl_context = ssl.create_default_context(cafile=certifi.where())
   urlopen(request, timeout=timeout, context=ssl_context)
   ```

3. **Set biến môi trường** trỏ tới CA bundle của certifi (không cần đổi code):

   ```bash
   export SSL_CERT_FILE=$(python -m certifi)
   ```

## Exit ticket

### 1. Case nào nên dùng multi-agent? Vì sao?
- **Trường hợp áp dụng**: Các bài toán phức tạp, quy trình gồm nhiều công đoạn đòi hỏi chuyên môn riêng biệt (ví dụ: Thu thập thông tin $\rightarrow$ Phân tích luận điểm $\rightarrow$ Tổng hợp báo cáo gán trích dẫn).
- **Lý do**: 
  - **Tách biệt trách nhiệm (Separation of Concerns)**: Mỗi agent tập trung vào đúng vai trò chuyên biệt với system prompt và context tối ưu, giúp giảm hallucination.
  - **Khả năng mở rộng & Guardrails**: Dễ dàng đặt giới hạn (`max_iterations`, `timeout`), retry/fallback và kiểm soát chất lượng độc lập ở từng node.
  - **Tránh tràn context**: Handoff dữ liệu qua Pydantic State giúp giữ lại thông tin cốt lõi mà không bị trôi dữ liệu như khi dồn vào 1 single prompt dài.

### 2. Case nào không nên dùng multi-agent? Vì sao?
- **Trường hợp không nên áp dụng**: Các tác vụ đơn giản, phản hồi tức thì (ví dụ: trả lời FAQ, sửa lỗi chính tả, dịch thuật ngắn, hoặc câu hỏi 1 bước).
- **Lý do**:
  - **Độ trễ (Latency) & Chi phí (Cost) cao**: Multi-Agent gọi nhiều vòng LLM và thực hiện handoff qua lại làm tăng độ trễ và lượng token tiêu thụ.
  - **Phức tạp hóa không cần thiết (Over-engineering)**: Tăng rủi ro gãy luồng, lặp vô hạn (infinite loop) hoặc lỗi mất dấu state nếu quy trình không đủ phức tạp để chia nhiều agent.

