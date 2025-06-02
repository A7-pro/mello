# Use a base image with PHP-FPM and Nginx
FROM phpdockerio/php:8.2-fpm-alpine

# Install necessary packages
RUN apk --no-cache add \
    nginx \
    curl # curl is needed by PHP for the bot function

# Copy application code and configuration
WORKDIR /app
COPY AI_GPT.php /app/AI_GPT.php
COPY nginx.conf /etc/nginx/http.d/default.conf

# Expose port 80
EXPOSE 80

# Start PHP-FPM and Nginx
CMD php-fpm && nginx -g "daemon off;"
