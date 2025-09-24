FROM node:22-slim

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (or yarn.lock)
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of your application's code
COPY . .

# Expose the Vite development server port
EXPOSE 5173

# The command to start the Vite development server
CMD ["npm", "run", "dev"]
