FROM nginx:latest

# Copy NGINX config
COPY default.conf /etc/nginx/conf.d/default.conf

# Copy static files (HTML, JS, CSS)
COPY static/ /usr/share/nginx/html/