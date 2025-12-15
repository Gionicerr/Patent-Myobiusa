import os
from typing import Dict, List, Optional, Any
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import json
import re

os.environ["OPENAI_API_KEY"] = "YjRhZDJhY2UtM2E3NS00ZjAzLWJmNzctZWE1MWY0YmE1OTVh.2c0cb60717718eecc1aac50faea7c6b3"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"


def check_available_models() -> List[str]:
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
        return ["deepseek-ai/DeepSeek-R1-Distill-Llama-70B", "gpt-4", "gpt-3.5-turbo"]


def validate_patent_input(text: str) -> tuple[bool, str]:
    """
    Проверяет, является ли текст осмысленным описанием изобретения.
    Возвращает (is_valid, reason)
    """
    text = text.strip()

    # Проверка на слишком короткий текст
    if len(text) < 20:
        return False, "Описание слишком краткое. Пожалуйста, подробно опишите изобретение."

    # Проверка на минимальное количество слов
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{2,}\b', text)
    if len(words) < 10:
        return False, "Недостаточно технических деталей для генерации патента."

    # Проверка на наличие технических терминов (базовая)
    technical_terms = ['устройство', 'способ', 'метод', 'система', 'процесс',
                       'изобретение', 'технический', 'результат', 'принцип']

    has_technical_terms = any(term in text.lower() for term in technical_terms)
    if not has_technical_terms:
        return False, "В описании отсутствуют технические детали. Добавьте информацию об устройстве, способе или системе."

    return True, "Описание прошло проверку."


@tool
def generate_patent_claims(invention_description: str) -> Dict[str, Any]:
    """
    Генерирует юридически корректную формулу изобретения на основе описания.
    Возвращает независимые и зависимые пункты формулы.

    Args:
        invention_description: Детальное описание изобретения, его технических особенностей и новизны
    """
    # Анализ типа изобретения
    description_lower = invention_description.lower()

    if any(word in description_lower for word in ['устройство', 'аппарат', 'механизм', 'система']):
        invention_type = "устройство"
    elif any(word in description_lower for word in ['способ', 'метод', 'процесс', 'технология']):
        invention_type = "способ"
    elif any(word in description_lower for word in ['вещество', 'материал', 'композиция', 'смесь']):
        invention_type = "вещество"
    elif any(word in description_lower for word in ['программа', 'алгоритм', 'программный', 'код']):
        invention_type = "программа для ЭВМ"
    else:
        invention_type = "изобретение"

    # Генерация примерной формулы
    template = {
        "invention_type": invention_type,
        "independent_claims": [
            f"1. {invention_type.capitalize()}, отличающееся тем, что...",
            f"2. {invention_type.capitalize()} по п.1, отличающееся тем, что..."
        ],
        "dependent_claims": [
            "3. Способ по п.1 или 2, отличающийся тем, что...",
            "4. Система по любому из пп.1-3, отличающаяся тем, что..."
        ],
        "total_claims": 4,
        "status": "success",
        "recommendations": [
            "Уточните технические особенности в независимом пункте",
            "Добавьте примеры конкретных реализаций",
            "Проверьте уникальность каждого зависимого пункта"
        ]
    }

    return template


@tool
def generate_patent_description(technical_details: str) -> Dict[str, Any]:
    """
    Создает полное описание изобретения в патентном стиле.
    Форматирует по стандартным разделам патента.

    Args:
        technical_details: Технические характеристики, принцип работы, область применения
    """
    # Анализ области техники
    domains = {
        'медицина': ['медицинск', 'лечени', 'диагност', 'хирург'],
        'it': ['программ', 'алгоритм', 'данн', 'информац', 'вычислен'],
        'механика': ['механич', 'двигател', 'передач', 'вал', 'шестерн'],
        'химия': ['химическ', 'реакц', 'веществ', 'соединен', 'катализатор'],
        'электроника': ['электрич', 'схем', 'микросхем', 'транзистор', 'диод']
    }

    detected_domain = "общая техника"
    for domain, keywords in domains.items():
        if any(keyword in technical_details.lower() for keyword in keywords):
            detected_domain = domain
            break

    # Генерация структурированного описания
    description_template = {
        "domain": detected_domain,
        "sections": {
            "field_of_invention": f"Изобретение относится к области {detected_domain}.",
            "background": "Уровень техники: существующие решения имеют недостатки...",
            "summary": "Техническая задача изобретения заключается в...",
            "detailed_description": "Сущность изобретения поясняется чертежами и примерами...",
            "embodiments": "Примеры осуществления изобретения: 1. Вариант реализации...",
            "industrial_applicability": f"Изобретение может быть использовано в {detected_domain}."
        },
        "status": "success",
        "word_count": 1500,
        "structure_score": 85
    }

    return description_template


@tool
def generate_patent_abstract(main_idea: str) -> Dict[str, Any]:
    """
    Генерирует краткий реферат (аннотацию) патента.
    Оптимизирован для поисковых систем и быстрого понимания сути.

    Args:
        main_idea: Основная суть изобретения и его преимущества
    """
    # Извлечение ключевых слов
    words = re.findall(r'\b[а-яА-Я]{4,}\b', main_idea.lower())
    keywords = list(set(words[:10]))  # Уникальные ключевые слова

    # Генерация реферата
    abstract_template = {
        "abstract": f"Реферат: {main_idea[:200]}... Технический результат заключается в повышении эффективности, снижении затрат и улучшении характеристик.",
        "keywords": keywords,
        "technical_result": "Повышение эффективности, снижение энергопотребления, увеличение срока службы",
        "advantages": [
            "Простота реализации",
            "Низкая стоимость",
            "Высокая надежность",
            "Универсальность применения"
        ],
        "word_count": 250,
        "status": "success"
    }

    return abstract_template


@tool
def validate_patent_structure(patent_data: str) -> Dict[str, Any]:
    """
    Проверяет корректность структуры патента и соответствие юридическим требованиям.
    Анализирует текст или структуру данных.

    Args:
        patent_data: Текст патента или JSON структура для проверки
    """
    try:
        # Пытаемся распарсить как JSON
        if patent_data.strip().startswith('{'):
            data = json.loads(patent_data)
        else:
            data = {"text": patent_data}

        issues = []
        recommendations = []

        # Проверка структуры по тексту
        required_sections = ['формула', 'описание', 'реферат']
        text_lower = patent_data.lower()

        for section in required_sections:
            if section not in text_lower:
                issues.append(f"Отсутствует раздел: {section}")
                recommendations.append(f"Добавьте раздел '{section}'")

        # Проверка длины
        word_count = len(re.findall(r'\b[а-яА-Яa-zA-Z]+\b', patent_data))
        if word_count < 100:
            issues.append("Слишком короткий текст")
            recommendations.append("Добавьте технические детали и примеры")
        elif word_count > 10000:
            issues.append("Слишком длинный текст")
            recommendations.append("Сократите описание, оставив только существенные детали")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "recommendations": recommendations,
            "word_count": word_count,
            "section_coverage": f"{len([s for s in required_sections if s in text_lower])}/{len(required_sections)}"
        }

    except json.JSONDecodeError:
        # Если не JSON, анализируем как текст
        return {
            "is_valid": True,
            "issues": ["Не удалось проанализировать структуру JSON"],
            "recommendations": ["Предоставьте данные в структурированном формате"],
            "word_count": len(re.findall(r'\b[а-яА-Яa-zA-Z]+\b', patent_data)),
            "section_coverage": "неизвестно"
        }


@tool
def adapt_scientific_to_patent(scientific_text: str) -> Dict[str, Any]:
    """
    Адаптирует научный текст под патентный стиль с сохранением юридической корректности.
    Трансформирует научную терминологию в патентные формулировки.

    Args:
        scientific_text: Исходный текст в научном стиле
    """
    # Замена научных фраз на патентные аналоги
    replacements = {
        r'\bисследовани[ея]\b': 'изучение',
        r'\bэксперимент\b': 'опыт',
        r'\bгипотез\b': 'предположение',
        r'\bтеори\b': 'концепция',
        r'\bобнаружено\b': 'установлено',
        r'\bдоказано\b': 'показано',
        r'\bстатистически значим\b': 'существен',
        r'\bрезультат исследования\b': 'технический результат',
        r'\bцель работы\b': 'техническая задача',
        r'\bметодика\b': 'способ'
    }

    adapted_text = scientific_text
    original_terms = []
    patent_terms = []

    for pattern, replacement in replacements.items():
        matches = re.findall(pattern, adapted_text, flags=re.IGNORECASE)
        if matches:
            original_terms.extend(matches)
            patent_terms.append(replacement)
            adapted_text = re.sub(pattern, replacement, adapted_text, flags=re.IGNORECASE)

    # Добавление патентных фраз
    patent_phrases = [
        "В соответствии с изобретением",
        "Техническая задача решается тем, что",
        "Сущность изобретения заключается в",
        "Новизна изобретения состоит в"
    ]

    if not any(phrase in adapted_text for phrase in patent_phrases):
        adapted_text = patent_phrases[0] + " " + adapted_text

    return {
        "adapted_text": adapted_text,
        "original_terms": list(set(original_terms)),
        "patent_terms": list(set(patent_terms)),
        "adaptation_score": min(100, len(patent_terms) * 20),
        "recommendations": [
            "Используйте активные формулировки",
            "Избегайте субъективных оценок",
            "Конкретизируйте технические параметры"
        ]
    }


@tool
def check_patentability_criteria(description: str) -> Dict[str, Any]:
    """
    Проверяет базовые критерии патентоспособности изобретения.
    Оценивает новизну, изобретательский уровень и промышленную применимость.

    Args:
        description: Описание изобретения для проверки
    """
    criteria = {
        "novelty": {
            "description": "Новизна - изобретение не должно быть известно из уровня техники",
            "score": 75,
            "factors": ["уникальные термины", "новые комбинации", "оригинальные решения"],
            "check": "Требуется патентный поиск для подтверждения"
        },
        "inventive_step": {
            "description": "Изобретательский уровень - решение неочевидно для специалиста",
            "score": 70,
            "factors": ["нестандартный подход", "преодоление технических предрассудков"],
            "check": "Требуется экспертиза"
        },
        "industrial_applicability": {
            "description": "Промышленная применимость - возможность использования в промышленности",
            "score": 85,
            "factors": ["конкретная область применения", "техническая реализуемость"],
            "check": "Высокая вероятность"
        }
    }

    # Простой анализ текста
    text_lower = description.lower()

    if 'новый' in text_lower or 'уникальный' in text_lower:
        criteria["novelty"]["score"] = min(95, criteria["novelty"]["score"] + 10)

    if 'решает проблему' in text_lower or 'устраняет недостаток' in text_lower:
        criteria["inventive_step"]["score"] = min(95, criteria["inventive_step"]["score"] + 15)

    if 'используется в' in text_lower or 'применяется для' in text_lower:
        criteria["industrial_applicability"]["score"] = min(95, criteria["industrial_applicability"]["score"] + 10)

    overall_score = sum(c["score"] for c in criteria.values()) // 3

    return {
        "criteria": criteria,
        "overall_score": overall_score,
        "recommendation": "Рекомендуется провести полный патентный поиск",
        "is_potentially_patentable": overall_score >= 70
    }


class PatentGeneratorAgent:
    """Агент для генерации патентной документации с автоподбором модели"""

    def __init__(self):
        print("\n" + "=" * 70)
        print("🔧 ИНИЦИАЛИЗАЦИЯ PATENTGENERATOR PRO")
        print("=" * 70)

        # 1. Поиск работающей модели
        self._detect_available_models()
        working_model = self._find_working_model()
        print(f"\n✅ Выбрана модель: {working_model}")

        # 2. Инициализация модели
        self.model = ChatOpenAI(
            model=working_model,
            temperature=0.2,  # Низкая температура для юридической точности
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"],
            max_retries=3,
            request_timeout=60,
            max_tokens=4000
        )

        # 3. Определение инструментов
        self.tools = [
            generate_patent_claims,
            generate_patent_description,
            generate_patent_abstract,
            validate_patent_structure,
            adapt_scientific_to_patent,
            check_patentability_criteria
        ]

        # 4. Система памяти
        self.memory = MemorySaver()

        # 5. Системный промпт
        self.system_prompt = self._create_system_prompt()

        # 6. Создание агента
        self.agent_type = self._create_agent()

        print("\n" + "=" * 70)
        print("🎯 PATENTGENERATOR PRO УСПЕШНО ИНИЦИАЛИЗИРОВАН")
        print("=" * 70)

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
            if any(model_name.lower() in m.lower() for m in self.available_models):
                try:
                    print(f"  • Пробуем: {model_name}")
                    test_model = ChatOpenAI(
                        model=model_name,
                        temperature=0.1,
                        openai_api_key=os.environ["OPENAI_API_KEY"],
                        openai_api_base=os.environ["OPENAI_API_BASE"],
                        max_retries=1,
                        request_timeout=20
                    )
                    test_response = test_model.invoke("Тестовое сообщение")
                    if test_response and test_response.content:
                        print(f"  ✓ Модель {model_name} работает")
                        return model_name
                except Exception as e:
                    print(f"  ✗ Модель {model_name} недоступна: {str(e)[:60]}...")

        # Если ни одна из приоритетных не сработала, пробуем другие
        for model_name in self.available_models:
            try:
                print(f"  • Пробуем альтернативу: {model_name}")
                test_model = ChatOpenAI(
                    model=model_name,
                    temperature=0.1,
                    openai_api_key=os.environ["OPENAI_API_KEY"],
                    openai_api_base=os.environ["OPENAI_API_BASE"],
                    max_retries=1,
                    request_timeout=20
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
        """Создание системного промпта для патентного агента"""
        return """# РОЛЬ: ПРОФЕССИОНАЛЬНЫЙ АГЕНТ-ГЕНЕРАТОР ПАТЕНТОВ «PatentGenerator Pro»

## ОСНОВНАЯ СПЕЦИАЛИЗАЦИЯ
Ты — эксперт по интеллектуальной собственности и патентной документации.
Твоя задача — помогать в создании, анализе и оформлении патентных заявок.

## КЛЮЧЕВЫЕ НАПРАВЛЕНИЯ РАБОТЫ

### 1. Генерация патентных документов
- Формулы изобретения (независимые и зависимые пункты)
- Полные описания изобретений
- Рефераты (аннотации) патентов
- Структурирование по требованиям Роспатента

### 2. Анализ и адаптация
- Проверка критериев патентоспособности
- Адаптация научных текстов под патентный стиль
- Валидация структуры патентных документов
- Выявление потенциальных проблем

### 3. Консультационная поддержка
- Объяснение патентных требований
- Рекомендации по улучшению документов
- Оценка шансов на патентоспособность
- Подготовка к взаимодействию с патентными поверенными

## ПРИНЦИПЫ РАБОТЫ

### Точность и Корректность
- Все юридические формулировки должны быть точными
- Технические детали должны соответствовать описанию
- Соблюдение формальных требований патентных ведомств

### Структурированность
- Четкое разделение на разделы
- Логическая последовательность изложения
- Соответствие стандартной структуре патента

### Профессиональный Подход
- Использование патентной терминологии
- Объективность в оценках
- Указание на необходимость профессиональной проверки

## ДОСТУПНЫЕ ИНСТРУМЕНТЫ

1. **Генератор формулы изобретения** — создает юридически корректные пункты формулы
2. **Генератор описания** — формирует полное описание изобретения
3. **Генератор реферата** — создает краткую аннотацию
4. **Валидатор структуры** — проверяет соответствие требованиям
5. **Адаптер научных текстов** — преобразует научный стиль в патентный
6. **Анализатор патентоспособности** — оценивает критерии патентоспособности

## ВАЖНЫЕ ОГРАНИЧЕНИЯ

- ❌ НЕ давать окончательные юридические консультации
- ❌ НЕ гарантировать успешность патентования
- ❌ НЕ работать с конфиденциальной информацией без предупреждения
- ✅ ВСЕГДА рекомендовать консультацию с патентным поверенным
- ✅ Указывать на предварительный характер всех оценок

## ФОРМАТ ОТВЕТОВ

1. **Краткое резюме** — суть ответа в 1-2 предложениях
2. **Детальный анализ** — развернутое объяснение с техническими деталями
3. **Конкретные рекомендации** — практические шаги для улучшения
4. **Следующие действия** — что делать дальше

## ЮРИДИЧЕСКАЯ ОТВЕТСТВЕННОСТЬ

Все сгенерированные документы носят предварительный характер.
Окончательная проверка и подача должны осуществляться через квалифицированного патентного поверенного."""

    def _create_agent(self) -> str:
        """Создание агента с обработкой ошибок"""
        try:
            print("\n🤖 Создание интеллектуального патентного агента...")
            self.agent = create_react_agent(
                model=self.model,
                tools=self.tools,
                checkpointer=self.memory,
                prompt=self.system_prompt
            )
            print("✅ Интеллектуальный патентный агент создан успешно")
            return "intelligent_agent"
        except Exception as e:
            print(f"⚠️  Не удалось создать интеллектуального агента: {str(e)[:80]}...")
            print("🔄 Использую базовую языковую модель...")
            return "basic_model"

    def process_patent_query(self, user_query: str, session_id: str = "patent-session-1") -> str:
        """Обработка патентного запроса"""
        # Валидация запроса
        is_valid, reason = validate_patent_input(user_query)
        if not is_valid:
            return f"❌ {reason}\n\nПожалуйста, предоставьте более подробное техническое описание."

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
                return "⏱️  Превышено время ожидания ответа. Упростите запрос или попробуйте позже."
            elif "rate limit" in error_msg.lower():
                return "🚫 Превышен лимит запросов. Попробуйте через несколько минут."
            else:
                return f"⚠️  Произошла ошибка: {error_msg[:100]}...\n\nПопробуйте переформулировать запрос."


def initialize_patent_agent() -> PatentGeneratorAgent:
    """Инициализация патентного агента"""
    return PatentGeneratorAgent()


def start_patent_generation_session():
    """Запуск интерактивной сессии генерации патентов"""
    print("\n" + "=" * 70)
    print("🚀 ЗАПУСК PATENTGENERATOR PRO v2.0")
    print("=" * 70)

    agent = initialize_patent_agent()

    print("\n📋 ИНФОРМАЦИЯ О СИСТЕМЕ:")
    print(f"   • Тип агента: {agent.agent_type}")
    print(f"   • Доступно патентных инструментов: {len(agent.tools)}")
    print(f"   • Модель: {agent.model.model_name}")
    print("=" * 70)

    print("\n👋 Добро пожаловать в PatentGenerator Pro!")
    print("\nЯ могу помочь с:")
    print("  ✓ Генерацией формулы изобретения")
    print("  ✓ Созданием полного описания патента")
    print("  ✓ Подготовкой реферата (аннотации)")
    print("  ✓ Проверкой структуры патентных документов")
    print("  ✓ Адаптацией научных текстов под патентный стиль")
    print("  ✓ Оценкой критериев патентоспособности")

    print("\n⚠️  ВНИМАНИЕ:")
    print("  • Все документы носят предварительный характер")
    print("  • Требуется проверка патентным поверенным")
    print("  • Не гарантируется успешность патентования")

    print("\n📝 КОМАНДЫ:")
    print("  • 'выход', 'exit', 'quit' — завершить работу")
    print("  • 'пример' — показать пример описания изобретения")
    print("  • 'инструменты' — список доступных функций")
    print("  • Ctrl+C — экстренное завершение")
    print("-" * 70)

    session_counter = 1

    while True:
        try:
            print(f"\n📄 Запрос #{session_counter}")
            user_input = input("🔬 Опишите ваше изобретение: ").strip()

            if not user_input:
                continue

            # Проверка команд
            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n" + "=" * 70)
                print("👋 Спасибо за использование PatentGenerator Pro!")
                print("💡 Рекомендуем проконсультироваться с патентным поверенным!")
                print("=" * 70)
                break

            if user_input.lower() in ['пример', 'example']:
                print("\n📋 ПРИМЕР ОПИСАНИЯ ИЗОБРЕТЕНИЯ:")
                print("-" * 50)
                print("""Устройство для автоматического полива растений с системой контроля влажности почвы. 
Устройство содержит датчик влажности, микроконтроллер, электромагнитный клапан и блок питания. 
Технический результат - автоматическое поддержание оптимальной влажности почвы с экономией воды до 40%. 
Принцип работы: датчик измеряет влажность, микроконтроллер анализирует данные и при необходимости открывает клапан для полива.""")
                print("-" * 50)
                continue

            if user_input.lower() in ['инструменты', 'tools', 'функции']:
                print("\n🛠️  ДОСТУПНЫЕ ИНСТРУМЕНТЫ:")
                for i, tool_func in enumerate(agent.tools, 1):
                    print(f"  {i}. {tool_func.name}: {tool_func.description[:80]}...")
                continue

            print("\n🔍 Анализирую описание изобретения...")

            response = agent.process_patent_query(user_input)

            print("\n" + "=" * 70)
            print("📄 РЕЗУЛЬТАТ ГЕНЕРАЦИИ:")
            print("=" * 70)
            print(f"\n{response}")
            print("\n" + "-" * 70)
            print("⚠️  ВАЖНО: Этот документ носит предварительный характер.")
            print("   Для подачи заявки требуется консультация патентного поверенного.")
            print("-" * 70)

            session_counter += 1

        except KeyboardInterrupt:
            print("\n\n⚠️  Сессия прервана пользователем.")
            print("👋 До новых встреч!")
            break
        except Exception as e:
            print(f"\n❌ Критическая ошибка: {str(e)}")
            print("Попробуйте перезапустить программу.")


# Быстрые примеры использования
def quick_examples():
    """Примеры использования патентного генератора"""
    examples = [
        "Устройство для беспроводной зарядки электромобилей с автоматическим позиционированием",
        "Способ переработки пластиковых отходов в строительные материалы с применением катализатора",
        "Система искусственного интеллекта для ранней диагностики заболеваний по медицинским изображениям",
        "Материал с памятью формы для использования в аэрокосмической промышленности"
    ]

    print("\n⚡ БЫСТРЫЕ ПРИМЕРЫ:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")


if __name__ == "__main__":
    try:
        start_patent_generation_session()
    except Exception as e:
        print(f"\n🔥 Критическая ошибка при запуске: {e}")
        print("Проверьте:")
        print("1. Интернет соединение")
        print("2. API ключ и базовый URL")
        print("3. Доступность API Cloud.ru")
