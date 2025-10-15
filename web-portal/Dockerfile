# Base stage installs prod dependencies
FROM node:22-slim AS base
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install --production

# Test stage installs dev dependencies runs the tests
FROM base AS test
RUN npm install
COPY . .
CMD ["npm", "test"]

# Development stage
FROM base
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev"]
