client<llm> OpenAI {
  provider openai
  options {
    model env.BENCHMARK_MODEL
    api_key env.OPENAI_API_KEY
  }
}
