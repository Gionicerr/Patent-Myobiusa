import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import re

os.environ["OPENAI_API_KEY"] = "ZDU2NzgzYmItNzQxYS00MWM5LWIwNjgtNzMxZTE5MWVlMzZm.2af17b95eeb186a39e21eda686687b64"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"


def is_valid_patent_description(text: str) -> tuple[bool, str]:
    """
    Проверяет, является ли текст осмысленным патентным описанием.
    Возвращает (is_valid, reason)
    """
    # Проверка на слишком короткий текст
    if len(text.strip()) < 20:
        return False, "Текст слишком короткий для патентного описания."
    
    # Проверка на набор случайных символов
    random_pattern = r"^[^a-zA-Zа-яА-Я0-9]{10,}$|([^a-zA-Zа-яА-Я0-9\s]{5,})"
    if re.search(random_pattern, text):
        return False, "Текст содержит слишком много случайных символов."
    
    # Проверка на повторяющиеся символы или слова
    repeated_chars = re.findall(r"(.)\1{5,}", text)
    if repeated_chars:
        return False, "Обнаружены повторяющиеся последовательности символов."
    
    # Проверка на минимальное количество слов
    words = re.findall(r'\b[а-яА-Яa-zA-Z]{2,}\b', text)
    if len(words) < 5:
        return False, "Недостаточно осмысленных слов для анализа."
    
    # Проверка на соотношение букв и символов
    letters = re.findall(r'[а-яА-Яa-zA-Z]', text)
    if len(letters) / len(text) < 0.3:
        return False, "Текст содержит недостаточно буквенных символов."
    
    # Проверка на наличие технических или патентных терминов
    patent_terms = ['изобретение', 'устройство', 'способ', 'технический', 'патент', 
                   'формула', 'описание', 'новый', 'улучшенный', 'конструкция']
    found_terms = sum(1 for term in patent_terms if term in text.lower())
    if found_terms < 1:
        return False, "Текст не содержит характерных для патентного описания терминов."
    
    return True, "Текст прошел базовую проверку."


@tool
def check_patent_requirements(description: str) -> str:
    """
    Проверяет патентное описание на соответствие основным юридическим требованиям.
    Args:
        description: текст патентного описания для проверки.
    """
    # Сначала проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно проверить описание: {reason}"
    
    issues = []
    
    # Проверка на наличие основных разделов
    required_sections = ["описание изобретения", "формула", "реферат", "область техники"]
    missing_sections = []
    
    for section in required_sections:
        if section not in description.lower():
            missing_sections.append(section)
    
    if missing_sections:
        issues.append(f"Отсутствуют обязательные разделы: {', '.join(missing_sections)}")
    
    # Проверка на новизну и изобретательский уровень
    if len(description.split()) < 500:
        issues.append("Описание слишком краткое. Рекомендуется подробно раскрыть сущность изобретения (минимум 500 слов)")
    
    # Проверка на промышленную применимость
    if "применение" not in description.lower() and "использование" not in description.lower():
        issues.append("Не указана промышленная применимость изобретения")
    
    if issues:
        return "Проблемы:\n" + "\n".join(f"- {issue}" for issue in issues)
    else:
        return "Описание соответствует основным требованиям. Рекомендуется провести патентный поиск перед подачей."


@tool
def analyze_novelty(description: str) -> str:
    """
    Анализирует новизну изобретения на основе представленного описания.
    Args:
        description: патентное описание для анализа новизны.
    """
    # Проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно проанализировать новизну: {reason}"
    
    # Анализ ключевых характеристик новизны
    novelty_indicators = [
        "новый способ",
        "уникальное устройство", 
        "улучшенная конструкция",
        "новое применение",
        "технический результат"
    ]
    
    found_indicators = []
    for indicator in novelty_indicators:
        if indicator in description.lower():
            found_indicators.append(indicator)
    
    if found_indicators:
        return f"Обнаружены признаки новизны: {', '.join(found_indicators)}. Рекомендуется провести углубленный патентный поиск."
    else:
        return "Признаки новизны выражены слабо. Рекомендуется четче сформулировать отличительные особенности изобретения."


@tool
def check_formality_requirements(description: str) -> str:
    """
    Проверяет соответствие формальным требованиям к патентной заявке.
    Args:
        description: текст для проверки формальных требований.
    """
    # Проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно проверить формальные требования: {reason}"
    
    formal_issues = []
    
    # Проверка структуры
    if not any(char.isdigit() for char in description):
        formal_issues.append("Рекомендуется добавить нумерацию разделов или пунктов")
    
    # Проверка на технические термины
    technical_terms = ["устройство", "способ", "средство", "элемент", "механизм"]
    found_terms = [term for term in technical_terms if term in description.lower()]
    
    if len(found_terms) < 2:
        formal_issues.append("Недостаточно технических терминов. Уточните техническую сущность изобретения")
    
    # Проверка на наличие формулы изобретения
    if "формула изобретения" not in description.lower():
        formal_issues.append("Отсутствует формула изобретения - обязательный элемент патентной заявки")
    
    if formal_issues:
        return "Формальные замечания:\n" + "\n".join(f"- {issue}" for issue in formal_issues)
    else:
        return "Формальные требования соблюдены."


@tool
def suggest_improvements(description: str) -> str:
    """
    Предлагает конкретные улучшения для патентного описания.
    Args:
        description: текст для анализа и предложения улучшений.
    """
    # Проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно предложить улучшения: {reason}"
    
    suggestions = []
    
    # Анализ полноты описания
    word_count = len(description.split())
    if word_count < 800:
        suggestions.append("Увеличить объем описания до 800-1500 слов для полноты раскрытия сущности изобретения")
    
    # Проверка на конкретность
    if "например" not in description.lower() and "предпочтительный вариант" not in description.lower():
        suggestions.append("Добавить конкретные примеры реализации или предпочтительные варианты исполнения")
    
    # Проверка на наличие чертежей
    if "чертеж" not in description.lower() and "рисунок" not in description.lower():
        suggestions.append("Рекомендуется подготовить графические материалы (чертежи, схемы, рисунки)")
    
    # Проверка на юридическую корректность
    if "патентная чистота" not in description.lower():
        suggestions.append("Проверить патентную чистоту и отсутствие нарушений исключительных прав третьих лиц")
    
    return "Рекомендации по улучшению:\n" + "\n".join(f"- {suggestion}" for suggestion in suggestions)


@tool
def estimate_processing_time(complexity: str) -> str:
    """
    Оценивает сроки рассмотрения патентной заявки в зависимости от сложности.
    Args:
        complexity: оценка сложности изобретения.
    """
    complexity = complexity.lower()
    
    if "простой" in complexity:
        return "Ожидаемый срок рассмотрения: 6-8 месяцев"
    elif "средний" in complexity:
        return "Ожидаемый срок рассмотрения: 8-12 месяцев"
    elif "сложный" in complexity:
        return "Ожидаемый срок рассмотрения: 12-18 месяцев"
    else:
        return "Стандартный срок рассмотрения: 10-12 месяцев. Сложные заявки могут рассматриваться до 24 месяцев."


class PatentExpert:
    """Эксперт по проверке патентных описаний"""
    
    def __init__(self):
        self.model = ChatOpenAI(
            model="deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
            temperature=0.2,  # Низкая температура для точности юридических проверок
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"]
        )
        
        self.tools = [
            check_patent_requirements,
            analyze_novelty,
            check_formality_requirements,
            suggest_improvements,
            estimate_processing_time
        ]
        self.memory = MemorySaver()
        
        self.system_prompt = """
Ты — эксперт по патентованию документов. Пользователь будет отправлять патентное описание своей работы. 
Твоя задача проверять текст, соответствует ли он юридическим требованиям и выдавать конечный ответ с описанием того что нужно исправить, если есть проблемы.

Основные аспекты проверки:
1. Соответствие формальным требованиям Роспатента
2. Наличие всех обязательных разделов (описание, формула, реферат)
3. Новизна и изобретательский уровень
4. Промышленная применимость
5. Полнота и ясность раскрытия сущности изобретения

После получения патентного описания:
- Тщательно проанализируй текст
- Используй доступные инструменты для проверки разных аспектов
- Составь структурированный отчет с выявленными проблемами
- Предложи конкретные рекомендации по исправлению
- Укажи на сильные стороны описания

Если пользователь отправляет явно бессмысленный текст (набор символов, слишком короткий текст, повторяющиеся символы) - вежливо сообщи об этом и попроси прислать настоящее патентное описание.

Всегда завершай проверку четким выводом о том, готово ли описание к подаче в патентное ведомство или требует доработки.
"""

        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            checkpointer=self.memory,
            prompt=self.system_prompt
        )

    def process_patent_description(self, description: str, thread_id: str = "patent-check-1") -> str:
        """Обрабатывает патентное описание и возвращает результат проверки"""
        # Предварительная проверка на валидность
        is_valid, reason = is_valid_patent_description(description)
        if not is_valid:
            return f"❌ Не могу обработать ваш запрос: {reason}\n\nПожалуйста, пришлите настоящее патентное описание для экспертизы."
        
        config = {"configurable": {"thread_id": thread_id}}
        
        try:
            response = self.agent.invoke(
                {"messages": [{"role": "user", "content": f"Проверь следующее патентное описание: {description}"}]},
                config=config
            )
            
            last_message = response["messages"][-1]
            return last_message.content
            
        except Exception as e:
            return f"Произошла ошибка при проверке описания: {str(e)}"


def create_patent_expert() -> PatentExpert:
    """Фабрика для создания эксперта по патентованию"""
    return PatentExpert()


def run_patent_check():
    """Запускает сессию проверки патентных описаний"""
    expert = create_patent_expert()
    
    print("=" * 60)
    print("        ЭКСПЕРТНАЯ ПРОВЕРКА ПАТЕНТНЫХ ОПИСАНИЙ")
    print("=" * 60)
    
    print("\nПривет, чем я могу тебе помочь?\n")

    while True:
        try:
            user_input = input("📝 Твое описание: ").strip()

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n✅ Спасибо за обращение! Удачи в патентовании!")
                break

            if not user_input:
                continue

            print("\n🔍 Проверяю описание на соответствие требованиям...\n")

            response = expert.process_patent_description(user_input)
            print(f"📊 Результат проверки:\n{response}\n")
            print("-" * 60 + "\n")

        except KeyboardInterrupt:
            print("\n\n✅ Проверка завершена. Удачи в оформлении документов!")
            break
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            print("Попробуй отправить описание еще раз.\n")


# Дополнительные инструменты для специфических проверок
@tool
def check_international_requirements(description: str) -> str:
    """
    Проверяет соответствие требованиям для международного патентования.
    Args:
        description: патентное описание для международной проверки.
    """
    # Проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно проверить международные требования: {reason}"
    
    intl_requirements = [
        "Соответствие требованиям РСТ (Договор о патентной кооперации)",
        "Возможность перевода на английский язык",
        "Учет международной классификации изобретений (МПК)",
        "Соответствие требованиям выбранных стран патентования"
    ]
    
    return "Международные требования:\n" + "\n".join(f"- {req}" for req in intl_requirements)


@tool
def verify_technical_disclosure(description: str) -> str:
    """
    Проверяет полноту раскрытия технической сущности изобретения.
    Args:
        description: описание для проверки технического раскрытия.
    """
    # Проверяем валидность описания
    is_valid, reason = is_valid_patent_description(description)
    if not is_valid:
        return f"Невозможно проверить техническое раскрытие: {reason}"
    
    technical_elements = [
        "Принцип действия",
        "Конструктивные особенности", 
        "Технический результат",
        "Сравнение с прототипом",
        "Преимущества перед аналогами"
    ]
    
    found_elements = []
    for element in technical_elements:
        if any(word in description.lower() for word in element.lower().split()):
            found_elements.append(element)
    
    if len(found_elements) >= 3:
        return f"Техническое раскрытие удовлетворительное. Обнаружены: {', '.join(found_elements)}"
    else:
        return "Техническое раскрытие недостаточное. Рекомендуется детализировать принцип действия и технические преимущества."


if __name__ == "__main__":
    run_patent_check()
