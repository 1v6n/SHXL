# Pull Request Description

### **TL;DR**

[Provide a brief summary of the purpose of this pull request. For example: “This PR adds the official game handbook and Cucumber feature files that define the expected behavior of Secret Hitler XL mechanics.”]

---

### Type of Change

*Indicate the nature of your PR by selecting the corresponding conventional commit prefix:*

* [ ] `fix:` 🐛 Bug fix (non-breaking change that fixes an issue)
* [ ] `feat:` ✨ New feature (non-breaking change that adds functionality)
* [ ] `perf:` ⚡ Performance improvement
* [ ] `refactor:` 🔧 Code change that neither fixes a bug nor adds a feature
* [ ] `docs:` 📝 Documentation-only changes
* [ ] `test:` 🧪 Adding or updating tests
* [ ] `style:` 💄 Changes that do not affect meaning (e.g. formatting, whitespace)
* [ ] `chore:` 🔨 Maintenance changes (build system, tooling, CI config, etc.)
* [ ] `build:` 📦 Changes that affect the build system or external dependencies
* [ ] `ci:` 🤖 Changes to CI/CD workflows
* [ ] `revert:` ⏪ Reverts a previous commit
* [ ] `tooling:` 🛠 Adds automation utilities for strategy evaluation
* [ ] `BREAKING CHANGE:` 💥 Any change that breaks existing functionality

The most significant nature of the PR should be whats in the title

---

### **Description**

Clearly describe the contents and changes introduced by this PR. For example:

- Full **game handbook** in markdown format covering rules, phases, factions, policies, and powers.
- Structured **Cucumber `.feature` files** covering the following mechanics:
  - Election Tracker reset logic
  - Legislative and Executive phases
  - Emergency powers, anti-policy mechanics, and win conditions
  - Setup procedures, role visibility, and voting flow

---

### **Objective**

Explain the main goal of this PR and its intended impact:
For example: *“Provide a shared foundation so all developers can implement game logic aligned with the handbook, using executable specifications as a contract.”*

---

### Checklist

_Example:_

- [ ] Handbook added and properly formatted in markdown
- [ ] `.feature` files included for key game mechanics
- [ ] Scenarios cover election flow, policy enactment, and powers
- [ ] All logic aligned with official handbook
- [ ] Ready for integration into CI/testing pipeline

---

### Testing

- [ ] Unit tests pass (`make test`)
- [ ] Cucumber tests pass (`behave`)
- [ ] Manual gameplay test completed

---

### 🖼️ Screenshots (if applicable)

_Add relevant screenshots if they help illustrate the changes._

---

### 💬 Additional Notes

_Add any additional information, design decisions, known issues, or suggestions for reviewers._

---

### 🔗 Related Issues / Closes

- Closes #12
- Closes #15
- Fixes #18
- Resolves #20

---

### 📂 Target Branch

Example: `develop` (Git Flow)
