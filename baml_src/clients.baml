client<llm> Gemini {
  provider google-ai
  options {
    model env.BENCHMARK_MODEL
    api_key env.GOOGLE_API_KEY
    generationConfig {
      temperature 0.1
    }
  }
}
