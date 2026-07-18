# Gemma Design

All generative reasoning runs through the provider interface in
`intelligence/gemma/providers/`. Prompts receive compact, structured evidence and
outputs must be schema-validated before use. External hosted LLMs are outside the
deployment boundary.
