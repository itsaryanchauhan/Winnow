# Contributing to Winnow

Thanks for your interest in contributing! Winnow is open-source and welcomes all contributions.

## 🛠️ Local Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/itsaryanchauhan/Winnow.git
   cd Winnow
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

## 🌿 Branch Convention

- `main` — stable, production-ready
- `feat/your-feature` — new features
- `fix/your-fix` — bug fixes

## 📬 Submitting a PR

1. Fork the repo
2. Create a branch: `git checkout -b feat/your-feature`
3. Make your changes
4. Push and open a Pull Request against `main`
5. Describe what you changed and why

## 🐛 Reporting Issues

Open an issue on [GitHub](https://github.com/itsaryanchauhan/Winnow/issues) with:
- What you expected to happen
- What actually happened
- Steps to reproduce

## 💡 Ideas for Contribution

- New compression strategies or model integrations
- Additional framework wrappers (LlamaIndex, Haystack)
- Performance improvements
- Documentation improvements
- Benchmark expansions

---

By contributing, you agree your code will be licensed under the MIT License.
