W12D2 Advanced API Patterns — Reflection

This assignment was one of the hardest things I’ve done so far in the program — not because any single feature was impossible, but because of how many moving parts had to work together at the same time.

On paper, each requirement felt manageable: authentication, rate limiting, caching, background tasks, health checks, Docker, tests, and a frontend demo. In practice, combining all of those into one working system exposed how fragile production systems really are. A small configuration mistake (like a wrong Redis hostname, a missing environment variable, or using localhost inside Docker) could break several features at once and make it feel like “nothing is working” even though the code itself was mostly correct.

The hardest part for me was debugging across layers:

figuring out whether an issue was in my Python code, FastAPI behavior, Redis, Docker networking, environment variables, or Streamlit reruns

understanding why something worked locally but not inside containers

interpreting HTTP status codes, headers, and logs instead of just reading tracebacks

That mental overhead was exhausting, and there were definitely moments where I felt stuck, frustrated, or like I had broken everything beyond repair. I also made the assignment harder than it needed to be by adding a Streamlit frontend on top of the backend. While it helped me visualize and test the system, it also introduced another source of complexity (service-to-service URLs, container timing, reruns, etc.) that made debugging more difficult.

At the same time, this assignment taught me more than any “clean” or simplified project could have.

I learned:

how production patterns interact instead of existing in isolation

how to reason about system behavior using logs, HTTP responses, and headers

how to debug distributed systems step-by-step instead of guessing

how configuration and infrastructure can be just as important as application logic

how to stay calm and systematic when something feels completely broken

Even though it was uncomfortable, I now feel much more confident reading backend systems, understanding where failures might come from, and fixing them in a structured way instead of randomly trying things.

Overall, this was a difficult, sometimes frustrating assignment — but also one of the most valuable learning experiences I’ve had so far. It made backend systems feel real instead of theoretical, and it showed me what “production-style thinking” actually looks like in practice.