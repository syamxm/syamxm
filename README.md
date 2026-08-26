<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/wordmark-dark.svg">
  <img alt="SYAMXM" src="assets/wordmark-light.svg" width="420">
</picture>

```console
syamxm@cachyos ~> whoami

  Ahmad Syamim — syamxm

syamxm@cachyos ~> cat about.txt

  Ahmad Syamim — final-year Computer Science (Hons) student at UiTM Shah
  Alam, DevSecOps specialisation. DevOps intern from 7 September 2026.

  I self-host everything I ship: the code, the pipeline, and the box it
  runs on. Nine services in front of the public internet, no open inbound
  ports — everything goes through Cloudflare Tunnel or Tailscale.

  Infrastructure that is defensible, not decorative.

syamxm@cachyos ~> env | grep -E 'ROLE|HOST|SHELL'

  ROLE    student · devops intern
  HOST    debian homeserver
  SHELL   fish
```

### `syamxm@cachyos ~> ls ~/projects`

| Project | What it does | Stack |
| --- | --- | --- |
| **[beanthere](https://github.com/syamxm/beanthere)** · [live](https://beanthere.syamxm.com) | Coffee-shop platform — online ordering, loyalty tiers, drink recommender running on a local Ollama model on a 4 GB GPU. Every deploy gated by a six-stage pipeline that fails closed. | PHP 8.2 · MariaDB · Ollama · Trivy |
| **[debian-watch](https://github.com/syamxm/debian-watch)** · [live](https://debian-watch.syamxm.com) | Homeserver monitoring — per-core CPU, memory, disks, network, temperatures, containers. Never mounts the Docker socket; reads through an nginx allowlist that forwards two endpoints and 403s the rest. Collectors degrade independently, so a dead sensor hides one panel instead of the app. | Go · HTMX · CodeQL · govulncheck |
| **[taskflow](https://github.com/syamxm/taskflow)** · [live](https://taskflow.syamxm.com) | MERN task manager. Five scanners — Semgrep SAST, Gitleaks, and Trivy across SCA, image and IaC — block the deploy on HIGH or CRITICAL. | MERN · GitHub Actions · JWT |
| **[cv-api-spring](https://github.com/syamxm/cv-api-spring)** · [live](https://cv-spring.syamxm.com) | My CV rebuilt on Spring Boot to learn the ecosystem properly. JSON is byte-for-byte identical to the Node API so the two can be diffed. One Thymeleaf template renders the page, the PDF and its A4 previews. 55 tests on Testcontainers. | Java 21 · Spring Boot 3.5 · Postgres · Flyway |
| **[cipher-agent](https://github.com/syamxm/cipher-agent)** · [live](https://cipher-agent.syamxm.com) | RSA spy game in a fake browser terminal — solo cipher missions plus a two-player one-time-pad channel. Hardened non-root container. | Python · FastAPI · pytest |
| **[cv-api](https://github.com/syamxm/cv-api)** · [live](https://cv.syamxm.com) | My CV as data — REST API serving resume JSON. Actions deploys over Tailscale SSH, published through a Cloudflare Tunnel. | Node · Express · Postgres |

Also: **[cipher-forge](https://github.com/syamxm/cipher-forge)** ([live](https://cipher-forge.syamxm.com)) RSA teaching game, solved by hand stage by stage ·
**[student_reminder_system](https://github.com/syamxm/student_reminder_system)** Flutter timetable and deadline reminders, FastAPI backend with bcrypt auth and Redis-rate-limited login ·
**[c-aegis-landing](https://github.com/syamxm/c-aegis-landing)** ([live](https://c-aegis.syamxm.com)) landing page for my final-year Android project, no framework, no build step ·
**[syamxm.com](https://github.com/syamxm/syamxm.com)** ([live](https://syamxm.com)) portfolio, vanilla HTML/CSS/JS

Grafana, Prometheus and Loki run the observability stack behind Cloudflare Access.
That repo is private — happy to walk through it.

### `syamxm@cachyos ~> cat learning.txt`

```console
  Currently studying Kubernetes and GitLab CI.
  Neither is in shipped work yet.
```

### `syamxm@cachyos ~> cat contact.txt`

[Portfolio](https://syamxm.com) · [CV](https://cv.syamxm.com) · [LinkedIn](https://www.linkedin.com/in/syamxm) · [Email](mailto:ahmadsyamim200@gmail.com)

### `syamxm@cachyos ~> git log --stat`

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/syamxm/syamxm/output/streak.svg">
  <img alt="GitHub streak stats" src="https://raw.githubusercontent.com/syamxm/syamxm/output/streak-light.svg">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/syamxm/syamxm/output/github-contribution-grid-snake-dark.svg">
  <img alt="contribution snake" src="https://raw.githubusercontent.com/syamxm/syamxm/output/github-contribution-grid-snake.svg">
</picture>
