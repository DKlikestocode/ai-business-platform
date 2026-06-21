FROM node:22-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

RUN chmod +x /app/scripts/docker-dev.sh

ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.dev.sh"]
CMD ["/app/scripts/docker-dev.sh"]
