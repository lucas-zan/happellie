# HappyEllie AI Configuration Guide

## Minimum required backend settings

Edit `backend/.env` and set:

```env
AI_API_KEY=your_key
AI_BASE_URL=your_openai_compatible_base_url
AI_DEFAULT_MODEL=your_model_name
```

Examples:

- Alibaba DashScope compatible mode:
  - `AI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1`
- Volcano Ark / other compatible gateways:
  - use the base URL shown in your console

## Optional per-stage model overrides

```env
AI_PLANNER_MODEL=...
AI_GENERATOR_MODEL=...
AI_PROFILE_MODEL=...
```

Recommended approach:
- planner: cheaper / faster model
- generator: main content model
- profile: cheaper / medium model

## Optional cost settings for admin analysis

```env
AI_INPUT_COST_PER_MILLION=0.2
AI_OUTPUT_COST_PER_MILLION=2.0
```

These values are used only for internal cost tracking in the admin panel.

## Fallback behavior

```env
AI_ENABLE_FALLBACK=true
```

- `true`: if the provider fails, HappyEllie falls back to local deterministic logic
- `false`: provider errors surface directly

## TTS

This version keeps TTS disabled by default:

```env
TTS_PROVIDER=disabled
```

You can leave it as-is.
