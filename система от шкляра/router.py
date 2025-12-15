#!/usr/bin/env python3
"""
🎯 УНИВЕРСАЛЬНЫЙ РОУТЕР ДЛЯ 5 АГЕНТОВ
Запускается: python router.py
"""

import subprocess
import re
import sys
import os
from pathlib import Path


class AgentRouter:
    """Роутер, который запускает агентов как есть"""

    def __init__(self):
        # Проверяем, что все файлы агентов существуют
        self.agents = {
            '1': {'name': '🔬 Патентный анализатор', 'file': 'agent1.py',
                  'keywords': ['патент', 'анализ', 'исследование', 'научн']},
            '2': {'name': '🎓 Универсальный помощник', 'file': 'agent2.py',
                  'keywords': ['юридическ', 'прав', 'закон', 'договор', 'общий']},
            '3': {'name': '💻 Фронтенд-эксперт', 'file': 'agent3.py',
                  'keywords': ['фронтенд', 'react', 'vue', 'angular', 'javascript', 'css']},
            '4': {'name': '📄 Генератор патентов', 'file': 'agent4.py',
                  'keywords': ['сгенерировать', 'оформить', 'патент', 'заявка', 'формула']},
            '5': {'name': '🛠️ Техподдержка', 'file': 'agent5.py',
                  'keywords': ['проблема', 'ошибка', 'не работает', 'помощь', 'статус']}
        }

    def find_agent(self, query):
        """Определяет, какой агент подходит для запросу"""
        query_lower = query.lower()

        best_match = None
        max_matches = 0

        for agent_id, agent_info in self.agents.items():
            matches = sum(1 for keyword in agent_info['keywords'] if keyword in query_lower)
            if matches > max_matches:
                max_matches = matches
                best_match = agent_id

        return best_match or '2'

    def run_agent(self, agent_id):
        """Запускает выбранного агента"""
        agent_info = self.agents.get(agent_id)
        if not agent_info:
            print(f"❌ Агент {agent_id} не найден")
            return False

        file_path = agent_info['file']

        if not Path(file_path).exists():
            print(f"❌ Файл {file_path} не найден!")
            print("Убедитесь, что в папке есть все 5 файлов агентов:")
            for a in self.agents.values():
                print(f"  • {a['file']}")
            return False

        print(f"\n🚀 Запускаю {agent_info['name']}...")
        print(f"📄 Файл: {file_path}")
        print("=" * 60)

        try:
            subprocess.run([sys.executable, file_path], check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка при запуске: {e}")
            return False
        except KeyboardInterrupt:
            print("\n⏹️  Агент остановлен пользователем")
            return True
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return False

    def show_menu(self):
        """Показывает меню выбора агента"""
        print("\n" + "=" * 60)
        print("🤖 ВЫБОР АГЕНТА")
        print("=" * 60)
        print("Выберите номер агента или введите запрос:")
        for agent_id, agent_info in self.agents.items():
            print(f"  [{agent_id}] {agent_info['name']}")
        print("\nИли введите:")
        print("  [выход] - Завершить программу")
        print("  [авто]  - Автоматический выбор по запросу")
        print("=" * 60)

    def start(self):
        """Запускает интерактивный режим"""
        print("\n" + "=" * 60)
        print("🚀 СИСТЕМА 5 АГЕНТОВ")
        print("=" * 60)
        print("Запущено! Введите запрос или номер агента.")

        while True:
            self.show_menu()

            user_input = input("\n👉 Ваш выбор: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['выход', 'exit', 'quit', 'q']:
                print("\n👋 До свидания!")
                break

            if user_input.lower() == 'авто':
                query = input("📝 Введите ваш запрос: ").strip()
                if not query:
                    continue
                agent_id = self.find_agent(query)
                print(f"🤖 Выбран: {self.agents[agent_id]['name']}")
                self.run_agent(agent_id)
                continue

            if user_input in self.agents:
                self.run_agent(user_input)
                continue

            agent_id = self.find_agent(user_input)
            print(f"🤖 Автоматически выбран: {self.agents[agent_id]['name']}")
            self.run_agent(agent_id)


def quick_start():
    """Запускает систему одним кликом"""
    print("⚡️ Быстрый старт...")

    required_files = ['agent1.py', 'agent2.py', 'agent3.py', 'agent4.py', 'agent5.py']
    missing = [f for f in required_files if not Path(f).exists()]

    if missing:
        print(f"⚠️  Отсутствуют файлы: {', '.join(missing)}")
        print("Убедитесь, что все 5 файлов в одной папке с router.py")
        return

    print("✅ Все агенты найдены!")

    router = AgentRouter()
    router.start()


if __name__ == "__main__":
    quick_start()
