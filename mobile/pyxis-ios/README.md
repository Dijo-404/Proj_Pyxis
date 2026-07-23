# Pyxis for iOS (native SwiftUI)

A fully native SwiftUI counterpart to the React Native reviewer app in
`mobile/pyxis/`, with 1:1 feature parity — same screens, same flows, same
backend, adapted to iOS Human Interface Guidelines.

> **Pyxis** is a local-first financial compliance and risk-triage platform.
> This app is the compliance reviewer's mobile workspace: it lists risk cases,
> shows each customer's Adaptive Financial Twin, the Gemma investigation, the
> scenario/evidence analysis, an isolated per-customer agent sandbox, and lets a
> human reviewer record the final decision and generate a report.

## Requirements

- Xcode 16 or newer (the project uses file-system-synchronized groups,
  `objectVersion = 77`).
- iOS 16.0+ deployment target, Swift 5.9+.
- The Pyxis FastAPI backend running locally (see the repo root `README.md`).
  The iOS Simulator reaches it at `http://127.0.0.1:8000` — the same base URL
  the RN app uses on the Simulator.

## Open & run

```bash
open mobile/pyxis-ios/Pyxis.xcodeproj
# then Cmd-R to run on an iOS 16+ Simulator
```

Start the backend first (from the repo root):

```bash
uvicorn backend.app.main:app --reload
python scripts/seed_database.py   # if you haven't seeded yet
```

### Running on a physical device

The backend is HTTP on your Mac's LAN. Set the API base URL either via the
`PyxisAPIBaseURL` key in `Pyxis/Info.plist` (e.g. `http://192.168.1.20:8000/api/v1`)
or the `PYXIS_API_BASE_URL` scheme environment variable. `NSAllowsLocalNetworking`
is enabled so local HTTP works without disabling App Transport Security globally.

### Regenerating the project (optional)

The committed `Pyxis.xcodeproj` builds directly. If you'd rather regenerate it:

```bash
brew install xcodegen
cd mobile/pyxis-ios && xcodegen generate
```

## Tests

```bash
xcodebuild test -scheme Pyxis -destination 'platform=iOS Simulator,name=iPhone 15'
```

Unit tests cover the view-model / business logic that has no UI dependency:
risk-band thresholds, the workspace decoder + `mapCase` mapping (including the
"missing sandbox throws" guard and status mapping), the `AuthStore` validation
and reviewer-matching rules, and `WorkspaceStore` load/error handling (driven by
a `URLProtocol` stub, no live backend needed).

## Architecture

MVVM with `ObservableObject` stores, mirroring the RN app's layer boundaries so
the two codebases stay conceptually mirrored:

```
Pyxis/
  PyxisApp.swift            App entry + lightweight DI (manual init injection)
  Theme/                    Design tokens (1:1 port of theme.ts) + riskBand
  Models/                   Domain + Sandbox types (port of types.ts)
  Networking/               APIClient (URLSession + async/await) + WorkspaceDTO
                            (raw wire shapes + mapCase, port of api.ts)
  State/                    WorkspaceStore, AuthStore, apiClient environment key
  Navigation/               Router (NavigationStack coordinator) + RootView
  Components/               Icon (FA/Feather → SF Symbols), UI primitives,
                            FlowLayout, floating BottomNav
  Screens/                  One file per screen (+ CaseDecisionTab)
```

### Screen parity

| React Native screen        | SwiftUI screen              |
| -------------------------- | --------------------------- |
| `LoginScreen`              | `LoginScreen`               |
| `DashboardScreen`          | `DashboardScreen`           |
| `CustomerRiskScreen`       | `CustomerRiskScreen`        |
| `ProfileScreen`            | `ProfileScreen`             |
| `CaseQueueScreen`          | `CaseQueueScreen`           |
| `CaseDetailScreen` (6 tabs)| `CaseDetailScreen` + `CaseDecisionTab` |
| `AskGemmaScreen`           | `AskGemmaScreen`            |
| `SandboxScreen`            | `SandboxScreen`             |

### API parity

Same endpoints, base URL, request/response shapes and error handling as
`mobile/pyxis/src/api.ts`:

- `GET /workspace/bootstrap`
- `POST /cases/{id}/ask-gemma`
- `POST /cases/{id}/review`
- `POST /reports/{id}/generate`

### iOS adaptations (HIG)

- FontAwesome/Feather icons → **SF Symbols** (`Components/Icon.swift`).
- RN's custom back-button headers → native `NavigationStack` bars with swipe-back.
- The node-tap anomaly dialog → a native **sheet** with detents.
- The hand-drawn RN charts (bar chart, score dial, branch graph, money flow) are
  reproduced natively with SwiftUI `Shape`/`Canvas`/`Layout` — no third-party
  charting dependency (the RN app used none either).
- One reachability fix: the RN `CaseQueueScreen` was fully built but unreachable
  (the Dashboard's `onOpenQueue` was wired but never surfaced). Here the
  Dashboard's "Open risk cases" tile opens the queue, honoring that wired intent.

## Note on building from this checkout

This codebase was authored on Linux, where Xcode/the iOS Simulator are not
available, so it has **not** been compiled here. It targets Xcode 16 / iOS 16
and is structured to open and build on macOS. Open it on a Mac and run to
verify; any residual project-file nit can be regenerated via `xcodegen generate`
(see above).
