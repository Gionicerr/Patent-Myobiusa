import os
import json
import time
import uuid
import asyncio
from typing import Dict, Any, List
from dotenv import load_dotenv

# FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# LangChain совместимые импорты
from langchain_community.chat_models.gigachat import GigaChat
from langchain_core.messages import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

# Pydantic модели для структурированного вывода
from pydantic import BaseModel as PydanticBaseModel

load_dotenv()

# ===== PYDTOMIC МОДЕЛИ ДЛЯ СТРУКТУРИРОВАННОГО ВЫВОДА =====


class NoveltyAnalysis(PydanticBaseModel):
    new_principle: str = Field(description="Абсолютно новый принцип действия")
    new_combination: str = Field(
        description="Новая комбинация известных элементов")
    new_application: str = Field(
        description="Новое применение известного объекта")


class TechnicalImplementation(PydanticBaseModel):
    construction_algorithm_composition: str = Field(
        description="Детальное пошаговое описание конструкции/алгоритма/состава")
    practical_implementation: str = Field(
        description="Конкретные параметры, материалы, программные библиотеки")
    distinctive_features: str = Field(
        description="Отличительные признаки по сравнению с прототипом")


class ExpectedResults(PydanticBaseModel):
    technical_result: str = Field(
        description="Количественные и качественные показатели результата")
    result_mechanism: str = Field(
        description="Причинно-следственная связь достижения результата")


class PatentabilityAssessment(PydanticBaseModel):
    novelty_analysis: NoveltyAnalysis
    potential_claims: List[str] = Field(
        description="Потенциальные пункты формулы изобретения")
    preliminary_level: str = Field(
        description="Уровень патентоспособности: Высокий/Повышенный/Средний/Низкий")
    justification: str = Field(
        description="Обоснование оценки патентоспособности")


class AnalyticalCommentary(PydanticBaseModel):
    novelty_evaluation: str = Field(
        description="Оценка по критерию новизны (N)")
    inventive_step_evaluation: str = Field(
        description="Оценка по критерию изобретательского уровня (I)")
    practical_applicability_evaluation: str = Field(
        description="Оценка по критерию промышленной применимости (P)")
    overall_patentability: str = Field(
        description="Общий уровень патентоспособности и рекомендации")


class PatentAnalysisResult(PydanticBaseModel):
    fundamental_principle: str = Field(
        description="Фундаментальный физический/химический/биологический/математический принцип")
    technical_implementation: TechnicalImplementation
    expected_results: ExpectedResults
    patentability_assessment: PatentabilityAssessment
    invention_description: str = Field(
        description="Структурированное предварительное описание изобретения")
    analytical_commentary: AnalyticalCommentary

# ===== LANGCHAIN АГЕНТ =====


class LangChainPatentAnalyzer:
    """Агент для патентного анализа с использованием LangChain"""

    def __init__(self):
        self.client_id = os.getenv("GIGACHAT_CLIENT_ID")
        self.client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")

        if not self.client_id or not self.client_secret:
            raise Exception("❌ Ключи GigaChat не настроены в .env файле")

        print("🔧 Инициализация LangChain GigaChat...")

        # Инициализация GigaChat через LangChain
        self.llm = GigaChat(
            credentials=self.client_secret,
            scope="GIGACHAT_API_PERS",
            verify_ssl_certs=False,
            temperature=0.1,
            timeout=120,
            model="GigaChat"
        )

        # Парсер для структурированного вывода
        self.output_parser = PydanticOutputParser(
            pydantic_object=PatentAnalysisResult)

        # Создаем промпт-шаблон
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", """Ты — AI-агент "ПатентныйАнализатор", специалист по анализу научно-технических работ для патентования.

ТВОИ КОМПЕТЕНЦИИ:
- Глубокий анализ фундаментальных принципов
- Структурирование информации по стандартам патентной заявки
- Оценка новизны и патентоспособности по критериям N-I-P
- Формулирование пунктов формулы изобретения

ТРЕБОВАНИЯ:
- Будь максимально конкретным и технически точным
- Сохраняй научную терминологию из исходного текста
- Используй количественные показатели где это возможно
- Не добавляй информацию, которой нет в представленной работе"""),

            ("human", """ПРОАНАЛИЗИРУЙ НАУЧНО-ТЕХНИЧЕСКУЮ РАБОТУ ДЛЯ ПАТЕНТОВАНИЯ:

ТЕКСТ РАБОТЫ:
{research_text}

{format_instructions}

ПРОВЕДИ ПОЛНЫЙ АНАЛИЗ ПО СТАНДАРТНОЙ СТРУКТУРЕ:

РАЗДЕЛ 3: СУЩНОСТЬ РЕШЕНИЯ
3.1. Фундаментальный принцип
3.2. Конструкция/Алгоритм/Состав с отличительными признаками
3.3. Практическая реализация

РАЗДЕЛ 4: РЕЗУЛЬТАТ
4.1. Технический результат (количественные и качественные показатели)
4.2. Механизм достижения результата

РАЗДЕЛ 5: ПАТЕНТОСПОСОБНОСТЬ
5.1. Анализ новизны
5.2. Пункты формулы изобретения
5.3. Оценка патентоспособности

СГЕНЕРИРУЙ ФИНАЛЬНЫЙ ДОКУМЕНТ И АНАЛИТИЧЕСКИЙ КОММЕНТАРИЙ.""")
        ])

        print("✅ LangChain агент инициализирован")

    async def analyze_research_paper(self, research_text: str) -> Dict[str, Any]:
        """Анализирует научную работу с использованием LangChain"""
        print("🔍 Запуск патентного анализа через LangChain...")

        if not research_text or len(research_text.strip()) < 50:
            raise Exception(
                "Текст для анализа слишком короткий (минимум 50 символов)")

        try:
            # Получаем инструкции для форматирования
            format_instructions = self.output_parser.get_format_instructions()

            # Форматируем промпт
            messages = self.prompt_template.format_messages(
                research_text=research_text[:12000],
                format_instructions=format_instructions
            )

            print("📨 Отправляю запрос через LangChain GigaChat...")
            start_time = time.time()

            # Отправляем запрос через LangChain
            response = await self.llm.agenerate([messages])

            processing_time = time.time() - start_time
            print(f"✅ Ответ получен за {processing_time:.2f} сек")

            # Извлекаем текст ответа
            response_text = response.generations[0][0].text

            # Парсим структурированный ответ
            parsed_result = self.output_parser.parse(response_text)

            # Конвертируем в dict и добавляем метаданные
            result_dict = parsed_result.dict()
            result_dict["analysis_metadata"] = {
                "model_used": "GigaChat",
                "framework": "LangChain",
                "processing_time_seconds": processing_time,
                "timestamp": time.time(),
                "text_length_analyzed": len(research_text),
                "agent_version": "1.0-LangChain"
            }

            return result_dict

        except Exception as e:
            print(f"❌ Ошибка в LangChain анализе: {e}")
            raise Exception(f"Ошибка анализа через LangChain: {str(e)}")


# ===== FASTAPI СЕРВЕР =====
app = FastAPI(
    title="Патентный анализатор с LangChain",
    description="AI-агент для анализа научных работ с использованием LangChain и GigaChat",
    version="1.0"
)

# Глобальный экземпляр агента
patent_analyzer = None

# Инициализация агента при запуске


@app.on_event("startup")
async def startup_event():
    global patent_analyzer
    try:
        patent_analyzer = LangChainPatentAnalyzer()
        print("🎉 LangChain агент успешно инициализирован!")
        print("📊 Конфигурация:")
        print(f"   - Модель: GigaChat")
        print(f"   - Фреймворк: LangChain")
        print(f"   - Парсер: PydanticOutputParser")
        print(f"   - Промпты: ChatPromptTemplate")
    except Exception as e:
        print(f"❌ Ошибка инициализации агента: {e}")
        patent_analyzer = None

# Модели запросов/ответов


class AnalysisRequest(BaseModel):
    text: str = Field(..., min_length=50,
                      description="Текст научной работы для анализа")


class AnalysisResponse(BaseModel):
    job_id: str
    status: str
    result: Dict[str, Any] = None
    error: str = None
    processing_time: float = None


# Хранилище задач
jobs_storage = {}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_patent(request: AnalysisRequest):
    """Эндпоинт для патентного анализа научной работы"""
    if patent_analyzer is None:
        raise HTTPException(status_code=500, detail="Агент не инициализирован")

    job_id = str(uuid.uuid4())
    start_time = time.time()

    try:
        print(f"📨 Получен запрос на анализ (ID: {job_id})")
        print(f"📝 Длина текста: {len(request.text)} символов")

        # Запускаем анализ через LangChain агента
        result = await patent_analyzer.analyze_research_paper(request.text)

        processing_time = time.time() - start_time

        # Сохраняем результат
        jobs_storage[job_id] = {
            "status": "completed",
            "result": result,
            "timestamp": time.time(),
            "processing_time": processing_time
        }

        print(f"✅ Патентный анализ завершен для {job_id}")

        return AnalysisResponse(
            job_id=job_id,
            status="success",
            result=result,
            processing_time=processing_time
        )

    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"{str(e)}"

        print(f"❌ Ошибка для {job_id}: {error_msg}")

        jobs_storage[job_id] = {
            "status": "error",
            "error": error_msg,
            "timestamp": time.time(),
            "processing_time": processing_time
        }

        return AnalysisResponse(
            job_id=job_id,
            status="error",
            error=error_msg,
            processing_time=processing_time
        )


@app.get("/results/{job_id}")
async def get_results(job_id: str):
    """Получить результаты анализа по ID задачи"""
    if job_id not in jobs_storage:
        raise HTTPException(status_code=404, detail="Задача не найдена")

    return jobs_storage[job_id]


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Патентный анализатор с LangChain работает! ✅",
            "version": "1.0",
            "framework": "FastAPI + LangChain + GigaChat",
            "status": "active",
            "endpoints": {
                "analyze": "POST /analyze - патентный анализ научной работы",
                "results": "GET /results/{job_id} - получить результаты анализа",
                "health": "GET /health - проверка состояния системы"
            }
        },
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@app.get("/health")
async def health_check():
    """Проверка здоровья системы"""
    health_status = {
        "status": "healthy" if patent_analyzer else "error",
        "service": "Patent Analyzer with LangChain",
        "model": "GigaChat",
        "framework": "LangChain",
        "agent_initialized": patent_analyzer is not None,
        "timestamp": time.time()
    }

    if patent_analyzer is None:
        health_status["message"] = "Агент не инициализирован"
        health_status["status"] = "error"

    return health_status


@app.get("/config")
async def get_config():
    """Информация о конфигурации системы"""
    return {
        "langchain_version": "0.0.353",
        "gigachat_integration": "langchain-community",
        "output_parser": "PydanticOutputParser",
        "prompt_templates": "ChatPromptTemplate",
        "features": [
            "Структурированный вывод с Pydantic",
            "Асинхронные запросы",
            "Валидация входных данных",
            "Обработка ошибок",
            "Мониторинг производительности"
        ]
    }

# Запуск сервера
if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 ПАТЕНТНЫЙ АНАЛИЗАТОР С LANGCHAIN")
    print("=" * 60)
    print("🔧 Конфигурация системы:")
    print("   - Фреймворк: LangChain 0.0.353")
    print("   - Модель: GigaChat")
    print("   - API: FastAPI")
    print("   - Парсер: PydanticOutputParser")
    print("📖 Документация: http://localhost:8005/docs")
    print("🌐 Health check: http://localhost:8005/health")
    print("=" * 60)

    uvicorn.run(app, host="0.0.0.0", port=8005, reload=True)
