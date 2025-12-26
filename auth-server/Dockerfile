# Use Node.js
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (Force ignore version conflicts)
RUN npm install --legacy-peer-deps

# Copy the rest of the code
COPY . .

# Open the port Hugging Face expects (7860)
EXPOSE 7860

# Start the server (forcing port 7860)
ENV PORT=7860
CMD ["npm", "run", "dev"]