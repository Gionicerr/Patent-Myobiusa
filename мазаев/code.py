import os
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
import requests

os.environ["OPENAI_API_KEY"] = "MjgwODM3NjQtNmNkYS00NjYwLWE5ZWMtNjczYzhiOWM0NDk5.c6410844ed69b95a2c1eca92f9f43678"
os.environ["OPENAI_API_BASE"] = "https://foundation-models.api.cloud.ru/v1"

# Сначала проверим, какие модели доступны
def check_available_models():
    try:
        from openai import OpenAI
        client = OpenAI(
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_API_BASE"]
        )
        models = client.models.list()
        print("Доступные модели:")
        for model in models.data:
            print(f"- {model.id}")
        return [model.id for model in models.data]
    except Exception as e:
        print(f"Ошибка при получении списка моделей: {e}")
        # Возвращаем список вероятно доступных моделей для Cloud.ru
        return ["gpt-3.5-turbo", "gpt-4", "sbert-ru-sentiment-rusentiment", "rugpt3large_based_on_gpt2"]

@tool
def get_help(topic: str) -> str:
    """
    Краткая справка по популярным ситуациям техподдержки.
    Args:
        topic: формулировка проблемы или вопроса пользователя.
    """
    topic = topic.lower()
    if "пароль" in topic:
        return "Чтобы восстановить пароль: нажмите 'Забыли пароль', введите email и следуйте инструкции из письма."
    if "генер" in topic:
        return "Если генерация не работает: попробуйте обновить страницу, очистить кеш и проверить интернет."

    if "ошибка" in topic or "500" in topic:
        return "Ошибка сервера: попробуйте еще раз через 10 минут. Если не заработает — напишите нам."
    return "Извините, пока нет конкретной инструкции по этому вопросу. Опишите проблему подробнее!"


@tool
def create_ticket(problem: str) -> str:
    """
    Создает заявку в техподдержку.
    Args:
        problem: описание проблемы.
    """
    return f"Ваша заявка принята! Описание: '{problem}'. Мы постараемся ответить в течение 24 часов."


@tool
def check_status() -> str:
    """
    Проверяет статус сервиса. Всегда возвращает, что всё работает.
    """
    return "Сервис работает нормально. Все системы доступны. Если у вас есть трудности — опишите их здесь."


# Проверяем доступные модели
print("Проверяем доступные модели...")
available_models = check_available_models()

# Пробуем разные модели, начиная с наиболее вероятных
working_model = None
for model_name in available_models:
    try:
        print(f"Пробуем модель: {model_name}")
        test_model = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            openai_api_base=os.environ["OPENAI_API_BASE"],
            max_retries=1,
            request_timeout=10
        )
        # Тестируем модель простым запросом
        test_response = test_model.invoke("Привет")
        working_model = model_name
        print(f"✅ Модель {model_name} работает!")
        break
    except Exception as e:
        print(f"❌ Модель {model_name} не работает: {str(e)[:100]}...")

if not working_model:
    # Если автоматический подбор не сработал, используем fallback
    print("Не удалось найти работающую модель. Используем резервный вариант...")
    working_model = "gpt-3.5-turbo"  # Все равно попробуем

print(f"Используем модель: {working_model}")

model = ChatOpenAI(
    model=working_model,
    temperature=0.7,
    openai_api_key=os.environ["OPENAI_API_KEY"],
    openai_api_base=os.environ["OPENAI_API_BASE"],
    max_retries=2,
    request_timeout=30
)

tools = [get_help, create_ticket, check_status]
memory = MemorySaver()

system_prompt = """
### ПРОМПТ ДЛЯ АГЕНТА ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ «Патентные описания»

**1. Введение и Идентификация Агента**

* Ты — официальный Агент Технической Поддержки сервиса «Патентные описания».
* Твое имя: «Тех-Агент Инвокер»
* Твоя главная цель: предоставлять быструю, точную, дружелюбную и профессиональную помощь пользователям.

**2.
Основные Принципы и Тон Общения**

* Тон: Всегда дружелюбный, терпеливый, поддерживающий и профессиональный.
* Эмпатия: Всегда начинай с выражения понимания проблемы пользователя.
* Ясность: Объясняй сложные вещи простым, понятным языком.

**3. Инструменты**

У тебя есть доступ к следующим инструментам:

- get_help: Получить справку по популярным проблемам
- create_ticket: Создать заявку в техподдержку  
- check_status: Проверить статус сервиса

**4. Протокол работы**

1. Поприветствуй пользователя и представься
2. Выясни проблему
3. Используй подходящие инструменты для помощи
4. Предложи решение или создай заявку
5. Убедись, что проблема решена

**5. Запреты**

* НЕЛЬЗЯ: Быть грубым или нетерпеливым.
* НЕЛЬЗЯ: Давать ложные гарантии.
* ВСЕГДА: Действуй в интересах пользователя.
"""

try:
    agent = create_react_agent(
        model=model,
        tools=tools,
        checkpointer=memory,
        prompt=system_prompt
    )
    print("✅ Агент успешно создан!")
except Exception as e:
    print(f"❌ Ошибка при создании агента: {e}")
    print("Создаем упрощенного агента...")
    # Резервный вариант - создаем простого агента без сложной логики
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    
    agent = create_tool_calling_agent(model, tools, prompt)
    agent = AgentExecutor(agent=agent, tools=tools, verbose=True)


def run_agent():
    config = {"configurable": {"thread_id": "user-session-1"}}

    print("=" * 70)
    print("       АГЕНТ ТЕХНИЧЕСКОЙ ПОДДЕРЖКИ «Патентные описания»")
    print("                    Тех-Агент Инвокер")
    print("=" * 70)
    print("\nДобро пожаловать! Я здесь, чтобы помочь вам решить любые проблемы.")
    print("Введите 'выход' для завершения работы.\n")

    while True:
        try:
            user_input = input("🙋 Вы: ").strip()

            if user_input.lower() in ['выход', 'exit', 'quit']:
                print("\n✅ Спасибо за обращение! Хорошего дня!")
                break

            if not user_input:
                continue

            print("\n🤖 Тех-Агент Инвокер обрабатывает ваш запрос...\n")

            response = agent.invoke(
                {"messages": [{"role": "user", "content": user_input}]},
                config=config
            )

            last_message = response["messages"][-1]
            print(f"💬 Тех-Агент Инвокер: {last_message.content}\n")
            print("-" * 70 + "\n")

        except KeyboardInterrupt:
            print("\n\n✅ Работа агента завершена. До свидания!")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {str(e)}")
            print("Но я все равно могу помочь! Опишите вашу проблему:")
            print("1. Проблемы с паролем")
            print("2. Проблемы с генерацией")
            print("3. Ошибки сервера")
            print("4. Создать заявку в поддержку")
            print("-" * 70 + "\n")


if __name__ == "__main__":
    run_agent()
