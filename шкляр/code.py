import os
from typing import Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

os.environ["OPENAI_API_KEY"] = "YjRhZDJhY2UtM2E3NS00ZjAzLWJmNzctZWE1MWY0YmE1OTVh.2c0cb60717718eecc1aac50faea7c6b3"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"


@tool
def generate_patent_claims(invention_description: str) -> Dict[str, str]:
    """
    Генерирует юридически корректную формулу изобретения на основе описания.

    Args:
        invention_description: Детальное описание изобретения, его технических особенностей и новизны
    """
    # В реальной реализации здесь будет шаблон и логика генерации
    return {
        "claims": "1. Устройство по п.1, отличающееся тем, что...\n2. Способ по п.1, включающий этапы...",
        "status": "success",
        "section": "formula_izobreteniya"
    }


@tool
def generate_patent_description(technical_details: str) -> Dict[str, str]:
    """
    Создает полное описание изобретения в патентном стиле.

    Args:
        technical_details: Технические характеристики, принцип работы, область применения
    """
    return {
        "description": "Изобретение относится к области... Технический результат заключается в...",
        "status": "success",
        "section": "opisanie"
    }


@tool
def generate_patent_abstract(main_idea: str) -> Dict[str, str]:
    """
    Генерирует краткий реферат (аннотацию) патента.

    Args:
        main_idea: Основная суть изобретения и его преимущества
    """
    return {
        "abstract": "Полезная модель предназначена для... Основные преимущества:...",
        "status": "success",
        "section": "referat"
    }


@tool
def validate_patent_structure(patent_data: Dict[str, str]) -> Dict[str, any]:
    """
    Проверяет корректность структуры патента и соответствие юридическим требованиям.

    Args:
        patent_data: Словарь с разделами патента для проверки
    """
    return {
        "is_valid": True,
        "issues": [],
        "recommendations": ["Рекомендуется уточнить формулу изобретения", "Добавить примеры реализации"]
    }


@tool
def adapt_scientific_to_patent(scientific_text: str) -> Dict[str, str]:
    """
    Адаптирует научный текст под патентный стиль с сохранением юридической корректности.

    Args:
        scientific_text: Исходный текст в научном стиле
    """
    return {
        "adapted_text": "В соответствии с изобретением... Техническая задача решается тем, что...",
        "original_terms": ["научный термин"],
        "patent_terms": ["патентный термин"]
    }


model = ChatOpenAI(
    model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
    temperature=0.3,  # Снижена для большей консервативности в юридических текстах
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"]
)

tools = [
    generate_patent_claims,
    generate_patent_description,
    generate_patent_abstract,
    validate_patent_structure,
    adapt_scientific_to_patent
]

memory = MemorySaver()

system_prompt = """
### ПРОМПТ ДЛЯ АГЕНТА-ГЕНЕРАТОРА ПАТЕНТОВ «PatentGenerator Pro»

**1. Идентификация и Назначение**

* Ты — профессиональный Агент-Генератор патентной документации «PatentGenerator Pro»
* Специализация: автоматическая генерация юридически корректных патентных документов
* Твоя задача: создавать качественные патентные разделы на основе технических описаний

**2. Основные Функциональные Возможности**

А. Генерация основных разделов патента:
   - Формула изобретения (Claims) — юридически точная и защищаемая
   - Полное описание изобретения (Description)
   - Реферат (Abstract) — краткая аннотация

Б. Адаптация стиля:
   - Преобразование научного стиля в патентный
   - Обеспечение юридической корректности формулировок
   - Использование стандартных патентных шаблонов

**3. Принципы Работы**


* Точность: Все технические детали должны быть точно отражены
* Юридическая корректность: Соблюдение патентных требований и форматов
* Полнота: Все существенные аспекты изобретения должны быть раскрыты
* Ясность: Текст должен быть понятен эксперту в данной области

**4. Протокол Взаимодействия**

Шаг 1: Анализ входных данных
  - Определение типа изобретения (устройство, способ, вещество)
  - Выявление ключевых технических особенностей

Шаг 2: Выбор подходящих инструментов генерации
  - Формула изобретения для юридической защиты
  - Описание для раскрытия сущности
  - Реферат для краткого представления

Шаг 3: Валидация и адаптация
  - Проверка корректности структуры
  - Адаптация стиля при необходимости

**5. Требования к Качеству**

* Формула изобретения должна четко определять объем правовой защиты
* Описание должно позволять воспроизведение изобретения специалистом
* Реферат должен точно отражать сущность и преимущества
* Все разделы должны соответствовать патентным требованиям

**6. Ограничения**

* НЕ давать юридические консультации
* НЕ гарантировать успешность патентования
* НЕ работать с конфиденциальной информацией без предупреждения
* Всегда указывать на необходимость проверки патентным поверенным
"""

agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=memory,
    prompt=system_prompt
)


def run_agent():
    config = {"configurable": {"thread_id": "patent-session-1"}}

    print("=" * 70)
    print(" АГЕНТ-ГЕНЕРАТОР ПАТЕНТНОЙ ДОКУМЕНТАЦИИ")
    print(" PatentGenerator Pro")
    print("=" * 70)
    print("\nГотов к генерации патентных документов.")
    print("Могу создать: формулу изобретения, описание, реферат.")
    print("Введите 'выход' для завершения работы.\n")

    while True:
        user_input = input("🔬 Введите описание изобретения: ").strip()

        if user_input.lower() in ['выход', 'exit', 'quit']:
            print("\n✅ Работа завершена. Рекомендуется проконсультироваться с патентным поверенным!")
            break

        if not user_input:
            continue

        print("\n⚙️ PatentGenerator Pro обрабатывает запрос...\n")

        try:
            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )

            last_message = response["messages"][-1]
            print(f"📄 Результат: {last_message.content}\n")
            print("-" * 70 + "\n")

        except Exception as e:
            print(f"❌ Ошибка генерации: {str(e)}")
            print("Пожалуйста, проверьте описание и попробуйте снова.\n")
            print("-" * 70 + "\n")


if __name__ == "__main__":
    run_agent()

