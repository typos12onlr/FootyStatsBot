# 1️⃣ Use official slim Python image
FROM python:3.11-slim

# 2️⃣ Set working directory
WORKDIR /app

# 3️⃣ Install system packages (optional)
RUN apt-get update && apt-get install -y build-essential

# 4️⃣ Copy requirements and install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5️⃣ Copy your full project
COPY . .

# 6️⃣ Run the bot when container starts
CMD ["python", "main.py"]