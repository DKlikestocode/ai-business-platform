FROM node:22-alpine

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json* ./
RUN npm install

COPY . .

EXPOSE 3000

ENTRYPOINT ["/bin/sh", "/app/docker-entrypoint.dev.sh"]
CMD ["npm", "run", "dev"]
