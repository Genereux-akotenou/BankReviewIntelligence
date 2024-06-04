# Use the official Apache HTTP Server image from the Docker Hub
FROM httpd:2.4

# Copy custom configuration file from the host to the container
COPY ./my-httpd.conf /usr/local/apache2/conf/httpd.conf

# Copy website content to the container
COPY ./public-html/ /usr/local/apache2/htdocs/

# Expose port 80
EXPOSE 80
