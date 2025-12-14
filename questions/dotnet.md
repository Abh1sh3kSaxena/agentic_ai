---
id: dotnet-001
role: [backend, fullstack]
min_years: 2
max_years: 15
tags: [async, performance]
explanation: |
  In .NET, asynchronous IO uses the async/await pattern which allows the thread to be returned to the threadpool while IO completes.
  Use async when your work is IO-bound (network, disk) to improve scalability. Use synchronous code for simple CPU-bound operations.
---
Explain the difference between synchronous and asynchronous IO in .NET. When would you prefer async?

---
id: dotnet-002
role: [backend]
min_years: 4
max_years: 20
tags: [concurrency, threading]
explanation: |
  .NET offers multiple approaches to concurrency: threads, threadpool, async/await and task-based parallelism. Choose tasks/async for IO-bound work and TPL/Parallel for CPU-bound parallelism.
---
How do you approach concurrency in a high-throughput .NET backend service? Mention tradeoffs and approaches.
