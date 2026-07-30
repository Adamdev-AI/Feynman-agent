# Feynman Agent 🧠

A desktop AI tutor that makes you actually *prove* you understand something — not just recognize it.

Built around the **Feynman Technique**: explain a topic in your own simple words, and if you can't, that's exactly where the gaps in your understanding are hiding. This app turns that idea into an app that talks back.

---

## What it does

You tell the AI what you're learning — a school lesson, an idea, a whole unit — and it stores that as a topic in your personal knowledge base. Then it asks you to explain it back, in your own words, like you're teaching a friend.

Here's the part that makes it more than a glorified quiz app: the AI doesn't just ask pre-written questions. It reads *your* explanation, figures out what you skipped over or got fuzzy on, and asks a targeted follow-up question about that specific gap — the same way a real tutor would catch you saying "and then, uh, stuff happens" and go "wait, back up."

Over time, your topics build up into a real Knowledge Base with deep analysis on each one, so you can see how your understanding is actually progressing, not just how many questions you've answered.

## Why I built it

I was watching a video about Richard Feynman explaining his 4-step technique for learning, and it clicked — most study apps test *recall*, not *understanding*. You can memorize a definition and still not really get it. I wanted something that forces the second one.

## Tech stack

| Piece | What it's doing |
|---|---|
| **PySide6** | The desktop GUI (Python bindings for Qt/C++) |
| **Mistral AI** | The reasoning engine — generates questions, evaluates explanations, finds gaps |
| **Tavily** | Lets the AI search the web when it needs outside context on a topic |
| **SQLite** | Local storage for topics, sessions, and progress |
| **ReportLab** | Generates the PDF deep-analysis reports for your Knowledge Base |

I picked Mistral and Tavily specifically because both have generous free-tier API credits — so anyone can clone this, drop in their own key, and start learning without paying for anything.

## How it's structured

The project is split into two clear halves:

- **GUI** — everything PySide6: windows, widgets, the Reasoning Stream view, the Knowledge Base view
- **AI** — everything about talking to Mistral/Tavily and turning responses into structured data the GUI can render

Two main screens tie it together:
- **Reasoning Stream** — the live back-and-forth between you and the AI, where the actual tutoring happens
- **Knowledge Base** — every topic you've built up, with generated deep analysis and (soon) exportable PDF reports

## Getting started

```bash
git clone https://github.com/Adamdev-AI/Feynman-agent.git
cd Feynman-agent
cd Feynman
pip install -r requirements.txt
```

You'll need your own API keys for Mistral and Tavily (both offer free tiers — see [mistral.ai](https://mistral.ai) and [tavily.com](https://tavily.com)). Drop them into a `.env` file in the project root:

```env
MISTRAL_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

Then run it:

```bash
python main.py
```

## Challenges along the way

Getting the AI's responses to update the GUI live — without freezing the whole app or hammering the device's resources — was the hardest part of this build. Threading API calls properly so the interface stays responsive while Mistral is "thinking" took a good chunk of the 14 days.

## What's next

- [ ] A one-click shortcut to launch the app instantly
- [ ] Deeper per-topic explanations in the Knowledge Base
- [ ] Letting users build their own flashcards from a topic
- [ ] Polishing the PDF deep-analysis report template

## A note on this project

Built solo, in 14 days, for this hackathon. If you try it out and hit something confusing or broken, feel free to open an issue — I'm actively improving it.

---

*If the Feynman Technique is new to you: the core idea is simple. Pick a topic, explain it like you're teaching a total beginner, find the spots where you get stuck or reach for jargon, then go back and fill those gaps in. This app just automates the "find the gaps" part.*
