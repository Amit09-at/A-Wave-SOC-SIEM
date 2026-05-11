COPY . .
RUN python setup_project.py

# NEW: Make the script executable and run it
RUN chmod +x start.sh
EXPOSE 5001
CMD ["./start.sh"]