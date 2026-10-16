# Ideas from Omarchy-M4-Native

Reference inspected on 2026-10-16:
[Kb2uka/Omarchy-M4-Native](https://github.com/Kb2uka/Omarchy-M4-Native), branch
`develop` at `21023d066b2e24d19d10eb092e5b643005d8cde1`. Its hardware is J713/T8132; ours is J613/T8122. This repository does
not copy its kernel modules, firmware, tuning constants or installer.

| M4 work | Relevance to this M3 | Next action |
| --- | --- | --- |
| CPU temperature discovery | Strong: missing SMC descriptions were also our problem; TCMz maximum and sensor refresh observations agree | Retain conservative J613 sensor configuration; compare against macOS on this machine before increasing power |
| CPU idle | Their patch fixes M4 register loss and an `idle=nop` boot | No transplant: this M3 already has WFI/CPU PD with increasing usage counters |
| CPU frequency scaling | Their initial image lacked controllers/OPPs | No transplant: apple-cpufreq and schedutil are active here, with 4056/2748 MHz policy maxima |
| Predictive CPU boost guard | Useful experimental method, but M4-specific heat model and OPP tables | Do not copy thresholds or boost states; investigate CPU cooling separately |
| Speaker startup recovery | Relevant symptom: our protection daemon also had an initial startup failure | Collect repeatable J613 logs before applying any startup-order fix |
| Browser/video comparisons | Useful: compare windowed/fullscreen, actual decoder use and dropped frames | Test on our matched M3 stack; no inherited M4 performance claims |
| Shutdown fix | M4 has a board-specific boot/power issue | Test J613 shutdown before assuming the same defect |
| Signed package channel | Good model if local patches become maintained software | For now retain upstream packages and record their exact versions |

Useful reference notes:

- [Temperature](https://github.com/Kb2uka/Omarchy-M4-Native/blob/develop/docs/j713-cpu-temperature.md)
- [CPU idle](https://github.com/Kb2uka/Omarchy-M4-Native/blob/develop/docs/j713-cpu-idle.md)
- [CPU frequency](https://github.com/Kb2uka/Omarchy-M4-Native/blob/develop/docs/j713-cpufreq.md)
- [CPU boost](https://github.com/Kb2uka/Omarchy-M4-Native/blob/develop/docs/j713-cpu-boost.md)

Their results are reference evidence, not hardware qualification for this M3.
