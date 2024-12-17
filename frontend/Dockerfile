# Build stage
FROM node:20-alpine AS builder

WORKDIR /usr/src/app

# Set production environment
ENV NODE_ENV=production

# Copy package files
COPY package*.json ./

# Install dependencies with production flags and clean cache in same layer
RUN npm install --production --silent && \
    npm cache clean --force

# Copy source code
COPY . .

# Build production assets
RUN npm run build

# Runtime stage
FROM nginx:alpine-slim

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder
COPY --from=builder /usr/src/app/build /usr/share/nginx/html

# Install curl for healthcheck in same layer as cleanup
RUN apk add --no-cache curl && \
    rm -rf /var/cache/apk/*

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]