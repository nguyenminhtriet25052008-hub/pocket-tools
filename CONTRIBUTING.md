# Contributing

Thanks for wanting to help! The whole point of this repo is **small, useful, dependency-free**, so the rules are short:

1. **Standard library only.** If it needs `pip install`, it doesn't belong here.
2. **Small.** Aim for ~50 lines, hard ceiling ~90. One file per tool in `tools/`.
3. **Useful.** It should solve a real, recurring annoyance.
4. **Safe.** Anything that deletes/moves/renames must preview by default and require a flag (e.g. `--apply`).
5. **Testable.** Keep the logic in plain functions; keep `argparse` in `main()`. Add tests to `tests/test_tools.py`.
6. **Cross-platform.** Must work on Windows, macOS and Linux (CI checks all three).

```bash
python -m unittest discover -s tests -v
```

Then add a row to the tool table in `README.md` and open a PR. 🙌
