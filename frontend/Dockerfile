# Stage 1: Build React app
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY public/ ./public/
COPY src/ ./src/
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine

# Copy built React files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy custom Nginx config with API proxying
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
