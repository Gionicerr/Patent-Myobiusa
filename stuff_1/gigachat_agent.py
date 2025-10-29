from fastapi.responses import JSONResponse
import os
import httpx
import json
import time
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# ===== ФИКС ДЛЯ КЛЮЧЕЙ С == =====


def get_safe_env(key):
    """Безопасное получение переменных с обработкой =="""
    value = os.getenv(key)
    if value:
        # Убираем кавычки если есть
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        elif value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
    return value


# Получаем ключи безопасно
CLIENT_ID = get_safe_env("GIGACHAT_CLIENT_ID")
CLIENT_SECRET = get_safe_env("GIGACHAT_CLIENT_SECRET")

print("=" * 50)
print("🔍 Проверка ключей GigaChat:")
print(
    f"Client ID: {'✅' if CLIENT_ID else '❌'} {CLIENT_ID[:10] if CLIENT_ID else 'НЕ НАЙДЕН'}...")
print(
    f"Client Secret: {'✅' if CLIENT_SECRET else '❌'} {CLIENT_SECRET[:10] if CLIENT_SECRET else 'НЕ НАЙДЕН'}...")
print("=" * 50)

# ===== НАСТРОЙКА GIGACHAT =====


class GigaChatClient:
    def __init__(self):
        if not CLIENT_ID or not CLIENT_SECRET:
            raise Exception("Ключи GigaChat не настроены. Проверьте файл .env")

        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.api_url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        self._token = None
        self._token_expires = 0

    async def get_token(self):
        """Получаем токен для доступа к GigaChat"""
        if self._token and time.time() < self._token_expires:
            return self._token

        print("🔑 Получаю токен GigaChat...")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.auth_url,
                    data={"scope": "GIGACHAT_API_PERS"},
                    auth=(self.client_id, self.client_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"}
                )

                if response.status_code == 200:
                    data = response.json()
                    self._token = data["access_token"]
                    self._token_expires = time.time() + \
                        data["expires_in"] - 300
                    print("✅ Токен получен успешно!")
                    return self._token
                else:
                    error_text = response.text[:100]
                    raise Exception(
                        f"Ошибка авторизации GigaChat: {response.status_code} - {error_text}")

        except Exception as e:
            print(f"❌ Ошибка при получении токена: {e}")
            raise

    async def send_message(self, text: str):
        """Отправляем запрос к GigaChat"""
        token = await self.get_token()

        # СИСТЕМНЫЙ ПРОМПТ ДЛЯ ПАТЕНТНОГО АНАЛИЗА
        system_prompt = """Ты — AI-агент "ПатентныйАнализатор", специалист по анализу научно-технических работ для патентования. Твоя задача — проводить глубокий анализ представленных материалов и структурировать их по стандартам патентной заявки.

СТАНДАРТ АНАЛИЗА:
1. Выявлять фундаментальные принципы и техническую сущность
2. Структурировать информацию по разделам патентной заявки  
3. Оценивать новизну и патентоспособность
4. Формулировать потенциальные пункты формулы изобретения"""

        user_prompt = f"""
ПРОАНАЛИЗИРУЙ ПРЕДСТАВЛЕННУЮ НАУЧНО-ТЕХНИЧЕСКУЮ РАБОТУ ДЛЯ ПАТЕНТОВАНИЯ:

ТЕКСТ РАБОТЫ:
{text[:10000]}

ИНСТРУКЦИЯ ПО АНАЛИЗУ:

РАЗДЕЛ 3: СУЩНОСТЬ РЕШЕНИЯ
3.1. Фундаментальный принцип: Выяви и опиши фундаментальный физический, химический, биологический или математический принцип, на котором основано решение.

3.2. Конструкция/Алгоритм/Состав:
- Детальное, пошаговое описание
- Для устройства — перечень ключевых элементов и их взаимосвязь
- Для способа — последовательность и условия осуществления этапов  
- Для вещества/композиции — точный количественный и качественный состав
- Для ПО/алгоритма — блок-схема, псевдокод или описание ключевых математических преобразований
- КРИТИЧЕСКИ ВАЖНО: Укажи отличительные признаки по сравнению с прототипом

3.3. Реализация (Примеры выполнения):
- Конкретные параметры, материалы, программные библиотеки, архитектуры сетей
- Практические примеры воплощения решения

РАЗДЕЛ 4: ОЖИДАЕМЫЙ ИЛИ ДОСТИГНУТЫЙ РЕЗУЛЬТАТ
4.1. Технический результат:
- Количественные показатели: "скорость возрастает на X%", "точность повышается до Y", "потребляемая мощность снижается на Z%"
- Качественные показатели: "появляется возможность...", "обеспечивается устойчивость к..."

4.2. Механизм достижения результата:
- Объясни причинно-следственную связь: "Благодаря введению нового элемента X, который взаимодействует с Y по схеме Z, достигается результат R"

РАЗДЕЛ 5: ОЦЕНКА НОВИЗНЫ И ПАТЕНТОСПОСОБНОСТИ
5.1. Анализ новизны:
- Четко сформулируй, что именно является абсолютно новым
- Раздели на: Новый принцип действия, Новая комбинация известных элементов, Новое применение известного объекта

5.2. Потенциальные независимые пункты формулы изобретения:
- Сформулируй 1-2 ключевых пункта в свободной форме
- Пример: "1. Способ X, отличающийся тем, что, с целью достижения Y, этап A осуществляют с использованием B при условиях C."

5.3. Предварительная оценка патентоспособности:
- Укажи уровень: Высокий / Повышенный / Средний / Низкий 
- Кратко аргументируй, ссылаясь на разделы 5.1 и 4.1

ЗАКЛЮЧИТЕЛЬНОЕ ДЕЙСТВИЕ:
Сгенерируй финальный документ «Предварительное описание изобретения», структурированный по разделам выше, и добавь Аналитический комментарий с предварительной оценкой по критериям [N-I-P] и общим уровнем патентоспособности.

ВЕРНИ РЕЗУЛЬТАТ В СЛЕДУЮЩЕЙ JSON СТРУКТУРЕ:
{{
  "analysis_report": {{
    "fundamental_principle": "Фундаментальный физический/химический/биологический/математический принцип, на котором основано решение",
    "technical_implementation": {{
      "construction_algorithm_composition": "Детальное пошаговое описание конструкции/алгоритма/состава с указанием отличительных признаков от прототипа",
      "practical_implementation": "Конкретные параметры, материалы, программные библиотеки, архитектуры для практической реализации"
    }},
    "expected_results": {{
      "technical_result": "Количественные показатели (скорость +X%, точность до Y, мощность -Z%) и качественные показатели",
      "result_mechanism": "Причинно-следственная связь: благодаря элементу X, взаимодействующему с Y по схеме Z, достигается результат R"
    }},
    "patentability_assessment": {{
      "novelty_analysis": {{
        "new_principle": "Абсолютно новый принцип действия",
        "new_combination": "Новая комбинация известных элементов", 
        "new_application": "Новое применение известного объекта"
      }},
      "potential_claims": [
        "Пункт 1: Способ/Устройство/Вещество, отличающийся тем, что...",
        "Пункт 2: ..."
      ],
      "preliminary_assessment": {{
        "level": "Высокий/Повышенный/Средний/Низкий",
        "justification": "Аргументация на основе анализа новизны и технических результатов"
      }}
    }}
  }},
  "invention_description": "Структурированное предварительное описание изобретения по разделам 3.1-5.3",
  "analytical_commentary": {{
    "novelty_evaluation": "Оценка по критерию новизны (N)",
    "inventive_step_evaluation": "Оценка по критерию изобретательского уровня (I)", 
    "practical_applicability_evaluation": "Оценка по критерию промышленной применимости (P)",
    "overall_patentability": "Общий уровень патентоспособности и рекомендации"
  }},
  "analysis_metadata": {{
    "model_used": "GigaChat",
    "timestamp": "{time.time()}",
    "agent_version": "2.0"
  }}
}}

ТРЕБОВАНИЯ К ФОРМАТУ:
- Верни результат ТОЛЬКО в указанной JSON структуре
- Будь максимально конкретным и технически точным
- Сохраняй научную терминологию из исходного текста
- Не добавляй информацию, которой нет в представленной работе
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                print("📨 Отправляю запрос к GigaChat для патентного анализа...")
                response = await client.post(
                    self.api_url,
                    json={
                        "model": "GigaChat",
                        "messages": messages,
                        "temperature": 0.1,
                        "max_tokens": 6000
                    },
                    headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }
                )

                if response.status_code == 200:
                    print("✅ Ответ от GigaChat получен")
                    return response.json()
                else:
                    raise Exception(
                        f"Ошибка API GigaChat: {response.status_code}")

        except httpx.TimeoutException:
            raise Exception("❌ Таймаут запроса к GigaChat (более 90 секунд)")
        except Exception as e:
            raise Exception(f"❌ Ошибка соединения с GigaChat: {e}")

# ===== СОЗДАЕМ АГЕНТА =====


class PatentAnalyzerAgent:
    """Агент для патентного анализа научных работ"""

    def __init__(self):
        # Проверяем ключи при создании агента
        if not CLIENT_ID or not CLIENT_SECRET:
            raise Exception("❌ Ключи GigaChat не настроены в .env файле")
        self.gigachat = GigaChatClient()

    async def analyze(self, research_text: str):
        """Анализирует научную работу для патентования"""
        print("🔍 Патентный анализ запущен...")

        # Проверяем что текст не пустой
        if not research_text or len(research_text.strip()) < 50:
            raise Exception(
                "Текст для анализа слишком короткий (минимум 50 символов)")

        # Отправляем в GigaChat
        response = await self.gigachat.send_message(research_text)

        # Получаем ответ
        result_text = response["choices"][0]["message"]["content"]

        # Парсим JSON
        return self._parse_response(result_text)

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Парсит ответ от GigaChat"""
        try:
            # Ищем JSON в тексте
            start = text.find('{')
            end = text.rfind('}') + 1

            if start == -1 or end == 0:
                raise Exception("❌ GigaChat не вернул JSON в ответе")

            json_str = text[start:end]
            result = json.loads(json_str)

            # Добавляем временную метку
            if "analysis_metadata" not in result:
                result["analysis_metadata"] = {}
            result["analysis_metadata"]["processing_time"] = time.time()

            return result

        except json.JSONDecodeError as e:
            raise Exception(
                f"❌ Ошибка парсинга JSON от GigaChat: {e}\nПолученный текст: {text[:500]}...")
        except Exception as e:
            raise Exception(f"❌ Ошибка обработки ответа GigaChat: {e}")


# ===== FASTAPI СЕРВЕР =====
app = FastAPI(title="Патентный анализатор научных работ")

# Для хранения задач
jobs_storage = {}

# Модель для запроса


class AnalysisRequest(BaseModel):
    text: str


@app.post("/analyze")
async def analyze_patent(request: AnalysisRequest):
    """Главный endpoint для патентного анализа"""
    job_id = str(uuid.uuid4())

    try:
        print(f"📨 Получен запрос на патентный анализ (ID: {job_id})")
        print(f"📝 Длина текста: {len(request.text)} символов")

        # Создаем агента (проверяет ключи при создании)
        analyzer = PatentAnalyzerAgent()

        # Запускаем анализ
        result = await analyzer.analyze(request.text)

        # Сохраняем результат
        jobs_storage[job_id] = {
            "status": "completed",
            "result": result,
            "timestamp": time.time(),
            "text_length": len(request.text)
        }

        print(f"✅ Патентный анализ завершен для {job_id}")

        return {
            "job_id": job_id,
            "status": "success",
            "result": result
        }

    except Exception as e:
        error_msg = f"{str(e)}"
        print(f"❌ Ошибка для {job_id}: {error_msg}")

        jobs_storage[job_id] = {
            "status": "error",
            "error": error_msg,
            "timestamp": time.time()
        }

        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """Получить результаты по ID"""
    if job_id in jobs_storage:
        return jobs_storage[job_id]
    else:
        raise HTTPException(status_code=404, detail="Задача не найдена")


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Патентный анализатор научных работ работает! ✅",
            "version": "2.0",
            "model": "GigaChat",
            "description": "Глубокий анализ научных работ для патентования",
            "endpoints": {
                "analyze": "POST /analyze - патентный анализ научной работы",
                "results": "GET /results/{job_id} - получить результаты анализа"
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    try:
        if not CLIENT_ID or not CLIENT_SECRET:
            return {
                "status": "error",
                "message": "Ключи GigaChat не настроены в .env файле"
            }

        return {
            "status": "healthy",
            "service": "Patent Analyzer",
            "model": "GigaChat",
            "version": "2.0",
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    print("🚀 Запускаю патентный анализатор научных работ...")
    print("📖 Откройте: http://127.0.0.1:8003")
    print("⚡ Версия 2.0 - Глубокий патентный анализ")
    uvicorn.run(app, host="0.0.0.0", port=8003)
