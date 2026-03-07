# Stage 1: Build React app
FROM node:20-alpine AS build

ARG REACT_APP_AGENT_URL=https://nasiko-production.up.railway.app/
ENV REACT_APP_AGENT_URL=$REACT_APP_AGENT_URL

WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html

# Nginx config to support React Router (SPA)
RUN echo 'server { \
  listen 80; \
  location / { \
    root /usr/share/nginx/html; \
    try_files $uri /index.html; \
  } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80
