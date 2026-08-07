# Designing and Building AI Agents | تصميم وبناء وكلاء الذكاء الاصطناعي

## Introduction | مقدمة

This workshop introduces agent design step by step using Python and the OpenAI
Agents SDK. The first example creates a simple agent with one tool and no memory.
The next example adds a persistent session so the agent can remember previous
conversations. A third example adds tools for reading and renaming files.
A fourth example shows how to select a model and configure its behavior.
A fifth example introduces input and output guardrails.

تقدم هذه الورشة تصميم وكلاء الذكاء الاصطناعي خطوة بخطوة باستخدام بايثون وOpenAI Agents
SDK. ينشئ المثال الأول وكيلاً بسيطاً بأداة واحدة ومن دون ذاكرة، ثم يضيف المثال
التالي جلسة دائمة تمكّن الوكيل من تذكّر المحادثات السابقة. ويضيف مثال ثالث
أدوات لقراءة الملفات وإعادة تسميتها.
ويوضح مثال رابع كيفية اختيار النموذج وضبط سلوكه.
ويقدم مثال خامس ضوابط الإدخال والإخراج.

## Setup | الإعداد

### 1. Install Python | تثبيت بايثون

The [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) requires
Python 3.10 or newer. Install the latest stable version of Python 3 for your
operating system.

تتطلب حزمة OpenAI Agents SDK الإصدار 3.10 من بايثون أو إصداراً أحدث. ثبّت أحدث
إصدار مستقر من Python 3 لنظام التشغيل لديك.

#### Windows | ويندوز

1. Open the [Python downloads for Windows](https://www.python.org/downloads/windows/).
2. Download the latest stable 64-bit installer and run it.
3. Enable **Add Python to PATH** if the installer displays that option.
4. Open PowerShell or Command Prompt and verify the installation:

1. افتح صفحة [تنزيل بايثون لنظام ويندوز](https://www.python.org/downloads/windows/).
2. نزّل أحدث إصدار مستقر بنواة 64 بت، ثم شغّل ملف التثبيت.
3. فعّل خيار **Add Python to PATH** إذا ظهر في برنامج التثبيت.
4. افتح PowerShell أو موجه الأوامر وتحقق من التثبيت:

```powershell
py --version
```

#### macOS | ماك

1. Open the [Python downloads for macOS](https://www.python.org/downloads/macos/).
2. Download and run the installer for the latest stable Python 3 release.
3. Open Terminal and verify the installation:

1. افتح صفحة [تنزيل بايثون لنظام macOS](https://www.python.org/downloads/macos/).
2. نزّل برنامج تثبيت أحدث إصدار مستقر من Python 3 وشغّله.
3. افتح الطرفية وتحقق من التثبيت:

```bash
python3 --version
```

### 2. Create a virtual environment | إنشاء بيئة افتراضية

Open a terminal inside the workshop folder, then run the command for your system.
A virtual environment keeps this project's packages separate from other Python
projects.

افتح الطرفية داخل مجلد الورشة، ثم نفّذ الأمر المناسب لنظامك. تحافظ البيئة
الافتراضية على حزم هذا المشروع منفصلة عن مشاريع بايثون الأخرى.

On Windows:

على ويندوز:

```powershell
py -m venv .venv
```

On macOS:

على macOS:

```bash
python3 -m venv .venv
```

### 3. Activate the virtual environment | تفعيل البيئة الافتراضية

Activate the environment every time you open a new terminal for this project.

فعّل البيئة في كل مرة تفتح فيها طرفية جديدة لهذا المشروع.

Windows PowerShell | ويندوز PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, run the following command once and
then try activation again:

إذا منع PowerShell تشغيل ملف التفعيل، نفّذ الأمر التالي مرة واحدة، ثم حاول
التفعيل من جديد:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Windows Command Prompt | موجه أوامر ويندوز:

```bat
.venv\Scripts\activate.bat
```

macOS Terminal | طرفية macOS:

```bash
source .venv/bin/activate
```

When activation succeeds, `(.venv)` usually appears at the beginning of the
terminal prompt.

عند نجاح التفعيل، تظهر عادةً كلمة `(.venv)` في بداية سطر الطرفية.

### 4. Install the required packages | تثبيت الحزم المطلوبة

With the virtual environment active, upgrade `pip` and install the packages from
`requirements.txt`:

بعد تفعيل البيئة الافتراضية، حدّث `pip` وثبّت الحزم الموجودة في ملف
`requirements.txt`:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The requirements file installs the OpenAI Agents SDK and `python-dotenv`.

يثبّت ملف المتطلبات حزمة OpenAI Agents SDK وحزمة `python-dotenv`.

### 5. Set the OpenAI API key | إعداد مفتاح OpenAI

Make a copy of `.env.example` and name the copy `.env`.

أنشئ نسخة من ملف `.env.example` وغيّر اسم النسخة إلى `.env`.

On Windows PowerShell:

على Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

On Windows Command Prompt:

على موجه أوامر ويندوز:

```bat
copy .env.example .env
```

On macOS:

على macOS:

```bash
cp .env.example .env
```

Open `.env` and set your OpenAI API key:

افتح ملف `.env` وأضف مفتاح OpenAI الخاص بك:

```dotenv
OPENAI_API_KEY=your_openai_api_key
```

Keep this key private. The `.env` file is excluded from Git and must not be
committed.

حافظ على سرية المفتاح. ملف `.env` مستبعد من Git ويجب عدم رفعه إلى المستودع.

When you finish working, leave the virtual environment with:

عند الانتهاء من العمل، اخرج من البيئة الافتراضية باستخدام:

```bash
deactivate
```

## Python files | ملفات بايثون

All agent examples use the same general `File Assistant` name and instructions.
The available tools change between learning stages, while later examples add one
focused concept, such as sessions or model settings, without changing the general
instructions.

تستخدم جميع أمثلة الوكيل الاسم العام `File Assistant` والتعليمات العامة نفسها.
تتغير الأدوات المتاحة بين المراحل التعليمية، بينما تضيف الأمثلة اللاحقة مفهوماً
محدداً، مثل الجلسات أو إعدادات النموذج، من دون تغيير التعليمات العامة.

### `agent.py`

The first agent-design example. It creates a file assistant with one tool,
`list_folder`, which lists the contents of a folder. Each request is independent,
so this agent does not remember earlier conversations.

هذا هو المثال الأول لتصميم الوكيل. ينشئ مساعداً للملفات يمتلك أداة واحدة اسمها
`list_folder` لعرض محتويات المجلد. كل طلب مستقل، لذلك لا يتذكر هذا الوكيل
المحادثات السابقة.

Run it with:

شغّله باستخدام:

```bash
python agent.py
```

### `agent_session.py`

This example adds a persistent `SQLiteSession`. Conversation history is saved in
`history.db`, allowing the agent to remember information after it is closed and
started again. For example, it can remember your name when the same session is
reopened.

يضيف هذا المثال جلسة `SQLiteSession` دائمة. يُحفظ سجل المحادثة في ملف
`history.db`، مما يسمح للوكيل بتذكّر المعلومات بعد إغلاقه وتشغيله مرة أخرى.
على سبيل المثال، يمكنه تذكّر اسمك عند فتح الجلسة نفسها من جديد.

Run it with:

شغّله باستخدام:

```bash
python agent_session.py
```

### `agent_tools.py`

This example keeps `list_folder` and adds two tools: `read_file` reads the content
of a text file, and `rename_file` changes its name. The agent can now handle both
folder-listing requests and requests to read files and rename them based on their
content, while preserving extensions and avoiding duplicate names.

يحتفظ هذا المثال بأداة `list_folder` ويضيف أداتين: تقرأ `read_file` محتوى الملف
النصي، وتغيّر `rename_file` اسمه. يستطيع الوكيل الآن تنفيذ طلبات عرض محتويات
المجلد، وكذلك قراءة الملفات وإعادة تسميتها بناءً على محتواها، مع الحفاظ على
الامتدادات وتجنّب الأسماء المكررة.

Run it with:

شغّله باستخدام:

```bash
python agent_tools.py
```

### `agent_model.py`

This example keeps the same tools and demonstrates two model configurations:

- The active configuration selects `gpt-5.6-sol` and sets its reasoning effort
  to `medium`.
- The commented alternative selects `gpt-4.1` and sets `temperature=0.9` for
  more varied and creative responses.

The `model` value chooses the model. `reasoning.effort` controls how much
reasoning a supported reasoning model performs. `temperature` controls output
randomness and variation on models that support it. `frequency_penalty` is a
different setting that discourages repeated words or phrases; it is not the
creativity control. Not every model supports every setting.

يحتفظ هذا المثال بالأدوات نفسها، ويوضح إعدادين للنموذج:

- يختار الإعداد الفعّال `gpt-5.6-sol` ويضبط مستوى الاستدلال على `medium`.
- يختار الإعداد البديل المكتوب كتعليق `gpt-4.1` ويضبط `temperature=0.9`
  للحصول على إجابات أكثر تنوعاً وإبداعاً.

تحدد قيمة `model` النموذج المستخدم. ويتحكم `reasoning.effort` في مقدار الاستدلال
الذي يجريه النموذج الداعم لهذه الخاصية، بينما تتحكم `temperature` في عشوائية
الإجابة وتنوعها لدى النماذج التي تدعمها. أما `frequency_penalty` فهو إعداد مختلف
يقلل تكرار الكلمات أو العبارات، وليس إعداد الإبداع. لا تدعم جميع النماذج كل
الإعدادات.

Run it with:

شغّله باستخدام:

```bash
python agent_model.py
```

### `agent_guardrails.py`

This example adds two simple guardrails to the file assistant:

- The input guardrail checks the user's request. It blocks destructive words such
  as `delete` before the agent or its tools start.
- The output guardrail checks the agent's final response. It blocks the response
  if it contains a sensitive marker such as `secret` or `password`.

When a check fails, its `tripwire` is triggered. The runner raises either
`InputGuardrailTripwireTriggered` or `OutputGuardrailTripwireTriggered`, and the
program catches the exception and prints a clear message. The keyword checks are
intentionally simple for teaching; production guardrails usually need rules that
match the application's actual risks and data.

يضيف هذا المثال ضابطين بسيطين إلى مساعد الملفات:

- يفحص ضابط الإدخال طلب المستخدم، ويحظر كلمات الإجراء المدمر مثل `delete` قبل
  تشغيل الوكيل أو أدواته.
- يفحص ضابط الإخراج الإجابة النهائية للوكيل، ويحظرها إذا احتوت على كلمة حساسة
  مثل `secret` أو `password`.

عند فشل الفحص، يُفعّل `tripwire`. عندها يطلق المشغّل الاستثناء
`InputGuardrailTripwireTriggered` أو `OutputGuardrailTripwireTriggered`، ويلتقط
البرنامج الاستثناء ويعرض رسالة واضحة. فحص الكلمات هنا مبسط لأغراض التعليم؛ أما
في التطبيقات الحقيقية فيجب تصميم الضوابط لتناسب مخاطر التطبيق وبياناته.

Run it with:

شغّله باستخدام:

```bash
python agent_guardrails.py
```

Try these requests:

جرّب هذه الطلبات:

```text
List the files in this folder: .
Delete all files in this folder.
Reply with the word SECRET.
```

### `hook.py`

This supporting file defines `ConsoleHooks`, which prints agent, model, and tool
lifecycle events in the terminal. It helps learners observe what happens while an
agent is running.

هذا ملف مساعد يعرّف `ConsoleHooks` لطباعة أحداث تشغيل الوكيل والنموذج والأدوات
في الطرفية، مما يساعد المتعلمين على متابعة ما يحدث أثناء عمل الوكيل.
