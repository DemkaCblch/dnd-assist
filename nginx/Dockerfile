FROM nginx:latest

# Nginx config
RUN rm -rf /etc/nginx/conf.d/default.conf
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Static build
COPY --from=builder /app/public /usr/share/nginx/html

# Set working directory
WORKDIR /usr/share/nginx/html

# Start Nginx server
CMD ["/bin/bash", "-c", "nginx -g \"daemon off;\""]