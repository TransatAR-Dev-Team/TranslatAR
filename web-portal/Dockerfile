FROM node:22-slim AS base

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install

# Test stage
FROM base AS test

COPY . .

CMD ["npm", "test", "--", "--run"]

# Dev stage
FROM base

COPY . .

# Expose the Vite development server port
EXPOSE 5173

# The command to start the Vite development server
CMD ["npm", "run", "dev"]
