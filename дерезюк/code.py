import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import re

os.environ["OPENAI_API_KEY"] = "MThjNTMwNjQtOWM0MC00NmEwLWI1NmUtZmM0ODIwMzFhMjMz.11540ee087d2d1bd165bc567e64f5ac9"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"


def check_available_models():
    """Проверяет доступные модели в API Cloud.ru"""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_API_BASE"]
        )
        models = client.models.list()
        print("\nДоступные модели в API Cloud.ru:")
        for model in models.data:
            print(f"- {model.id}")
        return [model.id for model in models.data]
    except Exception as e:
        print(f"Ошибка при получении списка моделей: {e}")
        # Возвращаем список вероятно доступных моделей
        return ["deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "gpt-3.5-turbo", "gpt-4"]


def is_valid_frontend_query(text: str) -> tuple[bool, str]:
    """
    Проверяет, является ли текст осмысленным запросом по фронтенд-разработке.
    Возвращает (is_valid, reason)
    """
    # Проверка на слишком короткий текст
    if len(text.strip()) < 10:
        return False, "Запрос слишком короткий. Пожалуйста, опишите вашу проблему подробнее."
    
    # Проверка на набор случайных символов
    random_pattern = r"^[^a-zA-Zа-яА-Я0-9]{15,}$|([^a-zA-Zа-яА-Я0-9\s]{8,})"
    if re.search(random_pattern, text):
        return False, "Запрос содержит слишком много случайных символов."
    
    # Проверка на повторяющиеся символы или слова
    repeated_chars = re.findall(r"(.)\1{8,}", text)
    if repeated_chars:
        return False, "Обнаружены повторяющиеся последовательности символов."
    
    # Проверка на минимальное количество слов
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{2,}\b', text)
    if len(words) < 3:
        return False, "Недостаточно осмысленных слов для анализа."
    
    # Проверка на соотношение букв и символов
    letters = re.findall(r'[а-яА-Яa-zA-Z]', text)
    if len(letters) / len(text) < 0.4:
        return False, "Текст содержит недостаточно буквенных символов."
    
    return True, "Запрос прошел базовую проверку."


@tool
def react_help(question: str) -> str:
    """
    Предоставляет помощь по React: компоненты, хуки, состояние, производительность.
    Args:
        question: вопрос по React разработке.
    """
    react_knowledge = {
        "компонент": "React компоненты могут быть функциональными или классовыми. Функциональные компоненты с хуками - современный стандарт.",
        "хук": "Основные хуки: useState (состояние), useEffect (побочные эффекты), useContext (контекст), useReducer (сложное состояние).",
        "состояние": "Для управления состоянием используйте useState. Для сложного состояния - useReducer или сторонние решения (Redux, Zustand).",
        "оптимизация": "Для оптимизации используйте: React.memo, useMemo, useCallback, код-сплиттинг с React.lazy.",
        "роутинг": "Популярные решения для роутинга: React Router, Next.js встроенный роутинг.",
        "ошибка": "Для обработки ошибок используйте Error Boundaries в классовых компонентах."
    }
    
    question_lower = question.lower()
    for key in react_knowledge:
        if key in question_lower:
            return react_knowledge[key]
    
    return "Для решения вашей задачи по React рекомендую: 1) Проверить документацию React, 2) Использовать React DevTools для отладки, 3) Рассмотреть использование TypeScript для типизации."


@tool
def vue_help(question: str) -> str:
    """
    Предоставляет помощь по Vue.js: компоненты, композиция, состояние, производительность.
    Args:
        question: вопрос по Vue.js разработке.
    """
    vue_knowledge = {
        "компонент": "Vue компоненты используют Options API или Composition API. Composition API рекомендуется для сложных приложений.",
        "состояние": "Для реактивного состояния используйте ref() для примитивов и reactive() для объектов.",
        "композиция": "Composition API позволяет лучше организовать логику с помощью composable функций.",
        "роутинг": "Vue Router - официальное решение для маршрутизации во Vue приложениях.",
        "оптимизация": "Для оптимизации: v-once, v-memo, lazy loading компонентов, tree shaking."
    }
    
    question_lower = question.lower()
    for key in vue_knowledge:
        if key in question_lower:
            return vue_knowledge[key]
    
    return "Для решения вашей задачи по Vue.js: 1) Изучите Vue DevTools, 2) Используйте Vue 3 с Composition API, 3) Рассмотрите Pinia для управления состоянием."


@tool
def angular_help(question: str) -> str:
    """
    Предоставляет помощь по Angular: компоненты, сервисы, dependency injection, производительность.
    Args:
        question: вопрос по Angular разработке.
    """
    angular_knowledge = {
        "компонент": "Angular компоненты состоят из TypeScript класса, HTML шаблона и CSS стилей. Используют декоратор @Component.",
        "сервис": "Сервисы в Angular - это классы с декоратором @Injectable, используются для разделения бизнес-логики.",
        "dependency injection": "DI в Angular позволяет эффективно управлять зависимостями и тестировать компоненты.",
        "роутинг": "Angular Router предоставляет мощную систему маршрутизации с lazy loading модулей.",
        "оптимизация": "Для оптимизации: OnPush change detection, lazy loading, AOT компиляция, tree shaking."
    }
    
    question_lower = question.lower()
    for key in angular_knowledge:
        if key in question_lower:
            return angular_knowledge[key]
    
    return "Для Angular разработки: 1) Используйте Angular CLI, 2) Внедряйте OnPush стратегию change detection, 3) Используйте RxJS для реактивного программирования."


@tool
def css_help(question: str) -> str:
    """
    Предоставляет помощь по CSS: layout, анимации, responsive design, препроцессоры.
    Args:
        question: вопрос по CSS разработке.
    """
    css_knowledge = {
        "layout": "Современные подходы к верстке: Flexbox для одномерных layouts, Grid для двумерных, CSS Subgrid для сложных сеток.",
        "анимация": "Для анимаций используйте CSS transitions для простых и CSS animations/@keyframes для сложных. Consider motion preferences.",
        "responsive": "Responsive design: mobile-first подход, media queries, container queries, CSS clamp() для fluid typography.",
        "препроцессор": "Популярные препроцессоры: Sass (рекомендуется), Less, Stylus. Используйте переменные, миксины, вложенность.",
        "framework": "Популярные CSS фреймворки: Tailwind CSS (utility-first), Bootstrap, Bulma, Material-UI."
    }
    
    question_lower = question.lower()
    for key in css_knowledge:
        if key in question_lower:
            return css_knowledge[key]
    
    return "Для CSS проблем: 1) Используйте DevTools для инспектирования, 2) Проверьте специфичность селекторов, 3) Рассмотрите CSS-in-JS решения для изоляции стилей."


@tool
def javascript_help(question: str) -> str:
    """
    Предоставляет помощь по JavaScript/TypeScript: синтаксис, асинхронность, типы, современные возможности.
    Args:
        question: вопрос по JavaScript/TypeScript разработке.
    """
    js_knowledge = {
        "асинхронность": "Для работы с асинхронностью: Promises, async/await, рассмотрите RxJS для сложных потоков данных.",
        "typescript": "TypeScript добавляет статическую типизацию. Используйте strict mode, правильные типы, generics для повторно используемого кода.",
        "es6": "Современный JavaScript: стрелочные функции, деструктуризация, шаблонные строки, модули, optional chaining, nullish coalescing.",
        "обработка ошибок": "Используйте try/catch для синхронных ошибок, .catch() для промисов. Реализуйте глобальные обработчики ошибок.",
        "оптимизация": "Оптимизация JS: дебаунсинг, троттлинг, виртуализация списков, Web Workers для тяжелых вычислений."
    }
    
    question_lower = question.lower()
    for key in js_knowledge:
        if key in question_lower:
            return js_knowledge[key]
    
    return "Для JavaScript/TypeScript: 1) Используйте ESLint и Prettier, 2) Пишите тесты (Jest, Vitest), 3) Изучите современные ES6+ возможности."


@tool
def build_tools_help(question: str) -> str:
    """
    Предоставляет помощь по сборщикам: Webpack, Vite, настройка, оптимизация сборки.
    Args:
        question: вопрос по инструментам сборки.
    """
    build_knowledge = {
        "webpack": "Webpack: настройте loaders для разных файлов, plugins для дополнительной функциональности, optimization для продакшн сборки.",
        "vite": "Vite: использует esbuild для dev сервера, Rollup для production. Быстрая сборка благодаря native ES modules.",
        "оптимизация": "Оптимизация сборки: код-сплиттинг, tree shaking, минификация, сжатие, lazy loading, кэширование.",
        "config": "Основные конфигурационные файлы: webpack.config.js, vite.config.js, package.json scripts, .babelrc, tsconfig.json."
    }
    
    question_lower = question.lower()
    for key in build_knowledge:
        if key in question_lower:
            return build_knowledge[key]
    
    return "Для настройки сборки: 1) Начните с готовых шаблонов (Create React App, Vite templates), 2) Используйте анализаторы бандлов, 3) Настройте оптимизацию для production."


@tool
def debugging_help(problem: str) -> str:
    """
    Предоставляет помощь по отладке: инструменты, методологии, распространенные ошибки.
    Args:
        problem: описание проблемы для отладки.
    """
    debugging_approaches = {
        "ошибка": "Методология отладки: 1) Воспроизвести ошибку, 2) Изолировать проблему, 3) Использовать console.log/debugger, 4) Анализировать стек вызовов.",
        "производительность": "Инструменты для профилирования: Chrome DevTools Performance tab, React DevTools Profiler, Lighthouse, WebPageTest.",
        "memory": "Для диагностики утечек памяти: Chrome DevTools Memory tab, отслеживайте нарастание heap size, ищите циклические ссылки.",
        "network": "Проблемы с сетью: используйте Network tab в DevTools, проверяйте CORS, кэширование, размеры файлов."
    }
    
    problem_lower = problem.lower()
    for key in debugging_approaches:
        if key in problem_lower:
            return debugging_approaches[key]
    
    return "Общий подход к отладке: 1) Используйте DevTools браузера, 2) Ведите систематический поиск, 3) Используйте source maps, 4) Пишите тесты для предотвращения регрессий."


@tool
def provide_code_example(technology: str, task: str) -> str:
    """
    Предоставляет примеры кода для различных фронтенд задач.
    Args:
        technology: технология (React, Vue, Angular, JS, TS, CSS)
        task: описание задачи для примера кода.
    """
    examples = {
        "react_component": """
// Функциональный компонент React с TypeScript
interface ButtonProps {
  onClick: () => void;
  children: React.ReactNode;
  disabled?: boolean;
}

const Button: React.FC<ButtonProps> = ({ onClick, children, disabled = false }) => {
  return (
    <button 
      onClick={onClick}
      disabled={disabled}
      className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
    >
      {children}
    </button>
  );
};
""",
        "vue_component": """
<!-- Vue 3 компонент с Composition API -->
<template>
  <button 
    @click="handleClick"
    :disabled="disabled"
    class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
  >
    {{ label }}
  </button>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  label: String,
  disabled: Boolean
});

const emit = defineEmits(['click']);

const handleClick = () => {
  if (!props.disabled) {
    emit('click');
  }
};
</script>
""",
        "css_grid": """
/* CSS Grid layout пример */
.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  padding: 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 1rem;
}

/* Responsive design с media queries */
@media (max-width: 768px) {
  .container {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
}
"""
    }
    
    tech_lower = technology.lower()
    task_lower = task.lower()
    
    if "react" in tech_lower and "компонент" in task_lower:
        return examples["react_component"]
    elif "vue" in tech_lower and "компонент" in task_lower:
        return examples["vue_component"]
    elif "css" in tech_lower and ("grid" in task_lower or "layout" in task_lower):
        return examples["css_grid"]
    
    return "Пример кода будет зависеть от конкретной задачи. Уточните: технологию, задачу и требуемую функциональность."


@tool
def general_knowledge_search(topic: str) -> str:
    """
    Поиск общей информации по различным темам.
    Args:
        topic: тема для поиска информации.
    """
    general_knowledge = {
        "погода": "Я не имею доступа к актуальным данным о погоде. Рекомендую использовать специализированные сервисы.",
        "новости": "Для получения актуальных новостей рекомендую обратиться к новостным порталам или агрегаторам.",
        "кофе": "Кофе - популярный напиток, приготовляемый из обжаренных кофейных зерен. Существует множество способов его приготовления.",
        "программирование": "Программирование - процесс создания компьютерных программ с использованием языков программирования.",
        "искусственный интеллект": "ИИ - область компьютерных наук, занимающаяся созданием машин, способных выполнять задачи, требующие человеческого интеллекта.",
        "спорт": "Спорт - деятельность, направленная на физическое развитие, соревнование и поддержание здоровья.",
        "музыка": "Музыка - вид искусства, использующий звук и тишину, организованные во времени.",
        "литература": "Литература - искусство слова, включающее поэзию, прозу и драматургию."
    }

    return general_knowledge.get(topic.lower(),
                                 "Интересующая вас тема требует более специализированных знаний. Могу помочь с фронтенд-разработкой!")


class FrontendExpert:
    """Эксперт по фронтенд-разработке с автоподбором модели"""
    
    def __init__(self):
        print("\n🔍 Инициализация фронтенд-эксперта...")

        # 1. Найти работающую модель
        working_model = self._find_working_model()
        print(f"✅ Используем модель: {working_model}")

        # 2. Создать модель с найденным именем
        self.model = ChatOpenAI(
            model=working_model,
            temperature=0.3,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"],
            max_retries=2,
            request_timeout=30
        )

        # 3. Определить инструменты
        self.tools = [
            react_help,
            vue_help,
            angular_help,
            css_help,
            javascript_help,
            build_tools_help,
            debugging_help,
            provide_code_example,
            general_knowledge_search
        ]

        self.memory = MemorySaver()

        # 4. Системный промпт
        self.system_prompt = """
Ты — эксперт по фронтенд-разработке, обладающий глубокими знаниями в области современных технологий, библиотек и практик. Твоя основная задача — выступать в роли помощника, наставника и консультанта для фронтенд-разработчика.

Твои основные особенности:
- Имеешь глубокие знания в React, Vue, Angular, JavaScript/TypeScript, CSS и инструментах сборки
- Можешь отвечать на общие вопросы по программированию и технологиям
- Всегда стараешься быть полезным и давать точные ответы

Принципы работы:
1. Будь дружелюбным, терпеливым и отзывчивым
2. Если не знаешь ответа - честно говори об этом
3. Для сложных вопросов разбивай их на логические этапы (chain-of-thought)
4. Предлагай несколько вариантов решений, объясняя плюсы и минусы каждого
5. Используй технику few-shot, предоставляя примеры кода и решений

Структура ответа:
1. Понятный и прямой ответ на вопрос
2. Примеры кода, если они уместны
3. Дополнительные рекомендации и best practices
4. Предложение помощи по другим вопросам

Типичные задачи, которые ты можешь решать:
- Создание и оптимизация React/Vue/Angular компонентов
- Настройка сборщиков, Webpack, Vite
- Работа с API, интеграция данных
- Обработка ошибок, отладка и профилирование
- Responsive design и CSS анимации
"""

        # 5. Создать агента с обработкой ошибок
        try:
            self.agent = create_react_agent(
                model=self.model,
                tools=self.tools,
                checkpointer=self.memory,
                prompt=self.system_prompt
            )
            print("✅ Реактивный агент успешно создан!")
            self.agent_type = "react_agent"
        except Exception as e:
            print(f"⚠️  Не удалось создать реактивного агента: {str(e)[:100]}...")
            print("Использую простую модель без инструментов...")
            self.agent_type = "simple_model"
            print("✅ Простая модель успешно создана!")

    def _find_working_model(self):
        """Автоматический подбор работающей модели"""
        print("🔎 Поиск доступной модели...")

        # Получить список доступных моделей
        available_models = check_available_models()

        if not available_models:
            print("⚠️  Не удалось получить список моделей, использую стандартный набор")
            available_models = ["deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "gpt-3.5-turbo", "gpt-4"]

        # Протестировать каждую модель
        for model_name in available_models:
            try:
                print(f"  Пробую модель: {model_name}")
                test_model = ChatOpenAI(
                    model=model_name,
                    temperature=0.1,
                    openai_api_key=os.environ["OPENAI_API_KEY"],
                    openai_api_base=os.environ["OPENAI_API_BASE"],
                    max_retries=1,
                    request_timeout=10
                )
                # Простой тестовый запрос
                test_response = test_model.invoke("Привет")
                print(f"  ✅ Модель {model_name} работает!")
                return model_name
            except Exception as e:
                print(f"  ❌ Модель {model_name} не работает: {str(e)[:80]}...")
                continue

        # Если ни одна модель не сработала
        print("⚠️  Не найдено работающих моделей, использую deepseek-ai/DeepSeek-R1-Distill-Llama-70B по умолчанию")
        return "deepseek-ai/DeepSeek-R1-Distill-Llama-70B"

    def process_question(self, question: str, thread_id: str = "frontend-session-1") -> str:
        """Обрабатывает вопрос по фронтенд-разработке и возвращает ответ"""
        # Предварительная проверка на валидность
        is_valid, reason = is_valid_frontend_query(question)
        if not is_valid:
            return f"❌ {reason}\n\nПожалуйста, опишите ваш вопрос по фронтенд-разработке более подробно."
        
        try:
            if self.agent_type == "react_agent":
                config = {"configurable": {"thread_id": thread_id}}
                response = self.agent.invoke(
                    {"messages": [{"role": "user", "content": question}]},
                    config=config
                )
                last_message = response["messages"][-1]
                return last_message.content
            else:
                # Для простой модели
                response = self.model.invoke(question)
                return response.content
            
        except Exception as e:
            return f"Произошла ошибка при обработке вопроса: {str(e)}\n\nПопробуйте переформулировать вопрос."


def create_frontend_expert() -> FrontendExpert:
    """Фабрика для создания эксперта по фронтенд-разработке"""
    return FrontendExpert()


def run_frontend_assistant():
    """Запускает сессию помощи по фронтенд-разработке"""
    print("=" * 70)
    print("           ЭКСПЕРТ ПО ФРОНТЕНД-РАЗРАБОТКЕ")
    print("              (с автоподбором модели)")
    print("=" * 70)

    expert = create_frontend_expert()

    print("\n" + "=" * 70)
    print("💻 Ассистент готов к работе!")
    print(f"📊 Тип агента: {expert.agent_type}")
    print("=" * 70)
    print("\nПривет, чем я могу тебе помочь?\n")
    print("Доступные команды:")
    print("  - 'выход', 'exit', 'quit' - завершить работу")
    print("  - Ctrl+C - аварийное завершение")
    print("-" * 70 + "\n")

    while True:
        try:
            user_input = input("💻 Ваш вопрос: ").strip()

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n✅ Удачи в разработке! Возвращайтесь с новыми вопросами!")
                break

            if not user_input:
                continue

            print("\n🔧 Анализирую вопрос...\n")

            response = expert.process_question(user_input)
            print(f"💡 {response}\n")
            print("-" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\n✅ Сессия завершена. Хорошего кодинга!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            print("Попробуйте сформулировать вопрос по-другому.\n")


if __name__ == "__main__":
    run_frontend_assistant()
