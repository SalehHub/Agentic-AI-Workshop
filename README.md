# Designing and Building AI Agents | تصميم وبناء وكلاء الذكاء الاصطناعي

## Introduction | مقدمة

This workshop introduces agent design step by step using Python and the OpenAI
Agents SDK. The first example creates a simple agent with one tool and no memory.
The next example adds a persistent session so the agent can remember previous
conversations. A third example adds tools for reading and renaming files.
A fourth example shows how to select a model and configure its behavior.
A fifth example introduces input and output guardrails.
A sixth example enhances the file reader to support different text encodings,
regular PDFs, and scanned PDFs using OCR.
A seventh example creates two agents: a file assistant and a specialist that
summarizes text files.
The eighth and final example adds a desktop chat interface, file and folder
attachments, and multiple saved conversations.

تقدم هذه الورشة تصميم وكلاء الذكاء الاصطناعي خطوة بخطوة باستخدام بايثون وOpenAI Agents
SDK. ينشئ المثال الأول وكيلاً بسيطاً بأداة واحدة ومن دون ذاكرة، ثم يضيف المثال
التالي جلسة دائمة تمكّن الوكيل من تذكّر المحادثات السابقة. ويضيف مثال ثالث
أدوات لقراءة الملفات وإعادة تسميتها.
ويوضح مثال رابع كيفية اختيار النموذج وضبط سلوكه.
ويقدم مثال خامس ضوابط الإدخال والإخراج.
ويطوّر مثال سادس أداة قراءة الملفات لدعم ترميزات نصية مختلفة وملفات PDF العادية
والممسوحة ضوئياً باستخدام OCR.
وينشئ مثال سابع وكيلين: مساعداً للملفات ووكيلاً متخصصاً في تلخيص الملفات النصية.
ويضيف المثال الثامن والأخير واجهة محادثة مكتبية، وإرفاق الملفات والمجلدات، وحفظ
عدة محادثات مستقلة.

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

The requirements file installs the OpenAI Agents SDK and the Python packages
needed to detect text encodings, read PDFs, run OCR, and display the GUI.

يثبّت ملف المتطلبات OpenAI Agents SDK وحزم بايثون اللازمة لاكتشاف ترميز النصوص
وقراءة ملفات PDF وتشغيل OCR وعرض الواجهة الرسومية.

#### Install the OCR engine | تثبيت محرك OCR

Example Six needs Tesseract installed on the computer to read scanned PDFs.
Install both English and Arabic language data, then verify that the `tesseract`
command works.

يحتاج المثال السادس إلى تثبيت Tesseract على الجهاز لقراءة ملفات PDF الممسوحة
ضوئياً. ثبّت بيانات اللغتين الإنجليزية والعربية، ثم تحقق من عمل أمر `tesseract`.

On macOS with [Homebrew](https://brew.sh/):

على macOS باستخدام [Homebrew](https://brew.sh/):

```bash
brew install tesseract tesseract-lang
```

On Windows, use the Windows installer linked from the
[Tesseract documentation](https://tesseract-ocr.github.io/tessdoc/), select the
Arabic language during installation, and allow the installer to add Tesseract to
`PATH`.

على ويندوز، استخدم برنامج تثبيت ويندوز المشار إليه في
[توثيق Tesseract](https://tesseract-ocr.github.io/tessdoc/)، واختر اللغة العربية
أثناء التثبيت، واسمح لبرنامج التثبيت بإضافة Tesseract إلى `PATH`.

Verify the installation:

تحقق من التثبيت:

```bash
tesseract --list-langs
```

The result should include `eng` and `ara`.

يجب أن تتضمن النتيجة `eng` و`ara`.

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
Starting with example two, every later example keeps the persistent session. The
available tools change between learning stages, while each later example adds one
focused concept without changing the general instructions.

تستخدم جميع أمثلة الوكيل الاسم العام `File Assistant` والتعليمات العامة نفسها.
ابتداءً من المثال الثاني، تحتفظ جميع الأمثلة اللاحقة بالجلسة الدائمة. وتتغير
الأدوات المتاحة بين المراحل التعليمية، بينما يضيف كل مثال لاحق مفهوماً محدداً
من دون تغيير التعليمات العامة.

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

### `agent_rename.py`

This example keeps `list_folder` and adds two tools: `read_file` reads a UTF-8
text file, while `rename_file` changes a file's name. The agent can read text
files and rename them based on their contents.

يحتفظ هذا المثال بأداة `list_folder` ويضيف أداتين: تقرأ `read_file` ملفاً نصياً
بترميز UTF-8، بينما تغيّر `rename_file` اسم الملف. يستطيع الوكيل قراءة الملفات
النصية وإعادة تسميتها بناءً على محتواها.

Run it with:

شغّله باستخدام:

```bash
python agent_rename.py
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

### `agent_pdf.py`

Example Six keeps the folder-listing, file-reading, and file-renaming tools. It
enhances `read_file` so it can detect common text encodings and read both regular
and scanned PDF files. Scanned pages use Arabic and English OCR. When a PDF has a
damaged text layer, the tool compares it with the OCR result and returns the more
readable version. Long results are shortened to protect the model's context
window.

يحتفظ المثال السادس بأدوات عرض المجلد وقراءة الملفات وإعادة تسميتها. ويطوّر
`read_file` لتكتشف ترميزات النصوص الشائعة وتقرأ ملفات PDF العادية والممسوحة
ضوئياً. تستخدم الصفحات الممسوحة OCR باللغتين العربية والإنجليزية. وإذا احتوى
ملف PDF على طبقة نص تالفة، تقارن الأداة النص بنتيجة OCR وتعيد النسخة الأكثر
وضوحاً. وتُختصر النتائج الطويلة لحماية نافذة سياق النموذج.

Run it with:

شغّله باستخدام:

```bash
python agent_pdf.py
```

Use this example—not `agent.py`—when you want to read or rename PDF files.

استخدم هذا المثال، وليس `agent.py`، عندما تريد قراءة ملفات PDF أو إعادة تسميتها.

### `agent_multiple.py`

Example Seven introduces a second agent named `File Summarizer`. The main `File
Assistant` keeps the previous tools and adds `write_file`, which creates a new
UTF-8 text file without overwriting an existing file. After reading a text file,
the main agent calls the second agent through the `summarize_file` tool and can
save the resulting summary with `write_file`. The summarizer has one focused job:
produce a clear and accurate summary without inventing information. The main
agent remains responsible for the final response. This demonstrates the
agents-as-tools orchestration pattern described in the
[OpenAI Agents SDK documentation](https://developers.openai.com/api/docs/guides/agents/orchestration).

يقدم المثال السابع وكيلاً ثانياً اسمه `File Summarizer`. يحتفظ `File Assistant`
الرئيسي بالأدوات السابقة ويضيف `write_file`، التي تنشئ ملفاً نصياً جديداً بترميز
UTF-8 من دون استبدال ملف موجود. وبعد قراءة الملف النصي، يستدعي الوكيل الثاني من
خلال أداة `summarize_file`، ثم يمكنه حفظ الملخص باستخدام `write_file`. للوكيل
المتخصص مهمة واحدة محددة: إنشاء ملخص واضح ودقيق من دون اختراع معلومات. ويبقى
الوكيل الرئيسي مسؤولاً عن الإجابة النهائية. يوضح هذا المثال نمط استخدام الوكلاء
كأدوات الموضح في
[توثيق OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/orchestration).

Run it with:

شغّله باستخدام:

```bash
python agent_multiple.py
```

Try this request:

جرّب هذا الطلب:

```text
Read and summarize /path/to/file.txt, then save the summary as /path/to/summary.txt
```

### `agent_gui.py`

Example Eight is the final example. It gives the complete text-file assistant a
desktop chat interface built with PySide6. The user can attach one or more file
paths or a folder path, then ask the agent to list, read, rename, write, or
summarize files. Attaching an item shares its local path with the agent; the
agent uses its tools when it needs to inspect that path.

Each new conversation receives a unique chat ID. The chat list, IDs, and message
history are stored in `gui_history.db`. Closing and reopening the application
restores the previous conversations, and switching chats gives the agent the
memory belonging only to the selected chat ID. IDs are used internally and are
not displayed in the interface.

المثال الثامن هو المثال الأخير. يمنح مساعد الملفات النصية الكامل واجهة محادثة
مكتبية مبنية باستخدام PySide6. يمكن للمستخدم إرفاق مسار ملف واحد أو عدة ملفات
أو مسار مجلد، ثم طلب عرض الملفات أو قراءتها أو إعادة تسميتها أو كتابتها أو
تلخيصها. يشارك الإرفاق المسار المحلي مع الوكيل، ويستخدم الوكيل أدواته عند حاجته
إلى فحص ذلك المسار.

تحصل كل محادثة جديدة على معرّف محادثة فريد. تُحفظ قائمة المحادثات ومعرّفاتها
وسجل الرسائل في `gui_history.db`. عند إغلاق التطبيق وفتحه من جديد، تظهر
المحادثات السابقة، ولكل محادثة ذاكرة مستقلة مرتبطة بمعرّفها فقط. تُستخدم
المعرّفات داخلياً ولا تظهر في الواجهة.

Run it with:

شغّله باستخدام:

```bash
python agent_gui.py
```

Use **Attach** to select files, folders, or both in the same picker. The selected
paths appear at the end of the message, where you can edit them before pressing
**Send** or `Ctrl+Enter`. Use **New Chat** to start an independent saved
conversation. Right-click a chat and choose **Delete Chat** to permanently
remove that conversation and its saved messages after confirming the warning.

استخدم **Attach** لاختيار ملفات أو مجلدات أو كليهما من النافذة نفسها. تظهر
المسارات المحددة في نهاية الرسالة، ويمكنك تعديلها قبل الضغط على **Send** أو
استخدام `Ctrl+Enter`. اضغط **New Chat** لبدء محادثة مستقلة ومحفوظة.
انقر بزر الفأرة الأيمن على محادثة واختر **Delete Chat** لحذفها نهائياً مع
رسائلها المحفوظة بعد تأكيد رسالة التحذير.

### `hook.py`

This supporting file defines `ConsoleHooks`, which prints agent, model, and tool
lifecycle events in the terminal. It helps learners observe what happens while an
agent is running.

هذا ملف مساعد يعرّف `ConsoleHooks` لطباعة أحداث تشغيل الوكيل والنموذج والأدوات
في الطرفية، مما يساعد المتعلمين على متابعة ما يحدث أثناء عمل الوكيل.
