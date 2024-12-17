# Build stage
FROM nginx:1.27-alpine-slim AS builder

# Install build dependencies and compile module in single layer
RUN apk add --no-cache \
    curl \
    gcc \
    libc-dev \
    make \
    openssl-dev \
    pcre-dev \
    zlib-dev \
    linux-headers \
    wget \
    git \
    && cd /tmp \
    && wget http://nginx.org/download/nginx-${NGINX_VERSION}.tar.gz \
    && tar zxf nginx-${NGINX_VERSION}.tar.gz \
    && git clone https://github.com/openresty/headers-more-nginx-module.git \
    && cd nginx-${NGINX_VERSION} \
    && ./configure \
        --with-compat \
        --add-dynamic-module=../headers-more-nginx-module \
    && make modules \
    && mkdir -p /modules \
    && cp objs/ngx_http_headers_more_filter_module.so /modules/

# Runtime stage
FROM nginx:1.27-alpine-slim

# Copy only the compiled module
COPY --from=builder /modules/ngx_http_headers_more_filter_module.so /etc/nginx/modules/

# Copy configuration
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./default.conf /etc/nginx/conf.d/default.conf

# Install only runtime dependencies
RUN apk add --no-cache curl

HEALTHCHECK --interval=1m30s --timeout=10s --start-period=40s --retries=3 CMD curl -so /dev/null http://localhost/ || exit 1