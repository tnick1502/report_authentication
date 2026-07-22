FROM node:16-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

COPY . /app
CMD ["npm", "start"]

