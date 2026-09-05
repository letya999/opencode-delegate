<p align="center">
  <a href="README.md">English</a> · <strong>Русский</strong>
</p>

<p align="center">
  <h1 align="center">OpenCode Delegate</h1>
</p>

<p align="center">
  <a href="https://github.com/letya999/opencode-delegate"><img src="https://img.shields.io/badge/статус-активен-brightgreen" alt="статус"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/лицензия-MIT-blue" alt="Лицензия: MIT"></a>
  <a href="https://skills.sh"><img src="https://img.shields.io/badge/skills.sh-доступен-black" alt="skills.sh"></a>
  <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/cli-opencode-purple" alt="CLI: opencode">
</p>

Скилл-делегат для неинтерактивного запуска OpenCode CLI (`opencode`) от [Артема Летюшева](https://github.com/letya999).

Основная команда — `scripts/delegate_opencode.py`. Главный потребитель — управляющий агент или оркестратор: каждый запуск выполняет OpenCode в ограниченном подпроцессе (`opencode run`) и возвращает структурированный JSON-конверт.

---

## Одна цель, изолированный подпроцесс, нулевое доверие

Скрипт-обёртка служит детерминированным барьером безопасности между управляющим агентом и OpenCode CLI:

- **Строго неинтерактивный запуск:** Вызывает `opencode run` напрямую через `subprocess.run(..., shell=False)` без TUI-интерфейса.
- **Провайдеро-независимость:** Поддерживает любого провайдера, настроенного в OpenCode (`openai`, `anthropic`, `ollama`, `openrouter` и др.).
- **Ограничение каталога:** Задаёт целевую рабочую директорию проекта через `--dir <cwd>`.
- **Верификация результатов:** Ответ считается непроверенным до независимой инспекции через diff и тесты.
- **Изоляция секретов:** Не считывает, не печатает и не передаёт ключи провайдеров, файлы `~/.config/opencode` или `.env`.

## Матрица возможностей

| Параметр / Возможность | Спецификация | Поведение и гарантии |
|---|---|---|
| **Команда запуска** | `opencode run "<task>"` | Неинтерактивное выполнение в режиме run |
| **Ограничение каталога** | `--dir <cwd>` | Ограничивает область действия целевой папкой проекта |
| **Выбор модели** | `--model <provider/model>` | Передаёт указанного провайдера/модель в OpenCode |
| **Форматы вывода** | Текст или `--json` | Сохраняет форматированный текст или полный JSON-поток событий |
| **Автономные правки** | `--always-approve` | Передаёт `--auto` для одобрения разрешённых операций |
| **Защита от утечки сессий** | Исключение `--share` | Никогда не публикует сессии в открытый доступ без запроса |
| **Возобновление сессий** | `--session <id>` / `--continue` | Возобновляет существующий диалог |
| **Переопределение бинарника** | Переменная `OPENCODE_BIN` | Приоритетный путь до вызова из PATH |
| **Коды возврата** | `0, 2, 65, 124, 126, 127` | Стандартизированная маршрутизация ошибок |

## Установка

Через `npx skills`:

```bash
npx skills add letya999/opencode-delegate
```

Или клонированием в каталог скиллов:

```bash
git clone https://github.com/letya999/opencode-delegate.git .agents/skills/opencode-delegate
```

## Быстрый старт

### POSIX (macOS, Linux, WSL)

```bash
python3 scripts/delegate_opencode.py \
  --cwd "$PWD" \
  --task "Проанализируй репозиторий и выдели самую критичную проблему." \
  --timeout 45m
```

### Windows PowerShell

```powershell
py -3 .\scripts\delegate_opencode.py `
  --cwd (Get-Location).Path `
  --task "Проанализируй репозиторий и выдели самую критичную проблему." `
  --timeout 45m
```

---

<details>
<summary>Схема JSON-манифеста и интеграция с агентом</summary>

Обёртка записывает `stdout.txt` (или `events.jsonl`), `stderr.log` и `result.json` во временный каталог:

```json
{
  "tool": "opencode",
  "cwd": "C:\\work\\repo",
  "exit_code": 0,
  "output_dir": "C:\\Temp\\opencode-delegate-xyz",
  "stdout": "C:\\Temp\\opencode-delegate-xyz\\stdout.txt",
  "stderr": "C:\\Temp\\opencode-delegate-xyz\\stderr.log",
  "response": "Финальный извлеченный текст ответа от OpenCode"
}
```

Если OpenCode завершился с кодом 0, но вернул пустой ответ, обёртка завершается с кодом `65`.

</details>

<details>
<summary>Флаги CLI и параметры запуска</summary>

| Флаг | Тип | Описание |
|---|---|---|
| `--cwd` | Путь (обязательный) | Рабочий каталог проекта. Код `2`, если каталог не существует. |
| `--task` | Строка (обязательный) | Текст задачи / поручения для OpenCode. |
| `--timeout` | Время (по умолчанию: `45m`) | Таймаут: `90s`, `45m`, `2h` или число секунд. |
| `--model` | Строка | Строка модели (например, `anthropic/claude-3-7-sonnet`). |
| `--json` | Флаг | Переключает захват вывода на поток событий JSON. |
| `--always-approve` | Флаг | Передаёт `--auto` для автоматического одобрения неблокирующих прав. |
| `--session` | Строка | Идентификатор сессии для возобновления. |
| `--continue` | Флаг | Продолжает последнюю сессию. |
| `--output-dir` | Путь | Каталог для сохранения логов и манифеста. |

</details>

<details>
<summary>Правила безопасности и изоляция секретов</summary>

- **Защита секретов:** Никогда не считывает и не логирует API-ключи, OAuth токены и файлы в каталоге `~/.config/opencode`.
- **Без публичного шаринга:** Никогда не передаёт `--share`, если это не запрошено явно.
- **Защита от циклов:** Делегированный OpenCode не должен запускать новые подпроцессы через обёртки.

</details>

<details>
<summary>Протокол независимой верификации</summary>

Ответы делегата не считаются окончательным доказательством. При изменении файлов:

1. Проверьте diff: `git diff --stat` и `git diff`.
2. Запустите тесты независимо: `pytest`, `npm test`, `cargo test`.
3. Проверьте добавленные файлы и импорты.

</details>

<details>
<summary>Набор тестов</summary>

Запуск тестов через стандартную библиотеку `unittest`:

```bash
python -m unittest discover -s tests -v
```

</details>

<details>
<summary>Точки входа скилла</summary>

- [SKILL.md](SKILL.md) — Спецификация инструкций для кодинг-агентов.
- [QUICKSTART.md](QUICKSTART.md) — Краткое руководство.
- [references/runtime-setup.md](references/runtime-setup.md) — Проверка окружения перед запуском.
- [references/headless-reference.md](references/headless-reference.md) — Справочник флагов OpenCode CLI.
- [.well-known/agent-skills/index.json](.well-known/agent-skills/index.json) — Индекс для каталога skills.sh.
- [dist/opencode-delegate.zip](dist/opencode-delegate.zip) — Архив скилла.

</details>

<details>
<summary>Лицензия</summary>

MIT License. См. полный текст в [LICENSE](LICENSE). Copyright (c) 2026 Artem Letyushev.

</details>
