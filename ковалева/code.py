import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import re
from typing import Optional

os.environ["OPENAI_API_KEY"] = "MThjNTMwNjQtOWM0MC00NmEwLWI1NmUtZmM0ODIwMzFhMjMz.11540ee087d2d1bd165bc567e64f5ac9"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"


def check_available_models() -> list:
    """Проверяет доступные модели в API Cloud.ru"""
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_API_BASE"]
        )
        models = client.models.list()
        print("\n📋 Доступные модели в API Cloud.ru:")
        for model in models.data:
            print(f"   - {model.id}")
        return [model.id for model in models.data]
    except Exception as e:
        print(f"⚠️  Ошибка при получении списка моделей: {e}")
        return ["deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "gpt-3.5-turbo", "gpt-4"]


def validate_query(text: str) -> tuple[bool, str]:
    """
    Проверяет, является ли текст осмысленным запросом.
    Возвращает (is_valid, reason)
    """
    text = text.strip()
    
    # Проверка на слишком короткий текст
    if len(text) < 5:
        return False, "Запрос слишком короткий. Пожалуйста, опишите подробнее."
    
    # Проверка на набор случайных символов
    if re.search(r"^[^a-zA-Zа-яА-Я0-9]{15,}$", text):
        return False, "Запрос содержит недопустимые символы."
    
    # Проверка на минимальное количество слов
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{2,}\b', text)
    if len(words) < 2:
        return False, "Недостаточно слов для анализа."
    
    # Проверка на соотношение букв и символов
    letters = re.findall(r'[а-яА-Яa-zA-Z]', text)
    if letters and len(letters) / len(text) < 0.3:
        return False, "Текст содержит недостаточно буквенных символов."
    
    return True, "Запрос прошел проверку."


@tool
def react_assistant(query: str) -> str:
    """Помощь по React: компоненты, хуки, состояние, производительность."""
    knowledge_base = {
        "компонент": """React компоненты:
• Функциональные (с хуками) - современный стандарт
• Классовые - для legacy кода
• Компоненты высшего порядка (HOC) для повторного использования логики""",
        
        "хук": """Основные хуки React:
1. useState - управление состоянием
2. useEffect - побочные эффекты
3. useContext - доступ к контексту
4. useReducer - сложное состояние
5. useCallback - мемоизация функций
6. useMemo - мемоизация значений""",
        
        "состояние": """Управление состоянием в React:
• useState - для простого состояния
• useReducer - для сложной логики
• Context API - для глобального состояния
• Redux/Zustand - для больших приложений
• MobX - для реактивного подхода""",
        
        "роутинг": """Роутинг в React:
• React Router - наиболее популярное решение
• Next.js - встроенный роутинг + SSR
• TanStack Router - типобезопасный роутер
• Рекомендация: Next.js для production""",
        
        "оптимизация": """Оптимизация React приложений:
1. React.memo - мемоизация компонентов
2. useMemo/useCallback - мемоизация значений/функций
3. Code splitting - разделение кода
4. Virtualization - для больших списков
5. Lazy loading - отложенная загрузка"""
    }
    
    query_lower = query.lower()
    
    # Проверка ключевых слов
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    # Если нет точного совпадения, ищем по частям
    if any(word in query_lower for word in ["react", "реакт", "ректа"]):
        return """Общие рекомендации по React:
1. Используйте функциональные компоненты с хуками
2. Разделяйте логику на кастомные хуки
3. Используйте TypeScript для типизации
4. Тестируйте с Jest + React Testing Library
5. Оптимизируйте ререндеры через React.memo"""
    
    return "Уточните ваш вопрос по React для более точного ответа."


@tool
def vue_assistant(query: str) -> str:
    """Помощь по Vue.js: композиция, состояние, производительность."""
    knowledge_base = {
        "компонент": """Vue 3 компоненты:
• Options API - традиционный подход
• Composition API - современный стандарт
• Script Setup - синтаксический сахар
• Рекомендация: Composition API для новых проектов""",
        
        "состояние": """Состояние в Vue 3:
• ref() - для примитивных значений
• reactive() - для объектов
• computed() - для вычисляемых свойств
• watch() - для отслеживания изменений
• Pinia - рекомендуемая библиотека состояния""",
        
        "композиция": """Composition API преимущества:
1. Лучшая организация кода
2. Переиспользование логики через composables
3. TypeScript поддержка
4. Дерево зависимостей""",
        
        "роутинг": """Роутинг во Vue:
• Vue Router 4 - официальное решение
• Поддержка nested routes
• Ленивая загрузка компонентов
• Навигационные хуки""",
        
        "оптимизация": """Оптимизация Vue:
• v-once - однократный рендеринг
• v-memo - мемоизация поддеревьев
• KeepAlive - кэширование компонентов
• Асинхронные компоненты"""
    }
    
    query_lower = query.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    if any(word in query_lower for word in ["vue", "вью", "view"]):
        return """Рекомендации по Vue.js:
1. Используйте Vue 3 с Composition API
2. Для состояния - Pinia вместо Vuex
3. Для UI - Vuetify, Element Plus или Quasar
4. Для SSR - Nuxt.js
5. Для статики - VitePress"""
    
    return "Уточните ваш вопрос по Vue.js для более точного ответа."


@tool
def angular_assistant(query: str) -> str:
    """Помощь по Angular: компоненты, сервисы, DI, производительность."""
    knowledge_base = {
        "компонент": """Angular компоненты:
• @Component декоратор
• HTML шаблон + TypeScript класс + CSS
• Lifecycle hooks
• Input/Output свойства
• View encapsulation""",
        
        "сервис": """Сервисы в Angular:
• @Injectable декоратор
• Dependency injection
• Singleton по умолчанию
• Для бизнес-логики и API вызовов
• Предоставляются в модулях или компонентах""",
        
        "dependency injection": """Dependency Injection:
• Иерархическая система инжекторов
• Providers в модулях
• @Injectable() декоратор
• Constructor injection
• Injection tokens""",
        
        "роутинг": """Angular Router:
• Многоуровневая маршрутизация
• Lazy loading модулей
• Route guards
• Resolvers
• ActivatedRoute для доступа к параметрам""",
        
        "оптимизация": """Оптимизация Angular:
• OnPush change detection
• Pure pipes
• trackBy в ngFor
• Lazy loading модулей
• AOT компиляция"""
    }
    
    query_lower = query.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    if any(word in query_lower for word in ["angular", "ангуляр", "анг"]):
        return """Рекомендации по Angular:
1. Используйте последнюю версию Angular
2. RxJS для реактивного программирования
3. NgRx для сложного состояния
4. Angular Material для UI
5. Jest для тестирования"""
    
    return "Уточните ваш вопрос по Angular для более точного ответа."


@tool
def css_assistant(query: str) -> str:
    """Помощь по CSS: layout, анимации, responsive, препроцессоры."""
    knowledge_base = {
        "layout": """Современные подходы к верстке:
1. Flexbox - для одномерных layouts
2. CSS Grid - для двумерных сеток
3. CSS Subgrid - для вложенных сеток
4. Container Queries - для компонентного подхода
5. Aspect-ratio - для соотношения сторон""",
        
        "анимация": """CSS анимации:
• transition - для простых анимаций
• animation + @keyframes - для сложных
• prefers-reduced-motion - для доступности
• will-change - для оптимизации
• Рекомендация: CSS-анимации вместо JS когда возможно""",
        
        "responsive": """Responsive design:
• Mobile-first подход
• Media queries
• Container queries (новинка)
• clamp() для fluid typography
• Viewport units (vw, vh, vmin, vmax)""",
        
        "препроцессор": """CSS препроцессоры:
• Sass/SCSS - наиболее популярный
• Less - более простой синтаксис
• Stylus - гибкий синтаксис
• PostCSS - для трансформаций
• Рекомендация: Sass с модулями""",
        
        "framework": """CSS фреймворки:
• Tailwind CSS - utility-first подход
• Bootstrap - самый популярный
• Bulma - flexbox-based
• Material-UI - material design
• Рекомендация: Tailwind для новых проектов"""
    }
    
    query_lower = query.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    if any(word in query_lower for word in ["css", "стили", "верстка"]):
        return """Общие рекомендации по CSS:
1. Используйте CSS Grid и Flexbox вместо float
2. Применяйте CSS custom properties (переменные)
3. Используйте methodologies (BEM, SMACSS)
4. Оптимизируйте для производительности
5. Тестируйте на различных устройствах"""
    
    return "Уточните ваш вопрос по CSS для более точного ответа."


@tool
def js_ts_assistant(query: str) -> str:
    """Помощь по JavaScript/TypeScript: синтаксис, асинхронность, типы."""
    knowledge_base = {
        "асинхронность": """Асинхронность в JS:
• Callbacks (устаревший подход)
• Promises (современный стандарт)
• async/await (синтаксический сахар)
• RxJS (для сложных потоков)
• Web Workers (для тяжелых вычислений)""",
        
        "typescript": """TypeScript рекомендации:
1. Используйте strict mode
2. Правильные типы для всего
3. Generics для повторно используемого кода
4. Utility types (Partial, Pick, Omit)
5. Декораторы для метапрограммирования""",
        
        "es6": """Современный JavaScript (ES6+):
• Стрелочные функции
• Деструктуризация
• Шаблонные строки
• Модули (import/export)
• Optional chaining (?.)
• Nullish coalescing (??)""",
        
        "обработка ошибок": """Обработка ошибок:
• try/catch для синхронного кода
• .catch() для промисов
• window.onerror для глобальных ошибок
• Error boundaries в React
• Sentry/Bugsnag для мониторинга""",
        
        "оптимизация": """Оптимизация JavaScript:
• Debouncing/throttling событий
• Virtualization длинных списков
• Web Workers
• Code splitting
• Tree shaking"""
    }
    
    query_lower = query.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    if any(word in query_lower for word in ["javascript", "js", "typescript", "ts"]):
        return """Рекомендации по JS/TS:
1. Используйте ESLint + Prettier
2. Пишите тесты (Jest, Vitest)
3. Используйте современный синтаксис
4. Документируйте код с JSDoc
5. Используйте TypeScript для больших проектов"""
    
    return "Уточните ваш вопрос по JavaScript/TypeScript для более точного ответа."


@tool
def build_tools_assistant(query: str) -> str:
    """Помощь по инструментам сборки: Webpack, Vite, настройка."""
    knowledge_base = {
        "webpack": """Webpack конфигурация:
• Entry/Output точки
• Loaders для разных типов файлов
• Plugins для дополнительной функциональности
• Optimization для production
• Dev server для разработки""",
        
        "vite": """Vite преимущества:
• Мгновенный запуск dev сервера
• Нативная поддержка ES modules
• Hot module replacement
• Оптимизированная production сборка
• Плагинная система""",
        
        "оптимизация": """Оптимизация сборки:
1. Code splitting
2. Tree shaking
3. Минификация
4. Сжатие (gzip, brotli)
5. Кэширование (content hashing)
6. Ленивая загрузка""",
        
        "config": """Конфигурационные файлы:
• webpack.config.js / vite.config.js
• package.json scripts
• .babelrc / babel.config.js
• tsconfig.json
• .eslintrc.js / .prettierrc"""
    }
    
    query_lower = query.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in query_lower:
            return answer
    
    if any(word in query_lower for word in ["webpack", "vite", "сборка", "build"]):
        return """Рекомендации по инструментам сборки:
1. Используйте Vite для новых проектов
2. Настраивайте code splitting
3. Используйте анализаторы бандлов
4. Оптимизируйте для production
5. Настройте кэширование"""
    
    return "Уточните ваш вопрос по инструментам сборки для более точного ответа."


@tool
def debugging_assistant(problem: str) -> str:
    """Помощь по отладке: инструменты, методологии, ошибки."""
    knowledge_base = {
        "ошибка": """Методология отладки:
1. Воспроизвести ошибку
2. Изолировать проблему
3. Использовать console.log / debugger
4. Анализировать стек вызовов
5. Проверить логи""",
        
        "производительность": """Профилирование производительности:
• Chrome DevTools Performance tab
• React DevTools Profiler
• Vue DevTools Performance
• Lighthouse audits
• WebPageTest""",
        
        "memory": """Диагностика утечек памяти:
1. Chrome DevTools Memory tab
2. Heap snapshots сравнение
3. Timeline allocation instrumentation
4. Проверка циклических ссылок
5. Мониторинг heap size""",
        
        "network": """Проблемы с сетью:
• DevTools Network tab
• Проверка CORS политик
• Кэширование ресурсов
• Оптимизация размеров файлов
• HTTP/2 или HTTP/3"""
    }
    
    problem_lower = problem.lower()
    
    for keyword, answer in knowledge_base.items():
        if keyword in problem_lower:
            return answer
    
    return """Общий подход к отладке:
1. Используйте DevTools браузера
2. Систематически сужайте круг поиска
3. Используйте source maps для минифицированного кода
4. Пишите тесты для предотвращения регрессий
5. Используйте мониторинг ошибок (Sentry)"""


@tool
def code_examples_assistant(technology: str, task: str) -> str:
    """Предоставляет примеры кода для фронтенд задач."""
    examples = {
        "react_component": """// React компонент с TypeScript и хуками
import React, { useState, useEffect } from 'react';

interface UserProfileProps {
  userId: number;
  onUpdate?: (data: UserData) => void;
}

const UserProfile: React.FC<UserProfileProps> = ({ userId, onUpdate }) => {
  const [user, setUser] = useState<UserData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId);
  }, [userId]);

  const fetchUser = async (id: number) => {
    try {
      const response = await fetch(`/api/users/${id}`);
      const data = await response.json();
      setUser(data);
      onUpdate?.(data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!user) return <div>User not found</div>;

  return (
    <div className="user-profile">
      <h2>{user.name}</h2>
      <p>Email: {user.email}</p>
      <p>Role: {user.role}</p>
    </div>
  );
};

export default UserProfile;""",
        
        "vue_component": """<!-- Vue 3 компонент с Composition API и TypeScript -->
<template>
  <div class="user-profile">
    <div v-if="loading" class="loading">Loading...</div>
    <div v-else-if="user" class="content">
      <h2>{{ user.name }}</h2>
      <p>Email: {{ user.email }}</p>
      <p>Role: {{ user.role }}</p>
      <button @click="handleEdit" class="edit-btn">Edit</button>
    </div>
    <div v-else class="not-found">User not found</div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';

interface UserData {
  id: number;
  name: string;
  email: string;
  role: string;
}

interface Props {
  userId: number;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  update: [data: UserData];
}>();

const user = ref<UserData | null>(null);
const loading = ref(true);

const fetchUser = async (id: number) => {
  try {
    const response = await fetch(`/api/users/${id}`);
    user.value = await response.json();
    emit('update', user.value);
  } catch (error) {
    console.error('Failed to fetch user:', error);
    user.value = null;
  } finally {
    loading.value = false;
  }
};

const handleEdit = () => {
  // Логика редактирования
};

onMounted(() => {
  fetchUser(props.userId);
});

watch(() => props.userId, (newId) => {
  fetchUser(newId);
});
</script>

<style scoped>
.user-profile {
  padding: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}
.loading {
  color: #666;
}
.edit-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
</style>""",
        
        "css_modern": """/* Современный CSS с переменными и Grid */
:root {
  --primary-color: #4361ee;
  --secondary-color: #3a0ca3;
  --text-color: #333;
  --bg-color: #f8f9fa;
  --border-radius: 8px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  --transition: all 0.3s ease;
}

.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: var(--transition);
  display: flex;
  flex-direction: column;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
}

.card-header {
  padding: 20px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: white;
}

.card-body {
  padding: 20px;
  flex-grow: 1;
}

.card-footer {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: var(--transition);
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  background: var(--secondary-color);
}

/* Темная тема */
@media (prefers-color-scheme: dark) {
  :root {
    --text-color: #f8f9fa;
    --bg-color: #212529;
  }
  
  .card {
    background: #2d3436;
    color: var(--text-color);
  }
}

/* Адаптивность */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
    gap: 16px;
    padding: 16px;
  }
  
  .card-header,
  .card-body,
  .card-footer {
    padding: 16px;
  }
}"""
    }
    
    tech_lower = technology.lower()
    task_lower = task.lower()
    
    if "react" in tech_lower and "компонент" in task_lower:
        return examples["react_component"]
    elif "vue" in tech_lower and "компонент" in task_lower:
        return examples["vue_component"]
    elif "css" in tech_lower or "стили" in tech_lower:
        return examples["css_modern"]
    
    return """Примеры кода доступны для:
1. React компонентов
2. Vue компонентов
3. Современного CSS

Уточните технологию и задачу для получения конкретного примера."""


@tool
def general_info_assistant(topic: str) -> str:
    """Поиск общей информации по различным темам."""
    knowledge = {
        "погода": "Я не имею доступа к текущим погодным данным. Для актуальной информации используйте специализированные сервисы погоды.",
        "новости": "Для получения актуальных новостей рекомендую обратиться к проверенным новостным порталам или агрегаторам.",
        "программирование": "Программирование — это процесс создания компьютерных программ с использованием языков программирования. Включает проектирование, написание, тестирование и поддержку кода.",
        "искусственный интеллект": "ИИ — область компьютерных наук, занимающаяся созданием систем, способных выполнять задачи, требующие человеческого интеллекта. Включает машинное обучение, нейронные сети и обработку естественного языка.",
        "веб разработка": "Веб-разработка включает фронтенд (клиентская часть), бэкенд (серверная часть) и DevOps. Современный стек: React/Vue/Angular, Node.js/Python, Docker, Kubernetes.",
        "обучение": "Для обучения программированию рекомендую: 1) Практические курсы, 2) Официальную документацию, 3) Open source проекты, 4) Сообщество разработчиков."
    }
    
    return knowledge.get(topic.lower(), 
        "Я специализируюсь на фронтенд-разработке. Могу помочь с React, Vue, Angular, JavaScript/TypeScript, CSS и инструментами сборки.")


class FrontendDevelopmentAssistant:
    """Ассистент по фронтенд-разработке с автоподбором модели"""
    
    def __init__(self):
        print("\n" + "=" * 60)
        print("🔧 ИНИЦИАЛИЗАЦИЯ АССИСТЕНТА ПО ФРОНТЕНД-РАЗРАБОТКЕ")
        print("=" * 60)
        
        # 1. Поиск работающей модели
        self._detect_available_models()
        working_model = self._find_working_model()
        print(f"\n✅ Выбрана модель: {working_model}")
        
        # 2. Инициализация модели
        self.model = ChatOpenAI(
            model=working_model,
            temperature=0.3,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"],
            max_retries=3,
            request_timeout=45,
            max_tokens=2000
        )
        
        # 3. Определение инструментов
        self.tools = [
            react_assistant,
            vue_assistant,
            angular_assistant,
            css_assistant,
            js_ts_assistant,
            build_tools_assistant,
            debugging_assistant,
            code_examples_assistant,
            general_info_assistant
        ]
        
        # 4. Система памяти
        self.memory = MemorySaver()
        
        # 5. Системный промпт
        self.system_prompt = self._create_system_prompt()
        
        # 6. Создание агента
        self.agent_type = self._create_agent()
        
        print("\n" + "=" * 60)
        print("🎯 АССИСТЕНТ УСПЕШНО ИНИЦИАЛИЗИРОВАН")
        print("=" * 60)
    
    def _detect_available_models(self):
        """Обнаружение доступных моделей"""
        print("\n🔍 Проверка доступных моделей...")
        self.available_models = check_available_models()
    
    def _find_working_model(self) -> str:
        """Автоматический подбор работающей модели"""
        print("\n⚙️  Тестирование моделей...")
        
        priority_models = [
            "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            "gpt-4",
            "gpt-3.5-turbo"
        ]
        
        # Проверяем приоритетные модели
        for model_name in priority_models:
            if model_name in (m.lower() for m in self.available_models):
                try:
                    print(f"  • Пробуем: {model_name}")
                    test_model = ChatOpenAI(
                        model=model_name,
                        temperature=0.1,
                        openai_api_key=os.environ["OPENAI_API_KEY"],
                        openai_api_base=os.environ["OPENAI_API_BASE"],
                        max_retries=1,
                        request_timeout=15
                    )
                    test_response = test_model.invoke("Тестовое сообщение")
                    if test_response and test_response.content:
                        print(f"  ✓ Модель {model_name} работает")
                        return model_name
                except Exception as e:
                    print(f"  ✗ Модель {model_name} недоступна: {str(e)[:60]}...")
        
        # Если ни одна из приоритетных не сработала, пробуем другие
        for model_name in self.available_models:
            if model_name not in priority_models:
                try:
                    print(f"  • Пробуем альтернативу: {model_name}")
                    test_model = ChatOpenAI(
                        model=model_name,
                        temperature=0.1,
                        openai_api_key=os.environ["OPENAI_API_KEY"],
                        openai_api_base=os.environ["OPENAI_API_BASE"],
                        max_retries=1,
                        request_timeout=15
                    )
                    test_response = test_model.invoke("Тестовое сообщение")
                    if test_response and test_response.content:
                        print(f"  ✓ Модель {model_name} работает")
                        return model_name
                except:
                    continue
        
        print("⚠️  Не удалось найти работающую модель, использую fallback")
        return "gpt-3.5-turbo"
    
    def _create_system_prompt(self) -> str:
        """Создание системного промпта"""
        return """# Роль: Эксперт по фронтенд-разработке

## Основная специализация
Ты — опытный фронтенд-разработчик с глубокими знаниями в:
• React (хуки, компоненты, состояние, оптимизация)
• Vue.js (Composition API, Vue 3, Pinia)
• Angular (компоненты, сервисы, RxJS, DI)
• JavaScript/TypeScript (ES6+, асинхронность, типы)
• CSS (Flexbox, Grid, анимации, responsive design)
• Инструменты сборки (Webpack, Vite, оптимизация)
• Отладка и производительность

## Принципы работы
1. Будь точным и конкретным в ответах
2. Приводи примеры кода когда это уместно
3. Объясняй сложные концепции простыми словами
4. Предлагай несколько решений с плюсами/минусами
5. Рекомендуй лучшие практики и современные подходы
6. Оставайся в рамках фронтенд-разработки

## Формат ответов
1. **Краткий ответ** на вопрос
2. **Подробное объяснение** при необходимости
3. **Пример кода** если требуется
4. **Дополнительные рекомендации**
5. **Ссылки на документацию** (если известны)

## Доступные инструменты
У тебя есть доступ к специализированным инструментам для помощи по:
- React, Vue, Angular
- CSS и верстке
- JavaScript/TypeScript
- Инструментам сборки
- Отладке и оптимизации
- Готовым примерам кода
- Общей информации

## Важно
• Если не знаешь ответа — честно скажи об этом
• Для сложных вопросов используй chain-of-thought
• Следи за актуальностью информации
• Будь полезным и профессиональным"""
    
    def _create_agent(self) -> str:
        """Создание агента с обработкой ошибок"""
        try:
            print("\n🤖 Создание интеллектуального агента...")
            self.agent = create_react_agent(
                model=self.model,
                tools=self.tools,
                checkpointer=self.memory,
                prompt=self.system_prompt
            )
            print("✅ Интеллектуальный агент создан успешно")
            return "intelligent_agent"
        except Exception as e:
            print(f"⚠️  Не удалось создать интеллектуального агента: {str(e)[:80]}...")
            print("🔄 Использую базовую языковую модель...")
            return "basic_model"
    
    def process_query(self, user_query: str, session_id: str = "frontend-dev-1") -> str:
        """Обработка пользовательского запроса"""
        # Валидация запроса
        is_valid, reason = validate_query(user_query)
        if not is_valid:
            return f"❌ {reason}\n\nПожалуйста, задайте более конкретный вопрос."
        
        try:
            if self.agent_type == "intelligent_agent":
                config = {"configurable": {"thread_id": session_id}}
                response = self.agent.invoke(
                    {"messages": [{"role": "user", "content": user_query}]},
                    config=config
                )
                last_message = response["messages"][-1]
                return last_message.content
            else:
                # Базовая модель
                response = self.model.invoke(user_query)
                return response.content if response else "Не удалось получить ответ"
                
        except Exception as e:
            error_msg = str(e)
            if "timeout" in error_msg.lower():
                return "⏱️  Превышено время ожидания ответа. Попробуйте более простой запрос."
            elif "rate limit" in error_msg.lower():
                return "🚫 Превышен лимит запросов. Попробуйте позже."
            else:
                return f"⚠️  Произошла ошибка: {error_msg[:100]}...\n\nПопробуйте переформулировать вопрос."


def initialize_assistant() -> FrontendDevelopmentAssistant:
    """Инициализация ассистента по фронтенд-разработке"""
    return FrontendDevelopmentAssistant()


def start_interactive_session():
    """Запуск интерактивной сессии помощи по фронтенд-разработке"""
    print("\n" + "=" * 70)
    print("🚀 ЗАПУСК АССИСТЕНТА ПО ФРОНТЕНД-РАЗРАБОТКЕ")
    print("=" * 70)
    
    assistant = initialize_assistant()
    
    print("\n📋 ИНФОРМАЦИЯ О СИСТЕМЕ:")
    print(f"   • Тип агента: {assistant.agent_type}")
    print(f"   • Доступно инструментов: {len(assistant.tools)}")
    print(f"   • Модель: {assistant.model.model_name}")
    print("=" * 70)
    
    print("\n👋 Привет! Я твой помощник по фронтенд-разработке.")
    print("\nЯ могу помочь с:")
    print("  • React, Vue, Angular разработкой")
    print("  • JavaScript/TypeScript вопросами")
    print("  • CSS, версткой и анимациями")
    print("  • Настройкой сборки (Webpack, Vite)")
    print("  • Отладкой и оптимизацией")
    print("  • Примеры кода и лучшие практики")
    
    print("\n📝 КОМАНДЫ:")
    print("  • 'выход', 'exit', 'quit' — завершить работу")
    print("  • 'помощь', 'help' — показать это сообщение")
    print("  • Ctrl+C — экстренное завершение")
    print("-" * 70)
    
    session_counter = 1
    
    while True:
        try:
            print(f"\n💭 Вопрос #{session_counter}")
            user_input = input("🎯 Ваш запрос: ").strip()
            
            if not user_input:
                continue
                
            # Проверка команд
            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n" + "=" * 70)
                print("👋 Спасибо за использование! Удачи в разработке!")
                print("=" * 70)
                break
                
            if user_input.lower() in ['помощь', 'help', '?']:
                print("\n📋 Доступные категории вопросов:")
                print("  1. React (компоненты, хуки, состояние)")
                print("  2. Vue.js (Composition API, Vue 3)")
                print("  3. Angular (компоненты, сервисы, RxJS)")
                print("  4. CSS (Grid, Flexbox, анимации)")
                print("  5. JavaScript/TypeScript (ES6+, типы)")
                print("  6. Инструменты сборки (Webpack, Vite)")
                print("  7. Отладка и оптимизация")
                print("  8. Примеры кода")
                continue
            
            print("\n🔍 Анализирую запрос...")
            
            response = assistant.process_query(user_input)
            
            print("\n" + "=" * 70)
            print("💡 ОТВЕТ:")
            print("=" * 70)
            print(f"\n{response}")
            print("\n" + "-" * 70)
            
            session_counter += 1
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Сессия прервана пользователем.")
            print("👋 До новых встреч!")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {str(e)}")
            print("Попробуйте перезапустить ассистента.")


# Дополнительные утилиты
def quick_help():
    """Быстрая справка по использованию"""
    print("\n⚡ БЫСТРАЯ СПРАВКА:")
    print("Примеры вопросов:")
    print("1. 'Как создать React компонент с TypeScript?'")
    print("2. 'Оптимизация производительности Vue приложения'")
    print("3. 'Лучшие практики CSS Grid'")
    print("4. 'Настройка Webpack для production'")
    print("5. 'Отладка утечек памяти в JavaScript'")


if __name__ == "__main__":
    try:
        start_interactive_session()
    except Exception as e:
        print(f"\n🔥 Критическая ошибка при запуске: {e}")
        print("Проверьте:")
        print("1. Интернет соединение")
        print("2. API ключ и базовый URL")
        print("3. Доступность API Cloud.ru")
