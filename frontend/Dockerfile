# 1. Використовуємо Node.js 20 як базовий образ
FROM node:20-alpine

# 2. Debug: Перевіряємо версії Node.js та npm
RUN echo "Using Node.js version:" && node -v
RUN echo "Using npm version:" && npm -v

# 3. Встановлюємо робочу директорію
WORKDIR /app
RUN echo "Working directory set to /app"

# 4. Копіюємо package.json і package-lock.json для кешування встановлення залежностей
COPY package*.json ./
RUN echo "Copied package.json and package-lock.json"

# 5. Встановлюємо залежності
RUN echo "Installing dependencies..."
RUN npm install --legacy-peer-deps && echo "Dependencies installed successfully."

# 6. Debug: Список встановлених залежностей
RUN echo "Installed dependencies:" && ls -l node_modules

# 7. Копіюємо весь код програми
COPY . .
RUN echo "Application files copied. Current directory contents:" && ls -l

# 8. Відкриваємо порт для Vite-сервера (порт 5173)
EXPOSE 5173
RUN echo "Port 5173 exposed for Vite development server."

# 9. Запускаємо Vite у режимі розробки
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
