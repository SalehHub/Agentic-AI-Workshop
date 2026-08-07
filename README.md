# Designing and Building AI Agents | تصميم وبناء وكلاء الذكاء الاصطناعي

## Introduction | مقدمة

This workshop introduces agent design step by step using Python and the OpenAI
Agents SDK. The first example creates a simple agent with one tool and no memory.
The next example adds a persistent session so the agent can remember previous
conversations.

تقدم هذه الورشة تصميم الوكلاء الذكيين خطوة بخطوة باستخدام بايثون وOpenAI Agents
SDK. ينشئ المثال الأول وكيلاً بسيطاً بأداة واحدة ومن دون ذاكرة، ثم يضيف المثال
التالي جلسة دائمة تمكّن الوكيل من تذكّر المحادثات السابقة.

## Setup | الإعداد

Before running the examples, make a copy of `.env.example` and name the copy
`.env`:

قبل تشغيل الأمثلة، أنشئ نسخة من ملف `.env.example` وغيّر اسم النسخة إلى `.env`:

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

## Python files | ملفات بايثون

### `agent.py`

The first agent-design example. It creates a document assistant with one tool,
`list_folder`, which lists the contents of a folder. Each request is independent,
so this agent does not remember earlier conversations.

هذا هو المثال الأول لتصميم الوكيل. ينشئ مساعداً للملفات يمتلك أداة واحدة اسمها
`list_folder` لعرض محتويات المجلد. كل طلب مستقل، لذلك لا يتذكر هذا الوكيل
المحادثات السابقة.

Run it with:

شغّله باستخدام:

```bash
python3 agent.py
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
python3 agent_session.py
```

### `hook.py`

This supporting file defines `ConsoleHooks`, which prints agent, model, and tool
lifecycle events in the terminal. It helps learners observe what happens while an
agent is running.

هذا ملف مساعد يعرّف `ConsoleHooks` لطباعة أحداث تشغيل الوكيل والنموذج والأدوات
في الطرفية، مما يساعد المتعلمين على متابعة ما يحدث أثناء عمل الوكيل.
