# Use Alpine Linux as base
FROM alpine:3.18

# Set maintainer label
LABEL maintainer="Jeron (JR)"
LABEL description="Frontend container with lighttpd for Milestone 2"

# Install lighttpd web server
RUN apk add --no-cache lighttpd

# Create web directory
RUN mkdir -p /var/www/localhost/htdocs

# Copy HTML file to web directory
COPY index.html /var/www/localhost/htdocs/

# Copy lighttpd configuration
COPY lighttpd.conf /etc/lighttpd/lighttpd.conf

# Create log directory
RUN mkdir -p /var/log/lighttpd && \
    chown -R lighttpd:lighttpd /var/log/lighttpd /var/www/localhost

# Expose port 80
EXPOSE 80

# Start lighttpd in foreground
CMD ["lighttpd", "-D", "-f", "/etc/lighttpd/lighttpd.conf"]