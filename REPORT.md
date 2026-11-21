# Verification & Submission Report — news-image-20261121

- **Repository URL:** https://github.com/honru09/news-image-20261121
- **Bounty URL:** https://make.fun/bounty/news-image-20261121
- **Initial Entry Commit SHA:** `a3dc908b9572a3ebb7aca133fa0889edab44ac26`
- **Report Commit SHA (HEAD prior to final SHA sync):** `2229fd72d9649628ffc26d2d2012b55048271e78`
- **Final Commit SHA (pushed HEAD):** `476ea9d52410e6d0154775b2b244994ba5fd8253`
- **Image File (`entry.png`):** 1024×1024 PNG, `119813` bytes (117.00 KiB, under 1 MiB)
- **Image SHA-256:** `6fce0cad6777576675174c353389f4761bc09008c4746e96cec876c22f9dff79`

## Determinism Verification

Ran `main.py` twice into two separate directories (`MAKEFUN_OUTPUT_DIR=out1` and `MAKEFUN_OUTPUT_DIR=out2`) and compared SHA-256 digests with `entry.png`:

```text
6fce0cad6777576675174c353389f4761bc09008c4746e96cec876c22f9dff79  entry.png
6fce0cad6777576675174c353389f4761bc09008c4746e96cec876c22f9dff79  out1/entry.png
6fce0cad6777576675174c353389f4761bc09008c4746e96cec876c22f9dff79  out2/entry.png
```

All three hashes match identically (**PASS**). `main.py` imports only Python standard library modules (`hashlib`, `os`, `shutil`, `sys`).

## What the Image Shows

`entry.png` presents a 1024×1024 newspaper front-page infographic summarizing the world news of Saturday, 21 November 2026. The masthead and lead visual banner cover Russia's largest overnight air assault on Ukraine (400+ drones and 110 missiles; some fell in Poland). Below the lead, a structured two-column dispatch grid with custom geometric icons covers the AI stock sell-off (S&P 500 and Dow down 3.7%), the ICJ ruling that Myanmar is responsible for the Rohingya genocide, the joint Trump–Xi–Putin peace declaration after the Shenzhen summit, Anthropic's sharp fall after listing, the reported breaches of the US Agriculture Department and FBI, Trump weighing new strikes on Iran, COP31 talks running past deadline, and Gen Z marches across 25 European states.
